"""Geohash cover plus exact great-circle filtering; no network/dependencies."""
import math

ALPHABET = '0123456789bcdefghjkmnpqrstuvwxyz'
EARTH_KM = 6371.0088


def encode(lat, lon, precision=7):
    if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError('Invalid coordinates')
    intervals = [[-180., 180.], [-90., 90.]]
    result, value, bits, axis = '', 0, 0, 0
    while len(result) < precision:
        low, high = intervals[axis]
        midpoint = (low + high) / 2
        upper = (lon if axis == 0 else lat) >= midpoint
        intervals[axis][0 if upper else 1] = midpoint
        value = (value << 1) | upper
        bits += 1
        axis = 1 - axis
        if bits == 5:
            result += ALPHABET[value]
            value, bits = 0, 0
    return result


def bounds(code):
    intervals, axis = [[-180., 180.], [-90., 90.]], 0
    for char in code:
        number = ALPHABET.index(char)
        for shift in (4, 3, 2, 1, 0):
            midpoint = sum(intervals[axis]) / 2
            intervals[axis][0 if number & (1 << shift) else 1] = midpoint
            axis = 1 - axis
    return (*intervals[1], *intervals[0])  # south, north, west, east


def approximate(lat, lon):
    south, north, west, east = bounds(encode(lat, lon, 5))
    return [(south + north) / 2, (west + east) / 2]


def distance_km(a_lat, a_lon, b_lat, b_lon):
    lat1, lat2 = math.radians(a_lat), math.radians(b_lat)
    dlat, dlon = lat2 - lat1, math.radians(b_lon - a_lon)
    value = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_KM * math.asin(math.sqrt(min(1., max(0., value))))


def cover(lat, lon, radius_km):
    """All precision-4 cells intersecting the circle's bounding rectangle.

    Includes neighboring cells and wraps the antimeridian. The caller MUST
    apply distance_km afterward. Near a pole all longitudes may be necessary.
    """
    if not math.isfinite(radius_km) or not 0 < radius_km <= 50:
        raise ValueError('Radius must be in (0, 50] km')
    encode(lat, lon)
    delta = math.degrees(radius_km / EARTH_KM)
    south, north = max(-90., lat - delta), min(90., lat + delta)
    longitude_delta = 180. if south <= -90 or north >= 90 else math.degrees(
        math.asin(min(1., math.sin(radius_km / EARTH_KM) / math.cos(math.radians(lat)))))
    lon_step, lat_step = 360 / 1024, 180 / 1024
    codes = set()
    for row in range(max(0, int((south + 90) // lat_step)), min(1023, int((north + 90) // lat_step)) + 1):
        for col in range(int((lon - longitude_delta + 180) // lon_step), int((lon + longitude_delta + 180) // lon_step) + 1):
            codes.add(encode(-90 + (row + .5) * lat_step, -180 + ((col % 1024) + .5) * lon_step, 4))
    return sorted(codes)
