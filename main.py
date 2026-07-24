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

def find_active_controller_index():
    """Automatycznie wykrywa, pod którym indeksem w systemie znajduje się aktywny pad (0-3)."""
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

def on_press(key):
    global cruise_enabled, target_speed_kmh
    try:
        if key.char == 'c':
            cruise_enabled = not cruise_enabled
            if cruise_enabled:
                print(f"\n🟢 [TEMPOMAT WŁĄCZONY] Docelowa prędkość: {target_speed_kmh:.1f} km/h")
            else:
                print(f"\n🔴 [TEMPOMAT WYŁĄCZONY]")
    except AttributeError:
        if key == keyboard.Key.page_up:
            target_speed_kmh += 5.0
            print(f"\n⏩ Zwiększono prędkość tempomatu do: {target_speed_kmh:.1f} km/h")
        elif key == keyboard.Key.page_down:
            target_speed_kmh -= 5.0
            print(f"\n⏪ Zmniejszono prędkość tempomatu do: {target_speed_kmh:.1f} km/h")

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
    print("🚗 TEMPOMAT XINPUT (Automatyczne wykrywanie pada) 🎮")
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

            # --- DYNAMICZNE WYSZUKIWANIE I KLONOWANIE PADA ---
            controller_idx = find_active_controller_index()
            if controller_idx is not None:
                try:
                    state = XInput.get_state(controller_idx)
                    
                    # 1. Klonowanie lewej gałki (skręt działa idealnie, bez samoczynnego skręcania)
                    sticks = XInput.get_thumb_values(state)
                    gamepad.left_joystick_float(sticks[0][0], sticks[0][1])

                    # 2. Odczyt triggerów gracza
                    triggers = XInput.get_trigger_values(state)
                    player_brake = triggers[0]
                    player_gas = triggers[1]

                    if cruise_enabled and current_speed is not None:
                        speed_error = target_speed_kmh - current_speed
                        
                        if speed_error > 0:
                            cruise_gas = min(1.0, speed_error * KP)
                            cruise_brake = 0.0
                        else:
                            cruise_gas = 0.0
                            cruise_brake = min(1.0, abs(speed_error) * KP)

                        # Override: Twoje fizyczne wciśnięcie ma wyższy priorytet
                        final_gas = max(cruise_gas, player_gas)
                        final_brake = max(cruise_brake, player_brake)
                    else:
                        final_gas = player_gas
                        final_brake = player_brake

                    # Wysyłamy obliczone triggery do wirtualnego pada
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