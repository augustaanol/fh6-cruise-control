import socket
import struct
import math
import asyncio
import os
import yaml
import vgamepad as vg
from pynput import keyboard
import XInput

# ==================================================
# --- DEFAULT CONFIGURATION GENERATOR ---
# ==================================================
DEFAULT_CONFIG = """# ==================================================
# --- NETWORK CONFIGURATION ---
# ==================================================
network:
  listen_ip: "127.0.0.1"
  listen_port: 8000
  
  # Forward telemetry to another device/software (e.g., SimHub, Telemetry Overlay, etc.)
  forward_enabled: false
  forward_ip: "127.0.0.1"
  forward_port: 8001

# ==================================================
# --- CRUISE CONTROL CONFIGURATION ---
# ==================================================
cruise_control:
  startup_target_speed_kmh: 60.0
  speed_step_kmh: 5.0      # Speed step in km/h
  kp: 0.4                  # A proportional gain for the cruise control (higher = more aggressive, lower = smoother)

# ==================================================
# --- KEYBOARD CONTROLS ---
# ==================================================
# Use single characters (e.g., 'z', 'x') or special keys (e.g., 'page_up', 'page_down', 'space')
keyboard:
  toggle_resume: 'home'
  toggle_current: 'end'
  speed_up: 'page_up'
  speed_down: 'page_down'

# ==================================================
# --- GAMEPAD CONTROLS (XInput) ---
# ==================================================
# Available buttons: 'DPAD_UP', 'DPAD_DOWN', 'DPAD_LEFT', 'DPAD_RIGHT', 'START', 'BACK',
# 'LEFT_THUMB', 'RIGHT_THUMB', 'LEFT_SHOULDER', 'RIGHT_SHOULDER', 'A', 'B', 'X', 'Y'
# Leave empty ('') to disable
gamepad:
  toggle_resume: ''
  toggle_current: ''
  speed_up: ''
  speed_down: ''
"""

def load_config(filename="config.yaml"):
    """Loads config from YAML file. If the file does not exist, creates a default one."""
    if not os.path.exists(filename):
        print(f"⚠️ Config file '{filename}' not found. Creating default one...")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(DEFAULT_CONFIG)
            
    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Config loading
config = load_config()

# --- NETWORK ---
LISTEN_IP = config['network'].get('listen_ip', '127.0.0.1')
LISTEN_PORT = config['network'].get('listen_port', 8000)
FORWARD_ENABLED = config['network'].get('forward_enabled', False)
FORWARD_IP = config['network'].get('forward_ip', '127.0.0.1')
FORWARD_PORT = config['network'].get('forward_port', 8001)

# --- CRUISE CONTROL ---
STARTUP_TARGET_SPEED_KMH = float(config['cruise_control'].get('startup_target_speed_kmh', 60.0))
SPEED_STEP_KMH = float(config['cruise_control'].get('speed_step_kmh', 5.0))
KP = float(config['cruise_control'].get('kp', 0.3))

def parse_kb_key(key_str):
    """Converts string keys like 'page_up' to keyboard.Key objects, and letters to strings."""
    if not key_str: return None
    key_str = str(key_str)
    if hasattr(keyboard.Key, key_str):
        return getattr(keyboard.Key, key_str)
    return key_str

# --- KEYBOARD ---
KB_TOGGLE_RESUME = parse_kb_key(config['keyboard'].get('toggle_resume'))
KB_TOGGLE_CURRENT = parse_kb_key(config['keyboard'].get('toggle_current'))
KB_SPEED_UP = parse_kb_key(config['keyboard'].get('speed_up'))
KB_SPEED_DOWN = parse_kb_key(config['keyboard'].get('speed_down'))

# --- GAMEPAD ---
PAD_TOGGLE_RESUME = config['gamepad'].get('toggle_resume')
PAD_TOGGLE_CURRENT = config['gamepad'].get('toggle_current')
PAD_SPEED_UP = config['gamepad'].get('speed_up')
PAD_SPEED_DOWN = config['gamepad'].get('speed_down')

