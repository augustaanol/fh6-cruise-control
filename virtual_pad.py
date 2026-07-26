import vgamepad as vg

class VirtualPad:
    def __init__(self):
        self.gamepad = vg.VX360Gamepad()

    def update_sticks(self, sticks):
        self.gamepad.left_joystick_float(sticks[0][0], sticks[0][1])
        self.gamepad.right_joystick_float(sticks[1][0], sticks[1][1])

    def apply_pedals_and_update(self, final_gas, final_brake):
        self.gamepad.right_trigger_float(final_gas)
        self.gamepad.left_trigger_float(final_brake)
        self.gamepad.update()

    def close(self):
        self.gamepad.reset()
        self.gamepad.update()