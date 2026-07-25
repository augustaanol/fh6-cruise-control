# Forza Horizon Cruise Control
Skrypt w Pythonie dodający funkcję tempomatu (Cruise Control) do serii gier Forza Horizon (FH4 / FH5 / FH6). Wykorzystuje odczyt telemetrii przez UDP oraz emulację wirtualnego kontrolera Xbox 360 (vgamepad), pozwalając na pełną swobodę sterowania i rozglądania się padem w tym samym czasie.

## Wymagania wstępne
1. uv - szybki manager pakietów dla Pythona. Jeśli nie masz jeszcze uv, zainstaluj go poleceniem w PowerShell
```PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
2. Kontroler zgodny z XInput
W przypadku korzystania z kontrolera Sony użyj oprogramowania tłumaczącego na XInput np. [DS4Windows](https://ds4-windows.com/)

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

### 2. Konfiguracja skryptu (config.yaml)
[Uruchom](https://github.com/augustaanol/fh6-cruise-control#uruchomienie) i zamknij skrypt by utworzyć domyślny plik konfiguracyjny.

#### network
| Zmienna | Wartość domyślna | Opis |
| --- | --- | --- |
| listen_ip | "127.0.0.1" | Adres na którym skrypt nasłuchuje telemetrii |
| listen_port | 8000 | Port na którym skrypt nasłuchuje telemetrii |
| forward_enabled | true | Przekazywanie surowej telemetrii z gry do innego urządzenia/programu np. SimHub |
| forward_ip | "127.0.0.1" | Adres przekazywania |
| forward_port | 8001 | Port przekazywania |

#### cruise_control
| Zmienna | Wartość domyślna | Opis |
| --- | --- | --- |
| startup_target_speed_kmh | 60.0 | Domyślna prędkość docelowa - używana jedynie przy pierwszym włączeniu w trybie "Wł. z poprzednią" |
| speed_step_kmh | 5.0 | Krok przy zwiększaniu/zmniejszaniu prędkości docelowej |
| kp | 0.4 | (0-1) Współczynnik siły przyspieszania/hamowania. Wyższy = bardziej agresywny. (Work in progress) | 

#### Sterowanie
| Zmienna | Domyśl. klawiatura | Domyśl. kontroler | Opis |
| --- | --- | --- | --- |
| toggle_resume | 'home' | '' | Wł. z poprzednią / Wył. - włącza tempomat z ostatnią ustawioną prędkością (domyślną przy pierwszym włączeniu) |
| toggle_current | 'end' | '' | Wł. z aktualną / Wył. - Włącza tempomat z aktualna prędkością |
| speed_up | 'page_up' | '' | Zwiększ prędkość (domyślnie +5 km/h) |
| speed_down | 'page_down | '' | Zmniejsz prędkość (domyślnie -5 km/h) |

Dostępne przyciski dla kontrolera: 'DPAD_UP', 'DPAD_DOWN', 'DPAD_LEFT', 'DPAD_RIGHT', 'START', 'BACK', 'LEFT_THUMB', 'RIGHT_THUMB', 'LEFT_SHOULDER', 'RIGHT_SHOULDER', 'A', 'B', 'X', 'Y'

## Uruchomienie
### Automatycznie (zalecane)
Uruchom plik run.bat. Skrypt automatycznie sprawdzi dostępność aktualizacji w Git (jesli wykryje repozytorium), zsynchronizuje zależności i uruchomi aplikację.
### Ręczny 
Otwórz terminal w folderze z plikami skryptu i wykonaj:
```PowerShell
uv run cruise-control.py
```