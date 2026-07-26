from dataclasses import dataclass

@dataclass
class CruiseState:
    target_speed_kmh: float
    current_speed: float = 0.0
    cruise_enabled: bool = False
    has_received_any_data: bool = False
    
    # Flagi akcji (mogą być zmieniane przez klawiaturę, pada lub API)
    action_toggle_resume: bool = False
    action_toggle_current: bool = False
    action_speed_up: bool = False
    action_speed_down: bool = False