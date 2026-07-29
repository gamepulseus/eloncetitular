import json
import logging
from pathlib import Path
from typing import Set
from config import STATE_FILE

logger = logging.getLogger("StateManager")

class StateManager:
    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self.processed_ids: Set[str] = set()
        self._load()

    def _load(self):
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.processed_ids = set(data.get("processed_ids", []))
                    logger.info(f"Loaded {len(self.processed_ids)} processed events from state.")
            except Exception as e:
                logger.error(f"Error loading state file: {e}")
                self.processed_ids = set()
        else:
            self.processed_ids = set()

    def save(self):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump({"processed_ids": list(self.processed_ids)}, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving state file: {e}")

    def is_processed(self, event_id: str) -> bool:
        return event_id in self.processed_ids

    def mark_processed(self, event_id: str):
        self.processed_ids.add(event_id)
        self.save()
