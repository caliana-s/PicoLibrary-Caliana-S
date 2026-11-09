"""
# main.py
# Main entry point to initialize, start, control, and stop MysteryGadget in MicroPython
# Author: caliana-s
"""

import time
from Log import *
from MysteryGadget import MysteryGadget

# Attempt to import MicroPython hardware modules; fall back to mocks on desktop
try:
    from Displays import LCDDisplay
    from Buzzer import PassiveBuzzer
    from LightStrip import LightStrip
    from Sensors import AnalogSensor
    IS_HARDWARE = True
except (ImportError, ModuleNotFoundError):
    IS_HARDWARE = False


def create_gadget():
    """
    Instantiate the hardware peripherals or mocks and create a MysteryGadget instance.

    Hardware Pin Assignments:
    -------------------------
    - LCD Display: I2C0 on SDA=GP0, SCL=GP1
    - Passive Buzzer: GP15
    - Neopixel Light Strip: GP2 (8 LEDs)
    - Potentiometer: GP26 (ADC0)

    Returns:
    --------
    MysteryGadget
        An initialized MysteryGadget instance.
    """
    if IS_HARDWARE:
        Log.i("main: Initializing Raspberry Pi Pico hardware peripherals...")
        lcd = LCDDisplay(sda=0, scl=1)
        buzzer = PassiveBuzzer(pin=16, name="EngineBuzzer")
        light_strip = LightStrip(pin=2, name="Tachometer", numleds=8, brightness=0.5)
        potentiometer = AnalogSensor(pin=26, name="ThrottlePot", lowActive=False)
    else:
        Log.i("main: Running in simulated environment (mocks active)...")

        class MockDisplay:
            def clear(self, line=-1):
                pass
            def showText(self, text, row=0, col=0):
                Log.i(f"[LCD Row {row}]: {text.strip()}")

        class MockBuzzer:
            def play(self, tone):
                Log.i(f"[Buzzer]: Playing {tone} Hz")
            def stop(self):
                Log.i("[Buzzer]: Stopped")

        class MockLightStrip:
            def __init__(self, numleds=8):
                self._numleds = numleds
                self.pixels = [(0, 0, 0)] * numleds
            def setPixel(self, pixelno, color, show=True):
                if 0 <= pixelno < self._numleds:
                    self.pixels[pixelno] = color
            def show(self):
                active = sum(1 for p in self.pixels if p != (0, 0, 0))
                Log.i(f"[LightStrip]: Tachometer {active}/{self._numleds} LEDs illuminated")
            def off(self):
                Log.i("[LightStrip]: LEDs OFF")

        class MockPotentiometer:
            def __init__(self):
                self._step = 0
            def rawValue(self):
                # Simulate ramping throttle up and down over 10 seconds
                # Triangle wave between 0 and 65535
                cycle = self._step % 40
                if cycle < 20:
                    val = int((cycle / 20.0) * 65535)
                else:
                    val = int(((40 - cycle) / 20.0) * 65535)
                self._step += 1
                return val

        lcd = MockDisplay()
        buzzer = MockBuzzer()
        light_strip = MockLightStrip(numleds=8)
        potentiometer = MockPotentiometer()

    return MysteryGadget(
        display=lcd,
        buzzer=buzzer,
        light_strip=light_strip,
        potentiometer=potentiometer,
        min_rpm=800,
        max_rpm=8000,
        max_speed=140
    )


def main():
    """
    Main execution workflow:
    1. Initialize the MysteryGadget instance.
    2. Start the engine simulation.
    3. Monitor and control the engine based on potentiometer input for ~10 seconds.
    4. Stop the engine simulation.
    """
    Log.i("=== Starting MysteryGadget Application ===")

    # 1. Create gadget instance
    gadget = create_gadget()

    # 2. Start the engine gadget
    Log.i("main: Starting engine...")
    gadget.start()

    # 3. Control for about 10 seconds (100 iterations at 0.1s interval = 10.0 seconds)
    duration_seconds = 10
    interval = 0.1
    iterations = int(duration_seconds / interval)

    Log.i(f"main: Monitoring and controlling engine for ~{duration_seconds} seconds...")
    gadget.control(iterations=iterations, delay=interval)

    # 4. Stop the engine gadget
    Log.i("main: Stopping engine...")
    gadget.stop()

    Log.i("=== MysteryGadget Application Completed ===")


if __name__ == "__main__":
    main()
