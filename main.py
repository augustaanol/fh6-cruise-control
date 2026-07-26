import asyncio
from config import load_config
from state import CruiseState
from telemetry import TelemetryReceiver
from inputs import InputHandler
from virtual_pad import VirtualPad
from cruise_logic import CruiseLogic

def get_key_display(key):
    if not key: return "NONE"
    if hasattr(key, 'name'): return key.name.upper()
    return str(key).upper()

async def main_loop():
    # 1. Inicjalizacja modułów
    config = load_config()
    state = CruiseState(target_speed_kmh=config['startup_speed'])
    
    telemetry = TelemetryReceiver(config)
    input_handler = InputHandler(config, state)
    vpad = VirtualPad()
    logic = CruiseLogic(config, state)

    print("==================================================")
    print("Forza Horizon Cruise Control")
    print("==================================================")
    print(f"[{get_key_display(config['kb_toggle_resume'])} / {config['pad_toggle_resume'] or 'NONE'}] - Enable (Last speed) / Disable")
    print(f"[{get_key_display(config['kb_toggle_current'])} / {config['pad_toggle_current'] or 'NONE'}] - Enable (Current speed) / Disable")
    print(f"[CHANGE SPEED (±{config['speed_step']} km/h)] - {get_key_display(config['kb_speed_up'])}/{get_key_display(config['kb_speed_down'])} or {config['pad_speed_up'] or 'NONE'}/{config['pad_speed_down'] or 'NONE'}\n")

    try:
        while True:
            # 2. Odczyt telemetrii
            data = telemetry.receive()
            if data:
                state.current_speed = telemetry.parse_speed(data) or 0.0
                if not state.has_received_any_data:
                    print(f"[Successfully connected to Forza telemetry]")
                    state.has_received_any_data = True

            # 3. Odczyt fizycznych pedałów i gałek z pada
            player_gas, player_brake, sticks = input_handler.read_gamepad()
            vpad.update_sticks(sticks)

            # 4. Przetwarzanie logiki i akcji (np. zmiana celu)
            logic.process_actions()
            
            # 5. Obliczenie wartości wyjściowej gazu i hamulca
            final_gas, final_brake = logic.calculate_pedals(player_gas, player_brake)

            # 6. Wysłanie danych do wirtualnego pada
            vpad.apply_pedals_and_update(final_gas, final_brake)
            
            # Odświeżanie 60 razy na sekundę
            await asyncio.sleep(1 / 60)

    except asyncio.CancelledError:
        pass
    finally:
        vpad.close()
        telemetry.close()

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        pass