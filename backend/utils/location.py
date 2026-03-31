"""
定位与路线偏离工具模块
使用 geopy 计算两点距离，判断路线偏离
"""
from typing import Optional


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Haversine 公式计算两点距离（单位：米）"""
    import math
    R = 6371000  # 地球半径(m)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def check_route_deviation(
    current_lat: float,
    current_lng: float,
    route_points: list,
    threshold_m: float = 50.0,
) -> dict:
    """
    检测当前位置是否偏离路线
    route_points: [{"lat": ..., "lng": ...}, ...]
    返回: {"deviated": bool, "min_distance_m": float}
    """
    if not route_points:
        return {"deviated": False, "min_distance_m": 0.0}
    min_dist = min(
        haversine(current_lat, current_lng, p["lat"], p["lng"])
        for p in route_points
    )
    return {
        "deviated": min_dist > threshold_m,
        "min_distance_m": round(min_dist, 1),
    }
