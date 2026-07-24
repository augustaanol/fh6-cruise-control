# Forza Horizon Cruise Control

Skrypt w Pythonie dodający funkcję tempomatu do FH4 / FH5 / FH6. Wykorzystuje odczyt telemetrii przez UDP oraz emulację wirtualnego kontrolera Xbox 360 (vgamepad), pozwalając na pełną swobodę kierowania padem w tym samym czasie.

## Wymagania wstępne
Jedynym narzędziem, jakiego potrzebujesz w systemie, jest uv (szybki menedżer pakietów i projektów). Python zostanie pobrany i skonfigurowany przez uv automatycznie.

Jeśli nie masz jeszcze uv, zainstaluj go poleceniem:

PowerShell:

```PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Instalacja
Sklonuj repozytorium i przejdź do niego w terminalu:

Bash
mkdir forza-cruise
cd forza-cruise
Zsynchronizuj projekt projekt za pomocą uv (automatycznie pobierze odpowiednią wersje Pythona, zainstaluje wymagane biblioteki i utworzy środowisko wirtualne):

```Bash
uv sync
```

## Konfiguracja

1. Ustawienia w grze
    Przejdź do Ustawienia -> Ekran i rozgrywka -> Telemetria:

    Wysyłanie danych (Data Out): WŁ (ON)
    Adres IP (Data Out IP): 127.0.0.1
    Port (Data Out Port): 8000

2. Konfiguracja w kodzie (main.py)
    W sekcji początkowej skryptu możesz dostosować parametry:

    ``` Python
    LISTEN_IP = "0.0.0.0"    # Lokalny adres
    LISTEN_PORT = 8000       # Musi pokrywać się z portem w grze

    FORWARD_IP = "192.168.0.30"  # Opcjonalny forward telemetrii (np. na dashboard webowy)
    FORWARD_PORT = 8000          

    target_speed_kmh = 90.0      # Początkowa prędkość docelowa
    KP = 0.3                     # Współczynnik dynamiki tempomatu
    ```

## Uruchomienie
Uruchom skrypt bezpośrednio przez uv (narzędzie samo zadba o środowisko wirtualne i odpowiednią wersję Pythona):

```Bash
uv run main.py
```

## Sterowanie z klawiatury:

C – Włączenie / Wyłączenie tempomatu
Page Up – Zwiększenie prędkości docelowej o 5 km/h
Page Down – Zmniejszenie prędkości docelowej o 5 km/h