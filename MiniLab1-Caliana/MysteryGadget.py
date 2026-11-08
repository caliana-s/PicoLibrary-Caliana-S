"""
# MysteryGadget.py
# Simulates an interactive engine gadget integrating an LCD display, buzzer, Neopixel light strip, and potentiometer
# Author: caliana-s
"""

import time
from Log import *


class MysteryGadget:
    """
    **MysteryGadget** simulates an interactive automobile engine dashboard.
    
    It integrates four hardware peripherals:
    - An **LCD display** (e.g., `LCDDisplay`) to display engine status, RPM, and speed.
    - A **buzzer** (e.g., `PassiveBuzzer`) to synthesize engine revs and low-frequency startup sounds.
    - A **Neopixel light strip** (e.g., `LightStrip`) to serve as a multi-color tachometer.
    - A **potentiometer** (e.g., `AnalogSensor`) to serve as the throttle / gas pedal.

    Parameters:
    ----------
    display : Display or LCDDisplay
        The display object responsible for presenting text and numeric information.
    buzzer : Buzzer or PassiveBuzzer
        The buzzer object used to play tone frequencies mimicking engine audio.
    light_strip : LightStrip
        The Neopixel light strip object used as a tachometer visualizer.
    potentiometer : Sensor or AnalogSensor or object
        The analog potentiometer sensor providing raw ADC readings (0-65535).
    min_rpm : int, optional
        The idle engine RPM speed (default: 800).
    max_rpm : int, optional
        The maximum (redline) engine RPM speed (default: 8000).
    max_speed : int, optional
        The maximum simulated vehicle speed in mph (default: 140).

    Examples:
    ---------
    1. Basic setup with hardware components:
       ```python
       from Displays import LCDDisplay
       from Buzzer import PassiveBuzzer
       from LightStrip import LightStrip
       from Sensors import AnalogSensor
       from MysteryGadget import MysteryGadget

       lcd = LCDDisplay(sda=0, scl=1)
       buzzer = PassiveBuzzer(pin=15)
       strip = LightStrip(pin=2, numleds=8)
       pot = AnalogSensor(pin=26)

       gadget = MysteryGadget(lcd, buzzer, strip, pot)
       gadget.start()
       gadget.control()
       gadget.stop()
       ```
    """

    def __init__(self, display, buzzer, light_strip, potentiometer, min_rpm=800, max_rpm=8000, max_speed=140):
        """
        Initialize the MysteryGadget instance with all required hardware peripherals.

        Parameters:
        ----------
        display : Display or LCDDisplay
            The LCD display instance.
        buzzer : Buzzer or PassiveBuzzer
            The buzzer instance.
        light_strip : LightStrip
            The Neopixel light strip instance.
        potentiometer : Sensor or AnalogSensor or object
            The analog potentiometer instance.
        min_rpm : int, optional
            Idle engine RPM (default: 800).
        max_rpm : int, optional
            Maximum engine RPM (default: 8000).
        max_speed : int, optional
            Maximum vehicle speed in mph (default: 140).

        Examples:
        ---------
        1. Initialize with custom RPM bounds:
           ```python
           gadget = MysteryGadget(lcd, buzzer, strip, pot, min_rpm=1000, max_rpm=9000)
           ```
        """
        Log.i("MysteryGadget: Initializing gadget components...")
        self._display = display
        self._buzzer = buzzer
        self._light_strip = light_strip
        self._potentiometer = potentiometer

        self._min_rpm = int(min_rpm)
        self._max_rpm = int(max_rpm)
        self._max_speed = int(max_speed)

        self._running = False
        self._current_rpm = self._min_rpm
        self._current_speed = 0

    def start(self):
        """
        Simulate starting the engine.
        
        This method plays a sequence of low-frequency engine cranking and idle rumble tones
        on the buzzer, initializes the display with starting speed and idle RPM values,
        and sets the initial tachometer state on the Neopixel strip.

        Parameters:
        ----------
        None

        Examples:
        ---------
        1. Start the engine gadget:
           ```python
           gadget.start()
           ```
        """
        Log.i("MysteryGadget: Starting engine simulation...")
        self._running = True

        # Display starting status
        if hasattr(self._display, "clear"):
            self._display.clear()
        if hasattr(self._display, "showText"):
            self._display.showText("Starting engine...", 0, 0)

        # Simulate low-frequency starter crank on the buzzer
        crank_tones = [50, 70, 60, 85, 75]
        for tone in crank_tones:
            if hasattr(self._buzzer, "play"):
                self._buzzer.play(tone)
            time.sleep(0.08)

        # Transition to low-frequency idle rumble (~70 Hz)
        idle_tone = 70
        if hasattr(self._buzzer, "play"):
            self._buzzer.play(idle_tone)

        self._current_rpm = self._min_rpm
        self._current_speed = 0

        # Show initial RPM and speed on the display
        if hasattr(self._display, "clear"):
            self._display.clear()
        if hasattr(self._display, "showText"):
            self._display.showText(f"RPM: {self._current_rpm:<11}", 0, 0)
            self._display.showText(f"Speed: {self._current_speed:>3} mph   ", 1, 0)

        # Set idle indicator on the light strip
        if hasattr(self._light_strip, "setPixel"):
            self._light_strip.setPixel(0, (0, 255, 0), show=True)

        Log.i(f"MysteryGadget: Engine started at idle ({self._min_rpm} RPM, {self._current_speed} mph)")

    def stop(self):
        """
        Stop the engine simulation.
        
        This method shuts down the engine, halts all buzzer sounds, extinguishes
        the Neopixel light strip, and displays "Engine stopped" on the LCD.

        Parameters:
        ----------
        None

        Examples:
        ---------
        1. Stop the engine gadget:
           ```python
           gadget.stop()
           ```
        """
        Log.i("MysteryGadget: Stopping engine simulation...")
        self._running = False

        # Stop audio immediately
        if hasattr(self._buzzer, "stop"):
            self._buzzer.stop()

        # Turn off Neopixel light strip
        if hasattr(self._light_strip, "off"):
            self._light_strip.off()

        # Update LCD display
        if hasattr(self._display, "clear"):
            self._display.clear()
        if hasattr(self._display, "showText"):
            self._display.showText("Engine stopped  ", 0, 0)

        Log.i("MysteryGadget: Engine successfully stopped")

    def control(self, iterations=None, delay=0.1):
        """
        Monitor the potentiometer and simulate engine acceleration and deceleration.
        
        Uses the raw value from the potentiometer to dynamically modulate engine RPM,
        synthesize corresponding engine sound frequencies on the buzzer, render a
        tachometer visualization across the Neopixel light strip, and show simulated
        RPM and speed values on the LCD display.

        Parameters:
        ----------
        iterations : int, optional
            Number of control cycles to execute. If None, loops continuously until
            interrupted or stop() is invoked (default: None).
        delay : float, optional
            Delay in seconds between successive sensor reads and updates (default: 0.1).

        Examples:
        ---------
        1. Run continuous control loop:
           ```python
           gadget.control()
           ```
        2. Run 50 cycles with 50ms delay:
           ```python
           gadget.control(iterations=50, delay=0.05)
           ```
        """
        if not self._running:
            Log.i("MysteryGadget: Engine is not running; starting before entering control loop")
            self.start()

        Log.i("MysteryGadget: Entering control loop...")
        num_leds = getattr(self._light_strip, "_numleds", 8)
        cycle_count = 0

        try:
            while self._running:
                # 1. Read potentiometer raw value (ADC range 0 - 65535)
                raw_val = self._read_potentiometer()
                raw_clamped = max(0, min(65535, int(raw_val)))
                ratio = raw_clamped / 65535.0

                # 2. Compute simulated RPM and vehicle speed
                self._current_rpm = int(self._min_rpm + ratio * (self._max_rpm - self._min_rpm))
                self._current_speed = int(ratio * self._max_speed)

                # 3. Simulate engine pitch modulation on the buzzer
                # Low idle (~60 Hz) ramping up to aggressive rev tone (~550 Hz)
                engine_frequency = int(60 + ratio * 490)
                if hasattr(self._buzzer, "play"):
                    self._buzzer.play(engine_frequency)

                # 4. Visualize RPM on the Neopixel light strip
                lit_leds = int(ratio * num_leds)
                for i in range(num_leds):
                    if i <= lit_leds and lit_leds > 0:
                        # Color coding: Green (safe) -> Yellow/Orange (mid) -> Red (redline)
                        if i < int(num_leds * 0.5):
                            color = (0, 255, 0)
                        elif i < int(num_leds * 0.8):
                            color = (255, 180, 0)
                        else:
                            color = (255, 0, 0)
                        if hasattr(self._light_strip, "setPixel"):
                            self._light_strip.setPixel(i, color, show=False)
                    else:
                        if hasattr(self._light_strip, "setPixel"):
                            self._light_strip.setPixel(i, (0, 0, 0), show=False)
                if hasattr(self._light_strip, "show"):
                    self._light_strip.show()

                # 5. Show simulated RPM and speed on the display
                if hasattr(self._display, "showText"):
                    self._display.showText(f"RPM: {self._current_rpm:<11}", 0, 0)
                    self._display.showText(f"Speed: {self._current_speed:>3} mph   ", 1, 0)

                Log.i(f"MysteryGadget: Raw={raw_clamped} -> RPM={self._current_rpm}, Speed={self._current_speed}mph, Freq={engine_frequency}Hz")

                time.sleep(delay)

                if iterations is not None:
                    cycle_count += 1
                    if cycle_count >= iterations:
                        break

        except KeyboardInterrupt:
            Log.i("MysteryGadget: Control loop interrupted by user")
            self.stop()

    def _read_potentiometer(self):
        """
        Internal helper to safely read the raw ADC value from the potentiometer object.

        Returns:
        -------
        int
            Raw sensor value between 0 and 65535.
        """
        if hasattr(self._potentiometer, "rawValue"):
            return self._potentiometer.rawValue()
        elif hasattr(self._potentiometer, "read_u16"):
            return self._potentiometer.read_u16()
        elif hasattr(self._potentiometer, "value"):
            return self._potentiometer.value()
        elif callable(self._potentiometer):
            return self._potentiometer()
        else:
            return int(self._potentiometer)


