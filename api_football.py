import logging
import httpx
from typing import Dict, Any, List, Optional
from config import API_KEY, API_BASE_URL

logger = logging.getLogger("APIFootball")

class APIFootballClient:
    def __init__(self, api_key: str = API_KEY, base_url: str = API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "x-apisports-key": self.api_key
        }

        self.quota_exceeded = False

    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Check for API errors or empty results
                errors = data.get("errors", {})
                if errors:
                    logger.warning(f"API Football response errors for {endpoint}: {errors}")
                    if isinstance(errors, dict) and "requests" in errors:
                        err_msg = str(errors.get("requests", ""))
                        if "request limit" in err_msg.lower():
                            self.quota_exceeded = True
                    elif isinstance(errors, list) and errors:
                        err_msg = str(errors[0])
                        if "request limit" in err_msg.lower():
                            self.quota_exceeded = True
                else:
                    self.quota_exceeded = False
                
                return data.get("response", [])
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching {endpoint}: {e.response.status_code} - {e.response.text}")
                return []
            except Exception as e:
                logger.error(f"Unexpected error fetching {endpoint}: {e}")
                return []

    async def get_status(self) -> Dict[str, Any]:
        """Check API subscription status and request usage."""
        url = f"{self.base_url}/status"
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                res = data.get("response", {})
                if isinstance(res, list):
                    return res[0] if res else {}
                elif isinstance(res, dict):
                    return res
                return {}
            except Exception as e:
                logger.error(f"Error fetching status: {e}")
                return {}

    async def get_live_fixtures(self, league_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """Get all currently live matches."""
        params = {"live": "all"}
        fixtures = await self._get("fixtures", params=params)
        
        if league_ids and fixtures:
            fixtures = [f for f in fixtures if f.get("league", {}).get("id") in league_ids]
            
        return fixtures

    async def get_fixture_by_id(self, fixture_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed fixture info by ID (useful when a match finishes and leaves live=all)."""
        res = await self._get("fixtures", params={"id": fixture_id})
        return res[0] if res else None

    async def get_fixture_events(self, fixture_id: int) -> List[Dict[str, Any]]:
        """Get real-time events (goals, cards, subs) for a specific fixture."""
        return await self._get("fixtures/events", params={"fixture": fixture_id})

    async def get_fixture_lineups(self, fixture_id: int) -> List[Dict[str, Any]]:
        """Get starting lineups for a specific fixture."""
        return await self._get("fixtures/lineups", params={"fixture": fixture_id})

    async def get_fixture_statistics(self, fixture_id: int) -> List[Dict[str, Any]]:
        """Get statistics (possession, shots, fouls, corners) for a fixture."""
        return await self._get("fixtures/statistics", params={"fixture": fixture_id})

    async def get_injuries(self, date: Optional[str] = None, league_id: Optional[int] = None, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get player injury reports."""
        params = {}
        if date:
            params["date"] = date
        if league_id:
            params["league"] = league_id
        if season:
            params["season"] = season
            
        return await self._get("injuries", params=params)

    async def get_transfers(self, team_id: Optional[int] = None, player_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get transfer information for a team or player."""
        params = {}
        if team_id:
            params["team"] = team_id
        if player_id:
            params["player"] = player_id
            
        return await self._get("transfers", params=params)
