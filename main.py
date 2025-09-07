#!/usr/bin/env python3
"""
GitHub PR Monitor Service
Main entry point for the service that monitors GitHub PR merges and sends Discord notifications.
"""

from flask import Flask
from threading import Thread
import time
import logging
import sys
from config import Config
from github_monitor import GitHubMonitor
from discord_notifier import DiscordNotifier
from pr_tracker import PRTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('github_pr_monitor.log')
    ])

logger = logging.getLogger(__name__)

# Web server to keep Replit alive
app = Flask('')


@app.route('/')
def home():
    return "GitHub PR Monitor is running!"


def run_web():
    import os
    port = int(os.environ.get("PORT", 8080))  # use Render/Heroku port, fallback to 8080 locally
    app.run(host="0.0.0.0", port=port)


def main():
    """Main service loop"""
    logger.info("Starting GitHub PR Monitor Service")

    try:
        # Initialize configuration
        config = Config()
        config.validate()
        logger.info(f"Monitoring repository: {config.github_repo}")
        logger.info(f"Target branches: {', '.join(config.target_branches)}")
        logger.info(f"Polling interval: {config.polling_interval} seconds")

        # Initialize components
        github_monitor = GitHubMonitor(config.github_token, config.github_repo)
        discord_notifier = DiscordNotifier(config.discord_webhook_url)
        pr_tracker = PRTracker()

        logger.info("Service initialized successfully")

        # Main monitoring loop
        while True:
            try:
                logger.debug("Checking for new merged PRs...")

                # Check each target branch
                all_new_prs = []
                for branch in config.target_branches:
                    logger.debug(f"Checking branch: {branch}")

                    # Get merged PRs from the current branch
                    merged_prs = github_monitor.get_merged_prs(branch)

                    if merged_prs is None:
                        logger.warning(
                            f"Failed to fetch PRs for branch {branch}, skipping"
                        )
                        continue

                    # Filter out already seen PRs
                    for pr in merged_prs:
                        if not pr_tracker.has_seen_pr(pr['id']):
                            all_new_prs.append(pr)
                            pr_tracker.mark_pr_as_seen(pr['id'])

                if all_new_prs:
                    logger.info(
                        f"Found {len(all_new_prs)} new merged PR(s) across all branches"
                    )

                    # Send Discord notifications for new PRs
                    for pr in all_new_prs:
                        success = discord_notifier.send_pr_notification(pr)
                        if success:
                            logger.info(
                                f"Notification sent for PR #{pr['number']} (→ {pr['base_branch']}): {pr['title']}"
                            )
                        else:
                            logger.error(
                                f"Failed to send notification for PR #{pr['number']}"
                            )
                else:
                    logger.debug("No new merged PRs found across all branches")

            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}", exc_info=True)
                logger.info(
                    "Continuing service after error - waiting 60 seconds before retry..."
                )
                time.sleep(60)  # Wait before retrying to avoid rapid failures

            # Wait before next poll
            time.sleep(config.polling_interval)

    except Exception as e:
        logger.error(f"Fatal error during initialization: {str(e)}",
                     exc_info=True)
        sys.exit(1)

    logger.info("GitHub PR Monitor Service stopped")


if __name__ == "__main__":
    # Start web server in separate thread
    Thread(target=run_web).start()

    # Start your main GitHub monitor
    main()
