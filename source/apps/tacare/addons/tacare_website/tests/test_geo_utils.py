"""Dependency-free numeric checks: python3 path/to/test_geo_utils.py."""
import importlib.util
import math
from pathlib import Path
import random
import unittest

spec = importlib.util.spec_from_file_location('geo_utils', Path(__file__).resolve().parents[1] / 'geo_utils.py')
geo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geo)


class GeoCheck(unittest.TestCase):
    def test_known_encoding(self):
        self.assertEqual(geo.encode(42.6, -5.6, 5), 'ezs42')
        self.assertEqual(geo.distance_km(0, 0, 0, 0), 0)
        self.assertAlmostEqual(geo.distance_km(0, 0, 0, 1), 111.195, places=3)

    def test_cover_crosses_cells_and_antimeridian(self):
        rng = random.Random(37)
        for lat, lon in [(10.7769, 106.7009), (21.0285, 105.8542), (0, 179.99), (70, -179.99)]:
            for radius in (2, 5, 10, 20, 50):
                cells = geo.cover(lat, lon, radius)
                self.assertEqual(len(cells), len(set(cells)))
                for _ in range(400):
                    delta_lat = rng.uniform(-radius, radius) / 111.3
                    delta_lon = rng.uniform(-radius, radius) / (111.3 * math.cos(math.radians(lat)))
                    target = (lat + delta_lat, (lon + delta_lon + 180) % 360 - 180)
                    if geo.distance_km(lat, lon, *target) <= radius:
                        self.assertIn(geo.encode(*target, 4), cells)

    def test_bounds_and_approximation(self):
        point = (10.77691, 106.70091)
        coarse = geo.approximate(*point)
        self.assertNotEqual(list(point), coarse)
        self.assertEqual(geo.encode(*point, 5), geo.encode(*coarse, 5))
        with self.assertRaises(ValueError): geo.encode(float('nan'), 106)
        with self.assertRaises(ValueError): geo.cover(10, 106, 500)


if __name__ == '__main__':
    unittest.main()
