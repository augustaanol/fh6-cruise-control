import socket
import struct
import math
import asyncio
import vgamepad as vg
from pynput import keyboard
import XInput

# ==================================================
# --- NETWORK CONFIGURATION ---
# ==================================================
LISTEN_IP = "127.0.0.1"  
LISTEN_PORT = 8000       

FORWARD_IP = "192.168.0.30"  
FORWARD_PORT = 8000          

# ==================================================
# --- CRUISE CONTROL CONFIGURATION ---
# ==================================================
STARTUP_TARGET_SPEED_KMH = 60.0  # Speed at script startup
KP = 0.3                         # Aggressiveness of acceleration/braking

# --- KEYBOARD ---
KB_TOGGLE_RESUME = 'z'           # Enables at the LAST SAVED speed (or disables)
KB_TOGGLE_CURRENT = 'x'          # Enables at the CURRENT speed (or disables)
KB_SPEED_UP = keyboard.Key.page_up
KB_SPEED_DOWN = keyboard.Key.page_down

# --- GAMEPAD (XInput) ---
# Available buttons: 'DPAD_UP', 'DPAD_DOWN', 'DPAD_LEFT', 'DPAD_RIGHT', 'START', 'BACK', 'LEFT_THUMB', 'RIGHT_THUMB', 'LEFT_SHOULDER', 'RIGHT_SHOULDER', 'A', 'B', 'X', 'Y'

PAD_TOGGLE_RESUME = ''
PAD_TOGGLE_CURRENT = ''
PAD_SPEED_UP = ''
PAD_SPEED_DOWN = ''

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
    """Automatically detects which index the active gamepad is on (0-3)."""
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
    forward_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("==================================================")
    print("🚗 ADVANCED CRUISE CONTROL (Smart Rounding) 🎮")
    print("==================================================")
    print(f"[{KB_TOGGLE_RESUME.upper()} / {PAD_TOGGLE_RESUME}] - Enable (Last speed) / Disable")
    print(f"[{KB_TOGGLE_CURRENT.upper()} / {PAD_TOGGLE_CURRENT}] - Enable (Current speed) / Disable")
    print(f"[CHANGE SPEED] - {KB_SPEED_UP.name}/{KB_SPEED_DOWN.name} or {PAD_SPEED_UP}/{PAD_SPEED_DOWN}\n")

    try:
        while True:
            latest_data = None

            while True:
                try:
                    data, _ = sock.recvfrom(1024)
                    if not has_received_any_data:
                        print(f"✅ [Successfully connected to Forza telemetry]")
                        has_received_any_data = True
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
                    print(f"\n🔴 [CRUISE CONTROL DISABLED] (Saved: {target_speed_kmh:.1f} km/h)")
                else:
                    if action_toggle_current and current_speed is not None:
                        target_speed_kmh = current_speed
                    
                    cruise_enabled = True
                    print(f"\n🟢 [CRUISE CONTROL ENABLED] Target: {target_speed_kmh:.1f} km/h")
                
                action_toggle_resume = False
                action_toggle_current = False

            # Changing speed (Rounding to nearest 5)
            if action_speed_up:
                # If 63, rounds down to 60 and adds 5 = 65. If 60, rounds down to 60 and adds 5 = 65.
                target_speed_kmh = math.floor(target_speed_kmh / 5.0) * 5.0 + 5.0
                print(f"\n⏩ Target increased: {target_speed_kmh:.1f} km/h")
                action_speed_up = False
                
            if action_speed_down:
                # If 63, rounds up to 65 and subtracts 5 = 60. If 60, rounds up to 60 and subtracts 5 = 55.
                target_speed_kmh = math.ceil(target_speed_kmh / 5.0) * 5.0 - 5.0
                if target_speed_kmh < 0.0: 
                    target_speed_kmh = 0.0
                print(f"\n⏪ Target decreased: {target_speed_kmh:.1f} km/h")
                action_speed_down = False

            # ==================================================
            # --- CONTROL LOGIC ---
            # ==================================================
            if cruise_enabled and current_speed is not None:
                speed_error = target_speed_kmh - current_speed
                
                if speed_error > 0:
                    cruise_gas = min(1.0, speed_error * KP)
                    cruise_brake = 0.0
                else:
                    cruise_gas = 0.0
                    cruise_brake = min(1.0, abs(speed_error) * KP)

                # Physical trigger overrides cruise control
                final_gas = max(cruise_gas, player_gas)
                final_brake = max(cruise_brake, player_brake)
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
        forward_sock.close()

if __name__ == "__main__":
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        asyncio.run(cruise_control_loop())
    except KeyboardInterrupt:
        pass