if __name__ == "__main__":
    Log.i("Starting MysteryGadget self-test...")

    # Mock Display for verification
    class MockDisplay:
        def __init__(self):
            self.lines = ["", ""]

        def clear(self, line=-1):
            if line < 0:
                self.lines = ["", ""]
            else:
                self.lines[line] = ""
            Log.i(f"MockDisplay: clear(line={line})")

        def showText(self, text, row=0, col=0):
            self.lines[row] = text
            Log.i(f"MockDisplay [Row {row}]: {text.strip()}")

    # Mock Buzzer for verification
    class MockBuzzer:
        def __init__(self):
            self.tone = 0
            self.is_playing = False

        def play(self, tone):
            self.tone = tone
            self.is_playing = True
            Log.i(f"MockBuzzer: Playing tone {tone} Hz")

        def stop(self):
            self.tone = 0
            self.is_playing = False
            Log.i("MockBuzzer: Stopped")

    # Mock LightStrip for verification
    class MockLightStrip:
        def __init__(self, numleds=8):
            self._numleds = numleds
            self.pixels = [(0, 0, 0)] * numleds
            self.is_on = False

        def setPixel(self, pixelno, color, show=True):
            if 0 <= pixelno < self._numleds:
                self.pixels[pixelno] = color

        def show(self):
            active_count = sum(1 for p in self.pixels if p != (0, 0, 0))
            Log.i(f"MockLightStrip: Displaying {active_count}/{self._numleds} active LEDs")

        def off(self):
            self.pixels = [(0, 0, 0)] * self._numleds
            self.is_on = False
            Log.i("MockLightStrip: Turned off")

        def on(self):
            self.is_on = True
            Log.i("MockLightStrip: Turned on")

    # Mock Potentiometer simulating increasing and decreasing throttle
    class MockPotentiometer:
        def __init__(self, values):
            self._values = values
            self._idx = 0

        def rawValue(self):
            val = self._values[self._idx % len(self._values)]
            self._idx += 1
            return val

    # Instantiate mock hardware components
    display = MockDisplay()
    buzzer = MockBuzzer()
    light_strip = MockLightStrip(numleds=8)
    # Simulated values: idle -> acceleration -> redline -> deceleration -> idle
    throttle_values = [0, 16384, 32768, 49152, 65535, 49152, 32768, 16384, 0]
    potentiometer = MockPotentiometer(throttle_values)

    # 1. Test Instantiation
    gadget = MysteryGadget(display, buzzer, light_strip, potentiometer)
    assert not gadget._running, "Engine should start in unstarted state"

    # 2. Test Start Method
    gadget.start()
    assert gadget._running, "Engine should be running after start()"
    assert buzzer.is_playing, "Buzzer should be active after start()"
    assert "RPM: 800" in display.lines[0], "Display should show idle RPM"
    assert "Speed:   0" in display.lines[1], "Display should show 0 speed"

    # 3. Test Control Method (simulating throttle acceleration and deceleration)
    gadget.control(iterations=len(throttle_values), delay=0.01)
    assert buzzer.is_playing, "Buzzer should be playing engine tone"

    # 4. Test Stop Method
    gadget.stop()
    assert not gadget._running, "Engine should be stopped after stop()"
    assert not buzzer.is_playing, "Buzzer should be stopped"
    assert "Engine stopped" in display.lines[0], "Display should show 'Engine stopped'"

    Log.i("Testing complete - all checks passed")
