# Forza Horizon 6 Cruise Control
A Python script that adds a **Cruise Control feature** to the **Forza Horizon 6** (should also work with FH4/FH5 - not tested yet). It utilizes UDP telemetry data and Xbox 360 virtual controller emulation (vgamepad), allowing full freedom to steer and look around using your gamepad at the same time.

## Prerequisites
1. **Windows 11** (may work with Linux, currently not tested)
2. **[uv](https://docs.astral.sh/uv/)** - A fast Python package manager. If you don't have uv installed yet, run this command in PowerShell:
  ```PowerShell
  powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
  ```
3. **An XInput-compatible controller**\
  Tested with Xbox Series and 8BitDo Ultimate 2 controllers. If you are using a DS4/DS5 controller, use an XInput translation tool such as DS4Windows.

## Installation
Clone the repository:

```Bash
git clone [https://github.com/augustaanol/fh6-cruise-control](https://github.com/augustaanol/fh6-cruise-control)
```

...or download .zip (will not update automatically).

## Configuration
### 1. In-game Settings
  Go to Settings -> HUD and Gameplay -> Telemetry
  - Data Out: ON
  - Data Out IP: 127.0.0.1
  - Data Out Port: 8000 (or any other available port set in script configuration)
    
### 2. Script Configuration (config.yaml)
  [Run](#launching) and close the script once to generate the default configuration file.
  #### network
  | Variable | Default Value | Description |
  | --- | --- | --- |
  | listen_ip | "127.0.0.1" | IP address the script listens on for telemetry |
  | listen_port | 8000 | Port the script listens on for telemetry |
  | forward_enabled | false  | Forward raw game telemetry to another device/software, e.g., SimHub |
  | forward_ip | "127.0.0.1" | Forwarding IP address |
  | forward_port | 8001 | Forwarding port |

  #### cruise_control
  | Variable | Default Value | Description |
  | --- | --- | --- |
  | startup_target_speed_kmh | 60.0 | Default target speed - used only on the first enable in "Resume" mode |
  | speed_step_kmh | 5.0 | Speed increment/decrement step |
  | kp | 0.4 | (0-1) Acceleration/braking strength coefficient. Higher = more aggressive. (Work in progress) |

  #### Controls
  | Variable | Default Keyboard | Default Controller | Description |
  | --- | --- | --- | --- |
  | toggle_resume | 'home' | '' | Toggle Resume / Off - enables cruise control at the last set speed (default on first enable) |
  | toggle_current | 'end' | '' | Toggle Current / Off - enables cruise control at your current speed |
  | speed_up | 'page_up' | '' | Increase speed (default +5 km/h) |
  | speed_down | 'page_down' | '' | Decrease speed (default -5 km/h) |
  
  **Available controller buttons:** 
  - 'DPAD_UP'
  - 'DPAD_DOWN'
  - 'DPAD_LEFT'
  - 'DPAD_RIGHT'
  - 'START'
  - 'BACK'
  - 'LEFT_THUMB'
  - 'RIGHT_THUMB'
  - 'LEFT_SHOULDER'
  - 'RIGHT_SHOULDER'
  - 'A'
  - 'B'
  - 'X'
  - 'Y'

## Launching
### Automatic (Recommended)
Run the run.bat file. The script will automatically check for Git updates (if a repository is detected), synchronize dependencies, and launch the application.

### Manual
Open a terminal in the folder containing the script files and execute:
```PowerShell
uv run cruise-control.py
```

  
