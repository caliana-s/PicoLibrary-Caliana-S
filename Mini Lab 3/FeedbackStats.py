"""Feedback statistics for the satisfaction kiosk.

Implements the FeedbackStats class shown in the supplied UML diagram.
"""


class FeedbackStats:
    """Store happy/unhappy response counts and calculate satisfaction."""

    def __init__(self):
        self._happy_count = 0
        self._unhappy_count = 0

    def get_total_count(self):
        """Return the total number of recorded responses."""
        return self._happy_count + self._unhappy_count

    def get_light_level(self):
        """Return positive feedback percentage for the status light/controller."""
        return self.calculate_percentage()

    def calculate_percentage(self):
        """Return the percentage of responses that were positive.

        With no responses, return 100.0 so an empty/reset kiosk does not
        incorrectly trigger the below-30-percent manager alert.
        """
        total = self.get_total_count()
        if total == 0:
            return 100.0
        return (self._happy_count / total) * 100.0

    def add_happy(self):
        """Record one positive response."""
        self._happy_count += 1

    def add_unhappy(self):
        """Record one negative response."""
        self._unhappy_count += 1

    def reset(self):
        """Reset both response counts to zero."""
        self._happy_count = 0
        self._unhappy_count = 0


# Basic desktop-side logic test; this block does not run when imported.
if __name__ == "__main__":
    stats = FeedbackStats()
    assert stats.get_total_count() == 0
    assert stats.calculate_percentage() == 100.0

    stats.add_happy()
    assert stats.get_total_count() == 1
    assert stats.get_light_level() == 100.0

    stats.add_unhappy()
    assert stats.get_total_count() == 2
    assert stats.calculate_percentage() == 50.0

    stats.add_unhappy()
    assert abs(stats.calculate_percentage() - (100.0 / 3.0)) < 0.000001

    stats.reset()
    assert stats.get_total_count() == 0
    assert stats.calculate_percentage() == 100.0
    print("FeedbackStats tests passed.")
