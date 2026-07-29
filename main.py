import asyncio
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any, Set

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from config import (
    LIVE_POLL_INTERVAL,
    IDLE_POLL_INTERVAL,
    TARGET_LEAGUES
)
from api_football import APIFootballClient
from state_manager import StateManager
from telegram_bot import TelegramBroadcaster
from twitter_bot import TwitterBroadcaster
import formatter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ElOnceTitular")

class FootballBotEngine:
    def __init__(self):
        self.api_client = APIFootballClient()
        self.state_manager = StateManager()
        self.telegram_broadcaster = TelegramBroadcaster()
        self.twitter_broadcaster = TwitterBroadcaster()
        self.tracked_live_fixture_ids: Set[int] = set()
        # Pending goal buffer to catch delayed assist data from API
        self.pending_goals: Dict[str, Dict[str, Any]] = {}

    async def broadcast_alert(self, msg: str, event_id: str):
        """Broadcast alert to Telegram (@ElOnceTitular) and Twitter, then mark event as processed."""
        # 1. Telegram
        tg_sent = await self.telegram_broadcaster.send_message(msg)
        # 2. Twitter / X (Disabled)
        tw_sent = await self.twitter_broadcaster.send_tweet(msg)

        if tg_sent or tw_sent:
            self.state_manager.mark_processed(event_id)

    async def check_api_status(self):
        logger.info("Checking API-Football status and quota...")
        status = await self.api_client.get_status()
        if status:
            requests_info = status.get("requests", {})
            subscription = status.get("subscription", {})
            logger.info(f"API Subscription: {subscription.get('plan', 'Unknown')}")
            logger.info(f"Requests used today: {requests_info.get('current', 0)} / {requests_info.get('limit_day', 0)}")
        else:
            logger.warning("Could not retrieve API status.")

    async def snapshot_live_fixtures_on_startup(self):
        """Mark all pre-existing events in currently live fixtures as processed so old past events are never posted."""
        logger.info("Initializing startup snapshot for live matches (suppressing all past events before bot start)...")
        fixtures = await self.api_client.get_live_fixtures(league_ids=TARGET_LEAGUES)
        if fixtures:
            for f in fixtures:
                f_id = f['fixture']['id']
                st_code = f['fixture']['status']['short']
                
                # Track currently live matches
                self.tracked_live_fixture_ids.add(f_id)

                # Mark current status and lineup as already processed
                self.state_manager.mark_processed(f"status_{f_id}_{st_code}")
                self.state_manager.mark_processed(f"lineup_{f_id}")

                # Mark all pre-existing events as already processed
                events = await self.api_client.get_fixture_events(f_id)
                for evt in events:
                    evt_type = evt.get("type", "")
                    elapsed = evt.get("time", {}).get("elapsed", 0)
                    player_id = evt.get("player", {}).get("id", 0) or 0
                    evt_id = f"evt_{f_id}_{elapsed}_{evt_type}_{player_id}"
                    self.state_manager.mark_processed(evt_id)

    async def process_single_fixture(self, fixture: Dict[str, Any], is_finished_check: bool = False):
        """Process a single fixture for live channel (@ElOnceTitular): status transitions, lineups, and events."""
        fixture_id = fixture['fixture']['id']
        status_code = fixture['fixture']['status']['short']
        
        # 1. Match status change alert (Kickoff, HT, 2H, FT, ET, PEN, etc.)
        status_event_id = f"status_{fixture_id}_{status_code}"
        if not self.state_manager.is_processed(status_event_id):
            stats = None
            if status_code in ["HT", "FT", "AET", "PEN"]:
                stats = await self.api_client.get_fixture_statistics(fixture_id)

            status_msg = formatter.format_match_status(fixture, status_code, statistics=stats)
            if status_msg:
                await self.broadcast_alert(status_msg, status_event_id)

        # IF match is finished or we are checking a finished fixture, DO NOT process old past events or lineups!
        if is_finished_check or status_code in ["FT", "AET", "PEN", "CANC", "ABD", "SUSP"]:
            return

        # 2. Lineup check (only for live / upcoming matches)
        lineup_event_id = f"lineup_{fixture_id}"
        if not self.state_manager.is_processed(lineup_event_id):
            lineups = await self.api_client.get_fixture_lineups(fixture_id)
            if lineups:
                lineup_msg = formatter.format_lineup(lineups, fixture)
                if lineup_msg:
                    await self.broadcast_alert(lineup_msg, lineup_event_id)

        # 3. Live events (Goals, Cards, Substitutions, VAR)
        events = await self.api_client.get_fixture_events(fixture_id)
        now_ts = asyncio.get_event_loop().time()

        for evt in events:
            evt_type = evt.get("type", "")
            evt_detail = evt.get("detail", "")
            elapsed = evt.get("time", {}).get("elapsed", 0)
            player_id = evt.get("player", {}).get("id", 0) or 0
            
            # Unique ID per event based on fixture, minute, type and player
            evt_id = f"evt_{fixture_id}_{elapsed}_{evt_type}_{player_id}"
            
            if self.state_manager.is_processed(evt_id):
                continue

            if evt_type == "Goal":
                assist_name = evt.get("assist", {}).get("name")
                if assist_name and assist_name != "None":
                    # Assist is available immediately! Post Goal WITH assist right away.
                    msg = formatter.format_goal(evt, fixture)
                    await self.broadcast_alert(msg, evt_id)
                    if evt_id in self.pending_goals:
                        del self.pending_goals[evt_id]
                else:
                    # Assist is missing initially. Buffer for 10-12 seconds to capture assist on next poll cycle.
                    if evt_id not in self.pending_goals:
                        self.pending_goals[evt_id] = {
                            "evt": evt,
                            "fixture": fixture,
                            "timestamp": now_ts
                        }
                    else:
                        prev_ts = self.pending_goals[evt_id]["timestamp"]
                        if now_ts - prev_ts >= 10.0:
                            # Waiting time passed and still no assist, post Goal without assist.
                            msg = formatter.format_goal(evt, fixture)
                            await self.broadcast_alert(msg, evt_id)
                            del self.pending_goals[evt_id]
            else:
                msg = None
                if evt_type == "Card":
                    msg = formatter.format_card(evt, fixture)
                elif evt_type == "subst":
                    msg = formatter.format_subst(evt, fixture)
                elif evt_type == "Var":
                    msg = formatter.format_var(evt, fixture)

                if msg:
                    await self.broadcast_alert(msg, evt_id)

    async def flush_pending_goals(self):
        """Flush any goals waiting for assist that have exceeded buffer time."""
        now_ts = asyncio.get_event_loop().time()
        expired_ids = []
        for evt_id, item in list(self.pending_goals.items()):
            if self.state_manager.is_processed(evt_id):
                expired_ids.append(evt_id)
                continue
            if now_ts - item["timestamp"] >= 10.0:
                msg = formatter.format_goal(item["evt"], item["fixture"])
                await self.broadcast_alert(msg, evt_id)
                expired_ids.append(evt_id)
        for eid in expired_ids:
            if eid in self.pending_goals:
                del self.pending_goals[eid]

    async def poll_live_fixtures(self) -> bool:
        """Poll live fixtures. Returns True if matches are currently live, False otherwise."""
        logger.info("Polling live fixtures...")
        fixtures = await self.api_client.get_live_fixtures(league_ids=TARGET_LEAGUES)
        
        current_live_ids: Set[int] = set()

        if fixtures:
            logger.info(f"Found {len(fixtures)} live fixture(s). Processing concurrently...")
            for f in fixtures:
                f_id = f['fixture']['id']
                current_live_ids.add(f_id)
                self.tracked_live_fixture_ids.add(f_id)

            # Concurrently process all currently live fixtures
            tasks = [self.process_single_fixture(f) for f in fixtures]
            await asyncio.gather(*tasks, return_exceptions=True)

        # Flush any pending goals whose buffer time expired
        await self.flush_pending_goals()

        # Detect fixtures that were live previously but just left live=all (Match Finished!)
        finished_candidates = self.tracked_live_fixture_ids - current_live_ids
        if finished_candidates:
            logger.info(f"Checking {len(finished_candidates)} recently finished match(es)...")
            for fix_id in list(finished_candidates):
                # Always discard from tracking set immediately to prevent infinite retry loops!
                self.tracked_live_fixture_ids.discard(fix_id)
                fix_data = await self.api_client.get_fixture_by_id(fix_id)
                if fix_data:
                    await self.process_single_fixture(fix_data, is_finished_check=True)

        return len(current_live_ids) > 0

    async def run(self):
        logger.info(f"Starting El Once Titular Automation Bot (Adaptive Polling: {LIVE_POLL_INTERVAL}s live / {IDLE_POLL_INTERVAL}s idle)...")
        await self.check_api_status()

        # Take a snapshot of currently live fixtures at startup to ignore all past events
        await self.snapshot_live_fixtures_on_startup()

        while True:
            try:
                # Poll live matches & events for live channel (@ElOnceTitular)
                has_live_matches = await self.poll_live_fixtures()
                
                # Check if API daily quota limit was reached
                if getattr(self.api_client, 'quota_exceeded', False):
                    logger.warning("API-Football daily request limit reached. Pausing polling for 5 minutes before retrying...")
                    await asyncio.sleep(300)
                    continue

                # Smart Adaptive Sleep: 15s when matches are live, 60s when no matches are live
                sleep_time = LIVE_POLL_INTERVAL if has_live_matches else IDLE_POLL_INTERVAL
                await asyncio.sleep(sleep_time)
                    
            except Exception as e:
                logger.error(f"Error in main polling loop: {e}", exc_info=True)
                await asyncio.sleep(LIVE_POLL_INTERVAL)

if __name__ == "__main__":
    bot = FootballBotEngine()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
