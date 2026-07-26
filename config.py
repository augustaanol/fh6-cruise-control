import os
import yaml
from pynput import keyboard

DEFAULT_CONFIG = """# ==================================================
# --- NETWORK CONFIGURATION ---
# ==================================================
network:
  listen_ip: "127.0.0.1"
  listen_port: 8000
  forward_enabled: false
  forward_ip: "0.0.0.0"
  forward_port: 8000

# ==================================================
# --- CRUISE CONTROL CONFIGURATION ---
# ==================================================
cruise_control:
  startup_target_speed_kmh: 60.0
  speed_step_kmh: 5.0
  kp: 0.3

# ==================================================
# --- KEYBOARD CONTROLS ---
# ==================================================
keyboard:
  toggle_resume: 'z'
  toggle_current: 'x'
  speed_up: 'page_up'
  speed_down: 'page_down'

# ==================================================
# --- GAMEPAD CONTROLS (XInput) ---
# ==================================================
gamepad:
  toggle_resume: ''
  toggle_current: ''
  speed_up: ''
  speed_down: ''
"""

def parse_kb_key(key_str):
    if not key_str: return None
    key_str = str(key_str)
    if hasattr(keyboard.Key, key_str):
        return getattr(keyboard.Key, key_str)
    return key_str

def load_config(filename="config.yaml"):
    if not os.path.exists(filename):
        print(f"⚠️ Config file '{filename}' not found. Creating default one...")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(DEFAULT_CONFIG)
            
    with open(filename, 'r', encoding='utf-8') as f:
        raw_config = yaml.safe_load(f)

    # Przygotowujemy ładny słownik dla aplikacji
    return {
        'net_listen_ip': raw_config['network'].get('listen_ip', '127.0.0.1'),
        'net_listen_port': raw_config['network'].get('listen_port', 8000),
        'net_forward_enabled': raw_config['network'].get('forward_enabled', False),
        'net_forward_ip': raw_config['network'].get('forward_ip', '127.0.0.1'),
        'net_forward_port': raw_config['network'].get('forward_port', 8001),
        
        'startup_speed': float(raw_config['cruise_control'].get('startup_target_speed_kmh', 60.0)),
        'speed_step': float(raw_config['cruise_control'].get('speed_step_kmh', 5.0)),
        'kp': float(raw_config['cruise_control'].get('kp', 0.3)),
        
        'kb_toggle_resume': parse_kb_key(raw_config['keyboard'].get('toggle_resume')),
        'kb_toggle_current': parse_kb_key(raw_config['keyboard'].get('toggle_current')),
        'kb_speed_up': parse_kb_key(raw_config['keyboard'].get('speed_up')),
        'kb_speed_down': parse_kb_key(raw_config['keyboard'].get('speed_down')),
        
        'pad_toggle_resume': raw_config['gamepad'].get('toggle_resume'),
        'pad_toggle_current': raw_config['gamepad'].get('toggle_current'),
        'pad_speed_up': raw_config['gamepad'].get('speed_up'),
        'pad_speed_down': raw_config['gamepad'].get('speed_down')
    }