# ==================================================
# --- STATE VARIABLES (Do not edit) ---
# ==================================================
target_speed_kmh = STARTUP_TARGET_SPEED_KMH
cruise_enabled = False
has_received_any_data = False
gamepad = vg.VX360Gamepad()
previous_pad_buttons = {}

# Action flags
action_toggle_resume = False
action_toggle_current = False
action_speed_up = False
action_speed_down = False


def find_active_controller_index():
    for i in range(4):
        try:
            if XInput.get_connected()[i]:
                return i
        except Exception:
            pass
    return None

def parse_speed(data: bytes) -> float | None:
    if len(data) < 311:
        return None
    try:
        vx = struct.unpack_from('<f', data, 32)[0]
        vy = struct.unpack_from('<f', data, 36)[0]
        vz = struct.unpack_from('<f', data, 40)[0]
        return math.sqrt(vx**2 + vy**2 + vz**2) * 3.6
    except Exception:
        return None

def is_key_match(key, config_key):
    if not config_key: return False
    if hasattr(key, 'char') and key.char is not None:
        return key.char.lower() == config_key.lower() if isinstance(config_key, str) else False
    else:
        return key == config_key

def on_press(key):
    global action_toggle_resume, action_toggle_current, action_speed_up, action_speed_down
    
    if is_key_match(key, KB_TOGGLE_RESUME):
        action_toggle_resume = True
    elif is_key_match(key, KB_TOGGLE_CURRENT):
        action_toggle_current = True
    elif is_key_match(key, KB_SPEED_UP):
        action_speed_up = True
    elif is_key_match(key, KB_SPEED_DOWN):
        action_speed_down = True

def check_pad_button(btn_name, current_state, previous_state):
    if not btn_name: return False
    return current_state.get(btn_name, False) and not previous_state.get(btn_name, False)

def get_key_display(key):
    """Formatuje nazwę klawisza do czytelnego wyświetlania w konsoli."""
    if not key: return "NONE"
    if hasattr(key, 'name'): return key.name.upper()
    return str(key).upper()

