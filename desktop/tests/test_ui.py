"""Presentation helpers do not need a display or GUI input automation."""
from datetime import datetime, timedelta
import unittest
import math

from dhms.app import chart_bounds, display_points, sample_file


class PresentationTests(unittest.TestCase):
    def test_small_series_unchanged(self):
        points = [(datetime(2024, 1, 1), 2)]
        self.assertEqual(display_points(points), points)

    def test_downsampling_bounded_order_and_extrema(self):
        first = datetime(2024, 1, 1)
        points = [(first + timedelta(seconds=i), 1000 if i == 5412 else -1000 if i == 9001 else i % 15) for i in range(20000)]
        sampled = display_points(points)
        self.assertLessEqual(len(sampled), 1000)
        self.assertEqual(sampled[0], points[0])
        self.assertEqual(sampled[-1], points[-1])
        self.assertEqual(sampled, sorted(sampled))
        self.assertIn(points[5412], sampled)
        self.assertIn(points[9001], sampled)

    def test_bundled_sample_present(self):
        self.assertTrue(sample_file().is_file())

    def test_chart_bounds_handle_extreme_and_tiny_finite_ranges(self):
        for values in ((-1e308, 1e308), (-1.7976931348623157e308, 1.7976931348623157e308), (0, 0), (1e-308, 2e-308)):
            scale, low, high = chart_bounds(values)
            self.assertTrue(all(math.isfinite(value) for value in (scale, low, high, high-low)))
            self.assertLess(low, high)
            for value in values:
                coordinate = (value / scale - low) / (high - low)
                self.assertTrue(math.isfinite(coordinate))
                self.assertGreaterEqual(coordinate, 0)
                self.assertLessEqual(coordinate, 1)


if __name__ == "__main__":
    unittest.main()
