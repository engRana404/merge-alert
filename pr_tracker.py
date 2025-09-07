"""
PR tracking module to avoid duplicate notifications
"""

import json
import logging
import os
from typing import Set
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PRTracker:
    """Tracks seen PRs to avoid sending duplicate notifications"""

    def __init__(self, storage_file: str = 'seen_prs.json'):
        self.storage_file = storage_file
        self.seen_prs: Set[int] = set()
        self.load_seen_prs()

    def load_seen_prs(self):
        """Load seen PR IDs from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)

                # Load PR IDs and check expiry
                current_time = datetime.utcnow().replace(
                    tzinfo=None)  # Make timezone-naive
                cutoff_time = current_time - timedelta(
                    days=30)  # Keep data for 30 days

                valid_prs = set()
                for entry in data.get('prs', []):
                    if isinstance(entry, dict):
                        pr_id = entry.get('id')
                        timestamp_str = entry.get('timestamp')

                        if pr_id and timestamp_str:
                            try:
                                # Convert to timezone-naive for comparison
                                timestamp = datetime.fromisoformat(
                                    timestamp_str.replace(
                                        'Z', '+00:00')).replace(tzinfo=None)
                                if timestamp >= cutoff_time:
                                    valid_prs.add(pr_id)
                            except ValueError:
                                # Skip invalid timestamp
                                continue
                    elif isinstance(entry, int):
                        # Legacy format - keep all IDs for backward compatibility
                        valid_prs.add(entry)

                self.seen_prs = valid_prs
                logger.info(
                    f"Loaded {len(self.seen_prs)} seen PR IDs from storage")

                # Save cleaned up data back if we removed expired entries
                if len(valid_prs) != len(data.get('prs', [])):
                    self.save_seen_prs()
            else:
                logger.info(
                    "No existing PR tracking file found, starting fresh")

        except Exception as e:
            logger.error(f"Error loading seen PRs: {str(e)}")
            logger.info("Starting with empty PR tracking")
            self.seen_prs = set()

    def save_seen_prs(self):
        """Save seen PR IDs to storage file"""
        try:
            current_time = datetime.utcnow().isoformat() + 'Z'

            # Convert set to list of dictionaries with timestamps
            prs_data = [{
                'id': pr_id,
                'timestamp': current_time
            } for pr_id in self.seen_prs]

            data = {
                'version': '1.0',
                'last_updated': current_time,
                'prs': prs_data
            }

            # Write to temporary file first, then rename for atomic operation
            temp_file = f"{self.storage_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)

            os.rename(temp_file, self.storage_file)
            logger.debug(f"Saved {len(self.seen_prs)} seen PR IDs to storage")

        except Exception as e:
            logger.error(f"Error saving seen PRs: {str(e)}")
            # Clean up temp file if it exists
            temp_file = f"{self.storage_file}.tmp"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    def has_seen_pr(self, pr_id: int) -> bool:
        """Check if a PR has been seen before"""
        return pr_id in self.seen_prs

    def mark_pr_as_seen(self, pr_id: int):
        """Mark a PR as seen and save to storage"""
        if pr_id not in self.seen_prs:
            self.seen_prs.add(pr_id)
            self.save_seen_prs()
            logger.debug(f"Marked PR {pr_id} as seen")

    def get_seen_count(self) -> int:
        """Get the number of tracked PRs"""
        return len(self.seen_prs)

    def cleanup_old_entries(self, days: int = 30):
        """Remove entries older than specified days"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)

                current_time = datetime.utcnow().replace(tzinfo=None)
                cutoff_time = current_time - timedelta(days=days)

                valid_prs = set()
                for entry in data.get('prs', []):
                    if isinstance(entry, dict):
                        timestamp_str = entry.get('timestamp')
                        if timestamp_str:
                            try:
                                timestamp = datetime.fromisoformat(
                                    timestamp_str.replace(
                                        'Z', '+00:00')).replace(tzinfo=None)
                                if timestamp >= cutoff_time:
                                    valid_prs.add(entry['id'])
                            except ValueError:
                                continue
                    elif isinstance(entry, int):
                        # Keep legacy entries for safety
                        valid_prs.add(entry)

                old_count = len(self.seen_prs)
                self.seen_prs = valid_prs
                self.save_seen_prs()

                removed = old_count - len(self.seen_prs)
                if removed > 0:
                    logger.info(f"Cleaned up {removed} old PR entries")

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