async def cruise_control_loop():
    global cruise_enabled, target_speed_kmh, has_received_any_data, previous_pad_buttons
    global action_toggle_resume, action_toggle_current, action_speed_up, action_speed_down
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.ioctl(socket.SIO_UDP_CONNRESET, False)
    except:
        pass
    sock.bind((LISTEN_IP, LISTEN_PORT))
    sock.setblocking(False)
    
    forward_sock = None
    if FORWARD_ENABLED:
        forward_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("==================================================")
    print("Forza Horizon Cruise Control")
    print("==================================================")
    print(f"[{get_key_display(KB_TOGGLE_RESUME)} / {PAD_TOGGLE_RESUME or 'NONE'}] - Enable (Last speed) / Disable")
    print(f"[{get_key_display(KB_TOGGLE_CURRENT)} / {PAD_TOGGLE_CURRENT or 'NONE'}] - Enable (Current speed) / Disable")
    print(f"[CHANGE SPEED (±{SPEED_STEP_KMH} km/h)] - {get_key_display(KB_SPEED_UP)}/{get_key_display(KB_SPEED_DOWN)} or {PAD_SPEED_UP or 'NONE'}/{PAD_SPEED_DOWN or 'NONE'}\n")

    try:
        while True:
            latest_data = None

            while True:
                try:
                    data, _ = sock.recvfrom(1024)
                    if not has_received_any_data:
                        print(f"[Successfully connected to Forza telemetry]")
                        has_received_any_data = True
                    
                    if FORWARD_ENABLED and forward_sock:
                        try:
                            forward_sock.sendto(data, (FORWARD_IP, FORWARD_PORT))
                        except Exception:
                            pass
                            
                    latest_data = data
                except BlockingIOError:
                    break
                except Exception:
                    break

            current_speed = parse_speed(latest_data) if latest_data else None

            controller_idx = find_active_controller_index()
            if controller_idx is not None:
                try:
                    state = XInput.get_state(controller_idx)
                    
                    # --- GAMEPAD BUTTONS HANDLING ---
                    current_pad_buttons = XInput.get_button_values(state)
                    
                    if check_pad_button(PAD_TOGGLE_RESUME, current_pad_buttons, previous_pad_buttons):
                        action_toggle_resume = True
                    if check_pad_button(PAD_TOGGLE_CURRENT, current_pad_buttons, previous_pad_buttons):
                        action_toggle_current = True
                    if check_pad_button(PAD_SPEED_UP, current_pad_buttons, previous_pad_buttons):
                        action_speed_up = True
                    if check_pad_button(PAD_SPEED_DOWN, current_pad_buttons, previous_pad_buttons):
                        action_speed_down = True
                        
                    previous_pad_buttons = current_pad_buttons

                    # --- CLONING THUMBSTICKS ---
                    sticks = XInput.get_thumb_values(state)
                    gamepad.left_joystick_float(sticks[0][0], sticks[0][1])
                    gamepad.right_joystick_float(sticks[1][0], sticks[1][1])

                    # --- READING PLAYER TRIGGERS (PEDALS) ---
                    triggers = XInput.get_trigger_values(state)
                    player_brake = triggers[0]
                    player_gas = triggers[1]

                except Exception:
                    player_brake = 0.0
                    player_gas = 0.0
            else:
                player_brake = 0.0
                player_gas = 0.0


            # ==================================================
            # --- PROCESSING ACTIONS (Flags) ---
            # ==================================================
            
            # Toggling cruise control
            if action_toggle_resume or action_toggle_current:
                if cruise_enabled:
                    cruise_enabled = False
                    print(f"\n[CRUISE CONTROL DISABLED] (Saved: {target_speed_kmh:.1f} km/h)")
                else:
                    if action_toggle_current and current_speed is not None:
                        target_speed_kmh = current_speed
                    
                    cruise_enabled = True
                    print(f"\n[CRUISE CONTROL ENABLED] Target: {target_speed_kmh:.1f} km/h")
                
                action_toggle_resume = False
                action_toggle_current = False

            # Changing speed (Dynamic Rounding to nearest SPEED_STEP_KMH)
            if action_speed_up:
                target_speed_kmh = math.floor(target_speed_kmh / SPEED_STEP_KMH) * SPEED_STEP_KMH + SPEED_STEP_KMH
                print(f"\n⏩ Target increased: {target_speed_kmh:.1f} km/h")
                action_speed_up = False
                
            if action_speed_down:
                target_speed_kmh = math.ceil(target_speed_kmh / SPEED_STEP_KMH) * SPEED_STEP_KMH - SPEED_STEP_KMH
                if target_speed_kmh < 0.0: 
                    target_speed_kmh = 0.0
                print(f"\n⏪ Target decreased: {target_speed_kmh:.1f} km/h")
                action_speed_down = False

            # ==================================================
            # --- CONTROL LOGIC ---
            # ==================================================
            TRIGGER_THRESHOLD = 0.05  # 5% martwej strefy (zapobiega przypadkowym dotknięciom)

            if cruise_enabled and current_speed is not None:
                # Jeśli gracz fizycznie wciska gaz lub hamulec, tymczasowo ignorujemy tempomat
                if player_gas > TRIGGER_THRESHOLD or player_brake > TRIGGER_THRESHOLD:
                    final_gas = player_gas
                    final_brake = player_brake
                else:
                    # Logika tempomatu uaktywnia się tylko, gdy triggery są puszczone
                    speed_error = target_speed_kmh - current_speed
                    
                    if speed_error > 0:
                        final_gas = min(1.0, speed_error * KP)
                        final_brake = 0.0
                    else:
                        final_gas = 0.0
                        final_brake = min(1.0, abs(speed_error) * KP)
            else:
                final_gas = player_gas
                final_brake = player_brake

            # Sending data to virtual gamepad
            gamepad.right_trigger_float(final_gas)
            gamepad.left_trigger_float(final_brake)
            gamepad.update()
            
            await asyncio.sleep(1 / 60)

    except asyncio.CancelledError:
        pass
    finally:
        gamepad.reset()
        gamepad.update()
        sock.close()
        if forward_sock:
            forward_sock.close()

if __name__ == "__main__":
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        asyncio.run(cruise_control_loop())
    except KeyboardInterrupt:
        pass