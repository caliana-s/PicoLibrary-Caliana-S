
"""
FeedbackController.py
Controls the satisfaction kiosk using the five states in the supplied
state diagram.
"""

import time
from Log import *
from StateModel import StateModel
from Counters import SoftwareTimer
from Button import Button
from LightStrip import LightStrip
from Displays import LCDDisplay
from Buzzer import PassiveBuzzer
from Sensors_advanced import UltrasonicSensor
from FeedbackStats import FeedbackStats


class FeedbackController:
    """Control the five kiosk states."""

    LCD_SDA = 0
    LCD_SCL = 1
    LIGHT_STRIP_PIN = 2
    ULTRASONIC_TRIGGER = 6
    ULTRASONIC_ECHO = 7
    BUZZER_PIN = 16
    RED_BUTTON_PIN = 11
    GREEN_BUTTON_PIN = 12

    FEEDBACK_DISPLAY_TIME = 5000

    def __init__(self):
        self._stats = FeedbackStats()

        self._display = LCDDisplay(sda=self.LCD_SDA, scl=self.LCD_SCL)

        self._light = LightStrip(
            pin=self.LIGHT_STRIP_PIN,
            name="Feedback Light",
            numleds=8,
            brightness=0.25
        )

        self._buzzer = PassiveBuzzer(
            pin=self.BUZZER_PIN,
            name="Manager Alarm"
        )

        self._sensor = UltrasonicSensor(
            trigger=self.ULTRASONIC_TRIGGER,
            echo=self.ULTRASONIC_ECHO,
            name="uss",
            lowActive=True,
            threshold=10.2
        )

        self._red_button = Button(
            self.RED_BUTTON_PIN,
            "red",
            handler=None,
            lowActive=True
        )

        self._green_button = Button(
            self.GREEN_BUTTON_PIN,
            "green",
            handler=None,
            lowActive=True
        )

        self._timer = SoftwareTimer(name="timer", handler=None)

        self._alarm_tone = 0
        self._alarm_change = time.ticks_ms()
        self._feedback_screen_started = 0

        # Five states:
        # 0 Welcome
        # 1 Selection
        # 2 Happy
        # 3 Unhappy
        # 4 Calling Manager

        self._model = StateModel(5, self, debug=True)

        self._model.addSensor(self._sensor)
        self._model.addButton(self._red_button)
        self._model.addButton(self._green_button)
        self._model.addTimer(self._timer)
        self._model.addCustomEvent("feedback_below_threshold")

        # State transitions
        self._model.addTransition(0, ["uss_trip"], 1)

        self._model.addTransition(1, ["green_press"], 2)
        self._model.addTransition(1, ["red_press"], 3)
        self._model.addTransition(1, ["timer_timeout"], 0)

        self._model.addTransition(2, ["timer_timeout"], 0)
        self._model.addTransition(2, ["feedback_below_threshold"], 4)

        self._model.addTransition(3, ["timer_timeout"], 0)
        self._model.addTransition(3, ["feedback_below_threshold"], 4)

        self._model.addTransition(4, ["green_press"], 0)

    def _show_lines(self, line1, line2=""):
        """Display two lines on the LCD."""
        self._display.clear()
        self._display.showText(str(line1)[:16], 0, 0)
        self._display.showText(str(line2)[:16], 1, 0)

    def _status_line(self):
        """Display positive feedback percentage and total responses."""
        return "Pos:{:.0f}% Total:{}".format(
            self._stats.calculate_percentage(),
            self._stats.get_total_count()
        )[:16]

    def stateEntered(self, state, event):
        Log.i(
            "FeedbackController entered state {} on {}".format(
                state, event
            )
        )

        if state == 0:
            self._timer.cancel()
            self._buzzer.stop()
            self._light.off()
            self._show_lines("Welcome!", "Come closer...")

        elif state == 1:
            self._buzzer.stop()
            self._light.off()
            self._show_lines("Rate your visit", "Green=Yes Red=No")
            self._timer.start(5)

        elif state == 2:
            self._timer.cancel()
            self._light.setColor((0, 180, 0))
            self._show_lines("Thank you!", self._status_line())

            # Keep the feedback screen visible for five seconds.
            self._feedback_screen_started = time.ticks_ms()

        elif state == 3:
            self._timer.cancel()
            self._light.setColor((180, 0, 0))
            self._show_lines("Sorry to hear", self._status_line())

            # Keep the feedback screen visible for five seconds.
            self._feedback_screen_started = time.ticks_ms()

        elif state == 4:
            self._timer.cancel()
            self._light.setColor((255, 0, 0))
            self._show_lines("Calling manager", "Press GREEN reset")

            self._alarm_tone = 0
            self._alarm_change = time.ticks_ms()
            self._buzzer.play(700)

    def stateLeft(self, state, event):
        Log.i(
            "FeedbackController leaving state {} on {}".format(
                state, event
            )
        )

        # Record customer feedback when leaving Selection.
        if state == 1:
            if event == "green_press":
                self._stats.add_happy()

            elif event == "red_press":
                self._stats.add_unhappy()

        # GREEN simulates manager acknowledgement during the alarm.
        elif state == 4 and event == "green_press":
            self._buzzer.stop()
            self._stats.reset()

    def stateEvent(self, state, event):
        return False

    def stateDo(self, state):
        """Handle feedback timing and the manager alarm."""

        if state == 0 and self._sensor.tripped():
            self._model.processEvent("uss_trip")

        elif state == 2 or state == 3:
            now = time.ticks_ms()

            # Wait five seconds before leaving the feedback screen.
            if time.ticks_diff(
                now, self._feedback_screen_started
            ) >= self.FEEDBACK_DISPLAY_TIME:

                if self._stats.calculate_percentage() < 30.0:
                    self._model.processEvent(
                        "feedback_below_threshold"
                    )
                else:
                    self._model.processEvent("timer_timeout")

        elif state == 4:
            # Alternate alarm tones every 350 milliseconds.
            now = time.ticks_ms()

            if time.ticks_diff(now, self._alarm_change) >= 350:
                self._alarm_tone = 1 - self._alarm_tone

                if self._alarm_tone == 0:
                    self._buzzer.play(700)
                else:
                    self._buzzer.play(1000)

                self._alarm_change = now

    def run(self):
        """Run the kiosk state model."""
        try:
            self._model.run(0.05)
        finally:
            self.stop()

    def stop(self):
        """Stop the kiosk and turn off its outputs."""
        self._timer.cancel()
        self._buzzer.stop()
        self._light.off()
        self._model.stop()


if __name__ == "__main__":
    kiosk = FeedbackController()

    try:
        kiosk.run()
    except KeyboardInterrupt:
        kiosk.stop()
