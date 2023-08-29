import unittest
from unittest import TestCase

from smoke.trend import simple_slope


class TestSimpleSlope(TestCase):
    def test_all_same(self) -> None:
        """A list values with the same delta will return that delta."""
        samples = [
            (0.1, [(0,0),(10,1),(20,2),(30,3),(40,4)]),
            (1, [(0,0),(10,10),(20,20),(30,30),(40,40)]),
            (10, [(0,0),(10,100),(20,200),(30,300),(40,400)]),
            (100, [(0,0),(10,1000),(20,2000),(30,3000),(40,4000)]),
        ]

        for expected, data in samples:
            with self.subTest():
                actual = simple_slope(data)
                self.assertEqual(actual, expected)

    def test_returns_0_if_only_zero_or_one_datapoints_long(self) -> None:
        """If the data is too short, assume an unchanging trend."""
        samples = [
            (0, []),
            (0, [(10,10)]),
        ]

        for expected, data in samples:
            with self.subTest():
                actual = simple_slope(data)
                self.assertEqual(actual, expected)


    def test_scales_with_range_of_data(self) -> None:
        """
        The trend value scales with the variance in range.

        This helps account for the case where the average change in the set is
        0ish, but the lowest and highest value in the set are very far apart.
        """

        samples = [
            (1 * (1 + (((0 - 1.5) + (1 - 1.5) + (2 - 1.5) + (3 - 1.5)) / 3)), [(0, 0), (1, 1), (2, 2), (3, 3)]),
            (1 * (1 + (((0 - 1.5) + (0 - 1.5) + (2 - 1.5) + (3 - 1.5)) / 3)), [(0, 0), (1, 0), (2, 2), (3, 3)])
        ]

        for expected, data in samples:
            with self.subTest():
                actual = simple_slope(data)
                self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
