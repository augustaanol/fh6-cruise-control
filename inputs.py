from pynput import keyboard
import XInput

class InputHandler:
    def __init__(self, config, state):
        self.config = config
        self.state = state
        self.previous_pad_buttons = {}
        
        # Start nasłuchiwania klawiatury
        self.listener = keyboard.Listener(on_press=self.on_kb_press)
        self.listener.start()

    def is_key_match(self, key, config_key):
        if not config_key: return False
        if hasattr(key, 'char') and key.char is not None:
            return key.char.lower() == config_key.lower() if isinstance(config_key, str) else False
        return key == config_key

    def on_kb_press(self, key):
        if self.is_key_match(key, self.config['kb_toggle_resume']):
            self.state.action_toggle_resume = True
        elif self.is_key_match(key, self.config['kb_toggle_current']):
            self.state.action_toggle_current = True
        elif self.is_key_match(key, self.config['kb_speed_up']):
            self.state.action_speed_up = True
        elif self.is_key_match(key, self.config['kb_speed_down']):
            self.state.action_speed_down = True

    def check_pad_button(self, btn_name, current_state):
        if not btn_name: return False
        return current_state.get(btn_name, False) and not self.previous_pad_buttons.get(btn_name, False)

    def find_active_controller_index(self):
        for i in range(4):
            try:
                if XInput.get_connected()[i]:
                    return i
            except Exception:
                pass
        return None

    def read_gamepad(self):
        player_gas, player_brake = 0.0, 0.0
        sticks = ((0.0, 0.0), (0.0, 0.0))
        
        idx = self.find_active_controller_index()
        if idx is not None:
            try:
                x_state = XInput.get_state(idx)
                current_pad_buttons = XInput.get_button_values(x_state)
                
                if self.check_pad_button(self.config['pad_toggle_resume'], current_pad_buttons):
                    self.state.action_toggle_resume = True
                if self.check_pad_button(self.config['pad_toggle_current'], current_pad_buttons):
                    self.state.action_toggle_current = True
                if self.check_pad_button(self.config['pad_speed_up'], current_pad_buttons):
                    self.state.action_speed_up = True
                if self.check_pad_button(self.config['pad_speed_down'], current_pad_buttons):
                    self.state.action_speed_down = True
                    
                self.previous_pad_buttons = current_pad_buttons
                sticks = XInput.get_thumb_values(x_state)
                
                triggers = XInput.get_trigger_values(x_state)
                player_brake = triggers[0]
                player_gas = triggers[1]
            except Exception:
                pass

        return player_gas, player_brake, sticks