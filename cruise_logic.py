import math

class CruiseLogic:
    def __init__(self, config, state):
        self.config = config
        self.state = state
        self.TRIGGER_THRESHOLD = 0.05

    def process_actions(self):
        # Włączanie / Wyłączanie
        if self.state.action_toggle_resume or self.state.action_toggle_current:
            if self.state.cruise_enabled:
                self.state.cruise_enabled = False
                print(f"\n[CRUISE CONTROL DISABLED] (Saved: {self.state.target_speed_kmh:.1f} km/h)")
            else:
                if self.state.action_toggle_current and self.state.current_speed > 0:
                    self.state.target_speed_kmh = self.state.current_speed
                self.state.cruise_enabled = True
                print(f"\n[CRUISE CONTROL ENABLED] Target: {self.state.target_speed_kmh:.1f} km/h")
            
            self.state.action_toggle_resume = False
            self.state.action_toggle_current = False

        # Zmiana prędkości
        step = self.config['speed_step']
        if self.state.action_speed_up:
            self.state.target_speed_kmh = math.floor(self.state.target_speed_kmh / step) * step + step
            print(f"\n⏩ Target increased: {self.state.target_speed_kmh:.1f} km/h")
            self.state.action_speed_up = False
            
        if self.state.action_speed_down:
            self.state.target_speed_kmh = math.ceil(self.state.target_speed_kmh / step) * step - step
            if self.state.target_speed_kmh < 0.0: 
                self.state.target_speed_kmh = 0.0
            print(f"\n⏪ Target decreased: {self.state.target_speed_kmh:.1f} km/h")
            self.state.action_speed_down = False

    def calculate_pedals(self, player_gas, player_brake):
        if self.state.cruise_enabled and self.state.current_speed > 0:
            # Fizyczny override gracza
            if player_gas > self.TRIGGER_THRESHOLD or player_brake > self.TRIGGER_THRESHOLD:
                return player_gas, player_brake

            # Logika tempomatu
            speed_error = self.state.target_speed_kmh - self.state.current_speed
            kp = self.config['kp']
            
            if speed_error > 0:
                final_gas = min(1.0, speed_error * kp)
                final_brake = 0.0
            else:
                final_gas = 0.0
                final_brake = min(1.0, abs(speed_error) * kp)
            
            return final_gas, final_brake
            
        return player_gas, player_brake