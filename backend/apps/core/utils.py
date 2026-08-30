import hashlib
import math
import random
import string
from django.utils import timezone

def compute_sha256(file_obj_or_bytes):
    "Compute SHA-256 hash of file content or bytes for tamper-evidence."
    sha256 = hashlib.sha256()
    if isinstance(file_obj_or_bytes, bytes):
        sha256.update(file_obj_or_bytes)
    elif hasattr(file_obj_or_bytes, 'read'):
        current_pos = file_obj_or_bytes.tell() if hasattr(file_obj_or_bytes, 'tell') else 0
        for chunk in getattr(file_obj_or_bytes, 'chunks', lambda: iter(lambda: file_obj_or_bytes.read(4096), b''))():
            sha256.update(chunk)
        if hasattr(file_obj_or_bytes, 'seek'):
            file_obj_or_bytes.seek(current_pos)
    return sha256.hexdigest()

def hash_session_id(session_id: str) -> str:
    "Anonymously hash client session UUID for privacy."
    if not session_id:
        return ''
    salt = 'awaaz_anon_salt_2026'
    return hashlib.sha256(f'{salt}:{session_id}'.encode('utf-8')).hexdigest()[:32]

def generate_public_id() -> str:
    "Generate public tracking identifier e.g. AWZ-2026-8941."
    year = timezone.now().year
    digits = ''.join(random.choices(string.digits, k=4))
    return f'AWZ-{year}-{digits}'

def haversine_distance_meters(lat1, lon1, lat2, lon2) -> float:
    "Calculate geodesic distance between two points in meters."
    if None in (lat1, lon1, lat2, lon2):
        return float('inf')
    R = 6371000
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    delta_phi = math.radians(float(lat2) - float(lat1))
    delta_lambda = math.radians(float(lon2) - float(lon1))

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def bounding_box(lat, lon, radius_meters=1000):
    "Return (min_lat, max_lat, min_lon, max_lon) for quick DB filtering."
    lat = float(lat)
    lon = float(lon)
    lat_delta = radius_meters / 111000.0
    lon_delta = radius_meters / (111000.0 * math.cos(math.radians(lat)))
    return (lat - lat_delta, lat + lat_delta, lon - lon_delta, lon + lon_delta)
