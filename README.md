# Forza Horizon Cruise Control
Skrypt w Pythonie dodający funkcję tempomatu (Cruise Control) do serii gier Forza Horizon (FH4 / FH5 / FH6). Wykorzystuje odczyt telemetrii przez UDP oraz emulację wirtualnego kontrolera Xbox 360 (vgamepad), pozwalając na pełną swobodę sterowania i rozglądania się padem w tym samym czasie.

## Wymagania wstępne
1. uv - szybki manager pakietów dla Pythona. Jeśli nie masz jeszcze uv, zainstaluj go poleceniem w PowerShell
```PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
2. Pad zgodny z XInput
W przypadku korzystania z kontrolera Sony użyj oprogramowania tłumaczącego go na XInput np. [DS4Windows](https://ds4-windows.com/)

## Instalacja
Sklonuj repozytorium:
```Bash
git clone https://github.com/augustaanol/fh6-cruise-control
```
## Konfiguracja
### 1. Ustawienia w grze
Przejdź do Ustawienia -> Ekran i rozgrywka -> Telemetria 
- Wysyłanie danych (Data Out): WŁ (ON)
- Adres IP (Data Out IP): 127.0.0.1
- Port (Data Out Port): 8000
### 2. Konfiguracja w kodzie (cruise-control.py)
W sekcji konfiguracyjnej na początku skryptu możesz dostosować przypisania przycisków oraz zachowanie tempomatu:
```Python

# --- NETWORK CONFIGURATION ---
LISTEN_IP = "127.0.0.1"          # Adres lokalny komputera
LISTEN_PORT = 8000               # Port nasłuchu telemtrii (taki sam jak ustawiony w grze)

FORWARD_IP = "192.168.0.30"      # Adres do przekazywania telemetrii dla innej aplikacji
FORWARD_PORT = 8000  

# --- CRUISE CONTROL CONFIGURATION ---
STARTUP_TARGET_SPEED_KMH = 60.0  # Początkowa prędkość po uruchomieniu skryptu
KP = 0.3                         # Współczynnik dynamiki (agresywność przyspieszania/hamowania)

# --- KEYBOARD ---
KB_TOGGLE_RESUME = 'z'           # Włącza na ostatnio zapamiętanej prędkości (lub wyłącza)
KB_TOGGLE_CURRENT = 'x'          # Włącza na BIEŻĄCEJ prędkości z telemetrii (lub wyłącza)
KB_SPEED_UP = keyboard.Key.page_up
KB_SPEED_DOWN = keyboard.Key.page_down

# --- GAMEPAD (XInput) ---
# Available buttons: 'DPAD_UP', 'DPAD_DOWN', 'DPAD_LEFT', 'DPAD_RIGHT', 'START', 'BACK', 'LEFT_THUMB', 'RIGHT_THUMB', 'LEFT_SHOULDER', 'RIGHT_SHOULDER', 'A', 'B', 'X', 'Y'
PAD_TOGGLE_RESUME = ''
PAD_TOGGLE_CURRENT = ''
PAD_SPEED_UP = ''
PAD_SPEED_DOWN = ''
```
## Uruchomienie
### Automatycznie (Zalecany w Windows)
Uruchom plik run.bat (dwukrotnym kliknięciem lub z terminala). Skrypt automatycznie sprawdzi dostępność aktualizacji w Git (jesli wykryje repozytorium), zsynchronizuje zależności i uruchomi aplikację.
### Ręczny 
Otwórz terminal w folderze z plikami skryptu i wykonaj:
```PowerShell
uv sync
uv run cruise-control.py
```
## Sterowanie domyślne
Tempomat oferuje dwa tryby aktywacji:
- [Z] - Wł. z poprzednią / Wył. (Włącza tempomat z ostatnią ustawioną prędkością lub domyślną przy pierwszym włączeniu)
- [X] - Wł. z aktualną / Wył. (Włącza tempomat z aktualna prędkością)

Zmiana prędkości automatycznie wyrównuje do wartości podzielnej przez 5
- [PgUp] - Zwiększ prędkość o 5 km/h
- [PgDown] - Zmniejsz prędkość o 5 km/h