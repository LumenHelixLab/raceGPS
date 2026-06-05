#!/usr/bin/env python3
"""
raceGPS Supabase API Client

Lightweight wrapper for crowd-sourced contributions.
Usage:
    from api_client import RaceGPSClient
    client = RaceGPSClient("https://your-project.supabase.co", "your-anon-key")
    client.submit_building_annotation("12345", "gas_station", 41.08, -81.52)
"""

import json
import urllib.request
import urllib.error
from typing import Any, Optional


class RaceGPSClient:
    def __init__(self, supabase_url: str, anon_key: str):
        self.base_url = supabase_url.rstrip("/")
        self.headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def _request(self, method: str, path: str, data: Optional[dict] = None, params: Optional[dict] = None) -> dict:
        url = f"{self.base_url}/rest/v1/{path}"
        if params:
            query = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
            url += "?" + query

        req = urllib.request.Request(url, headers=self.headers, method=method)
        if data:
            req.data = json.dumps(data).encode("utf-8")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return {"success": True, "data": json.loads(resp.read().decode("utf-8"))}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8") if e.fp else ""
            return {"success": False, "error": body, "status": e.code}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Players
    # ------------------------------------------------------------------
    def create_player(self, player_name: str = "Driver", avatar_color: str = "#00FFFF") -> dict:
        return self._request("POST", "players", {
            "player_name": player_name,
            "avatar_color": avatar_color,
        })

    def get_player(self, player_id: str) -> dict:
        return self._request("GET", "players", params={"id": f"eq.{player_id}"})

    # ------------------------------------------------------------------
    # User Routes (Community Courses)
    # ------------------------------------------------------------------
    def create_route(self, route_id: str, route_name: str, waypoints: list, checkpoints: list,
                     city_id: str = "akron-oh-beta-001", player_id: Optional[str] = None,
                     distance_meters: float = 0, difficulty: str = "medium") -> dict:
        return self._request("POST", "user_routes", {
            "route_id": route_id,
            "city_id": city_id,
            "player_id": player_id,
            "route_name": route_name,
            "waypoints": json.dumps(waypoints),
            "checkpoints": json.dumps(checkpoints),
            "distance_meters": distance_meters,
            "difficulty": difficulty,
            "status": "published",
        })

    def get_routes_for_city(self, city_id: str, limit: int = 50) -> dict:
        return self._request("GET", "user_routes", params={
            "city_id": f"eq.{city_id}",
            "status": "eq.published",
            "order": "rating_avg.desc",
            "limit": str(limit),
        })

    def rate_route(self, route_uuid: str, player_id: str, rating: int, review_text: str = "") -> dict:
        return self._request("POST", "route_ratings", {
            "route_id": route_uuid,
            "player_id": player_id,
            "rating": rating,
            "review_text": review_text,
        })

    # ------------------------------------------------------------------
    # Building Annotations (Train Mode)
    # ------------------------------------------------------------------
    def submit_building_annotation(self, building_osm_id: str, guessed_type: str,
                                   lat: float, lon: float, player_id: Optional[str] = None,
                                   guessed_name: str = "", confidence: int = 3) -> dict:
        return self._request("POST", "building_annotations", {
            "building_osm_id": building_osm_id,
            "player_id": player_id,
            "guessed_type": guessed_type,
            "guessed_name": guessed_name,
            "confidence": confidence,
            "lat": lat,
            "lon": lon,
        })

    def get_building_annotations(self, building_osm_id: str) -> dict:
        return self._request("GET", "building_annotations", params={
            "building_osm_id": f"eq.{building_osm_id}",
        })

    # ------------------------------------------------------------------
    # Route Feedback
    # ------------------------------------------------------------------
    def submit_route_feedback(self, route_id: str, feedback_type: str,
                              player_id: Optional[str] = None, description: str = "",
                              checkpoint_index: Optional[int] = None,
                              suggested_lat: Optional[float] = None,
                              suggested_lon: Optional[float] = None) -> dict:
        return self._request("POST", "route_feedback", {
            "route_id": route_id,
            "player_id": player_id,
            "feedback_type": feedback_type,
            "description": description,
            "checkpoint_index": checkpoint_index,
            "suggested_lat": suggested_lat,
            "suggested_lon": suggested_lon,
        })

    # ------------------------------------------------------------------
    # Traffic Reports
    # ------------------------------------------------------------------
    def submit_traffic_report(self, lat: float, lon: float, traffic_density: int,
                              city_id: str = "akron-oh-beta-001", player_id: Optional[str] = None,
                              time_of_day: str = "", day_of_week: int = 0) -> dict:
        return self._request("POST", "traffic_reports", {
            "city_id": city_id,
            "player_id": player_id,
            "lat": lat,
            "lon": lon,
            "traffic_density": traffic_density,
            "time_of_day": time_of_day,
            "day_of_week": day_of_week,
        })

    # ------------------------------------------------------------------
    # Contribution Log
    # ------------------------------------------------------------------
    def log_contribution(self, player_id: str, contribution_type: str,
                         target_id: str = "", points_earned: int = 0,
                         metadata: Optional[dict] = None) -> dict:
        return self._request("POST", "contribution_log", {
            "player_id": player_id,
            "contribution_type": contribution_type,
            "target_id": target_id,
            "points_earned": points_earned,
            "metadata": json.dumps(metadata) if metadata else None,
        })

    # ------------------------------------------------------------------
    # Citypack Versions
    # ------------------------------------------------------------------
    def get_citypack_version(self, city_id: str) -> dict:
        return self._request("GET", "citypack_versions", params={
            "city_id": f"eq.{city_id}",
            "is_latest": "eq.true",
            "limit": "1",
        })
