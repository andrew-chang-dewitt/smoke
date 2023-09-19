from typing import List, Tuple
from unittest import TestCase, main

from smoke.trend import simple_slope


class TestSimpleSlope(TestCase):
    """Testing behavior of the simple_slope function."""

    def test_returns_0_if_only_zero_or_one_datapoints_long(self) -> None:
        """If the data is too short, assume an unchanging trend."""
        samples: List[Tuple[int, List[Tuple[float, float]]]] = [
            (0, []),
            (0, [(10.0, 10.0)]),
        ]

        for expected, data in samples:
            with self.subTest():
                actual = simple_slope(data)
                self.assertEqual(actual, expected)

    def test_scales_with_range_of_data(self) -> None:
        """
        The trend value scales with the variance in range.

        This helps account for the case where the average change in the set is
        some value, but the lowest and highest value in the set are very far
        apart.
        """

        close_together = [
                (0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0)]
        far_apart = [
                (0.0, 0.0), (1.0, 0.0), (2.0, 3.0), (3.0, 3.0)]

        close_trend = simple_slope(close_together)
        far_trend = simple_slope(far_apart)

        self.assertLess(close_trend, far_trend)


if __name__ == "__main__":
    main()
