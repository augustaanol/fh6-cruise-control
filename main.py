import socket
import struct
import math
import asyncio
import vgamepad as vg
from pynput import keyboard
import XInput

# --- KONFIGURACJA UDP ---
LISTEN_IP = "127.0.0.1"  
LISTEN_PORT = 8000       

FORWARD_IP = "192.168.0.30"  
FORWARD_PORT = 8000          

# --- KONFIGURACJA TEMPOMATU ---
target_speed_kmh = 90.0
cruise_enabled = False
KP = 0.3 

gamepad = vg.VX360Gamepad()
has_received_any_data = False

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

def on_press(key):
    global cruise_enabled, target_speed_kmh
    try:
        if key.char == 'c':
            cruise_enabled = not cruise_enabled
            if not cruise_enabled:
                print("\n🛑 Tempomat WYŁĄCZONY.")
    except AttributeError:
        if key == keyboard.Key.page_up:
            target_speed_kmh += 5.0
        elif key == keyboard.Key.page_down:
            target_speed_kmh -= 5.0

async def cruise_control_loop():
    global cruise_enabled, has_received_any_data
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.ioctl(socket.SIO_UDP_CONNRESET, False)
    except:
        pass
    sock.bind((LISTEN_IP, LISTEN_PORT))
    sock.setblocking(False)
    forward_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("==================================================")
    print("🚗 FINALNY TEMPOMAT (Czysty gaz/hamulec) 🎮")
    print("==================================================")
    print("[C] - Włącz/Wyłącz tempomat | [PAGE UP/DOWN] - Zmiana prędkości\n")

    try:
        while True:
            latest_data = None

            while True:
                try:
                    data, _ = sock.recvfrom(1024)
                    if not has_received_any_data:
                        print(f"✅ [Pomyślnie podłączono telemetrię Forzy]")
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

            # --- TYLKO OBSŁUGA PEDAŁÓW (BEZ DOTYKANIA PRZYCISKÓW I GAŁEK) ---
            if XInput.get_connected()[0]:
                try:
                    state = XInput.get_state(0)
                    triggers = XInput.get_trigger_values(state)
                    player_brake = triggers[0]
                    player_gas = triggers[1]

                    if cruise_enabled and current_speed is not None:
                        speed_error = target_speed_kmh - current_speed
                        
                        if speed_error > 0:
                            cruise_gas = min(1.0, speed_error * KP)
                            cruise_brake = 0.0
                            status = "PRZYSPIESZANIE"
                        else:
                            cruise_gas = 0.0
                            cruise_brake = min(1.0, abs(speed_error) * KP)
                            status = "HAMOWANIE   "

                        # Override: Twoje wciśnięcie pedału ma wyższy priorytet
                        final_gas = max(cruise_gas, player_gas)
                        final_brake = max(cruise_brake, player_brake)
                        
                        # print(f"\r[WŁĄCZONY] Cel: {target_speed_kmh:5.1f} | Aktualna: {current_speed:5.1f} km/h | {status} (G: {final_gas:.2f} / H: {final_brake:.2f})", end="")
                    else:
                        # Tempomat wyłączony - przepuszczamy czysty sygnał z Twojego pada
                        final_gas = player_gas
                        final_brake = player_brake
                        
                        if current_speed is not None:
                            # print(f"\r[WYŁĄCZONY] Cel: {target_speed_kmh:5.1f} | Aktualna: {current_speed:5.1f} km/h | Czekam...                 ", end="")
                            pass

                    # Wirtualny pad steruje TYLKO triggerami
                    gamepad.right_trigger_float(final_gas)
                    gamepad.left_trigger_float(final_brake)

                except Exception:
                    pass

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