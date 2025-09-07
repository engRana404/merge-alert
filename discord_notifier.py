"""
Discord webhook client for sending PR merge notifications
"""

import requests
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DiscordNotifier:
    """Discord webhook client for sending notifications"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'GitHub-PR-Monitor/1.0'
        })

    def send_pr_notification(self, pr_data: Dict) -> bool:
        """
        Send a Discord notification for a merged PR
        
        Args:
            pr_data: Dictionary containing PR information
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            embed = self._create_pr_embed(pr_data)

            payload = {
                'embeds': [embed],
                'username':
                'GitHub PR Monitor',
                'avatar_url':
                'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'
            }

            logger.debug(
                f"Sending Discord notification for PR #{pr_data['number']}")

            response = self.session.post(self.webhook_url,
                                         json=payload,
                                         timeout=30)

            if response.status_code in [200, 204]:
                logger.info(
                    f"Discord notification sent successfully for PR #{pr_data['number']}"
                )
                return True
            else:
                logger.error(
                    f"Discord webhook failed with status {response.status_code}: {response.text}"
                )
                return False

        except requests.exceptions.Timeout:
            logger.error("Discord webhook request timed out")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to Discord webhook")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Discord webhook request failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error sending Discord notification: {str(e)}",
                exc_info=True)
            return False

    def _create_pr_embed(self, pr_data: Dict) -> Dict:
        """Create a Discord embed for the PR notification"""

        # Parse merged_at timestamp
        merged_at = datetime.fromisoformat(pr_data['merged_at'].replace(
            'Z', '+00:00'))

        # Create embed color based on PR status (green for merged)
        embed_color = 0x28a745  # Green color for merged PRs

        # Truncate title and body if too long
        title = pr_data['title']
        if len(title) > 256:
            title = title[:253] + "..."

        description = pr_data.get('body') or 'No description provided.'

        if len(description) > 400:
            description = description[:397] + "..."

        embed = {
            'title':
            f"🎉 PR #{pr_data['number']} merged to {pr_data['base_branch']}",
            'description':
            f"**{title}**\n\n{description}",
            'url':
            pr_data['html_url'],
            'color':
            embed_color,
            'timestamp':
            pr_data['merged_at'],
            'author': {
                'name': pr_data['user']['login'],
                'icon_url': pr_data['user']['avatar_url'],
                'url': f"https://github.com/{pr_data['user']['login']}"
            },
            'fields': [{
                'name':
                '📊 Changes',
                'value':
                f"**+{pr_data.get('additions', 0)}** / **-{pr_data.get('deletions', 0)}** lines\n"
                f"**{pr_data.get('changed_files', 0)}** files changed",
                'inline':
                True
            }, {
                'name': '🔀 Branches',
                'value':
                f"**From:** `{pr_data['head_branch']}`\n**To:** `{pr_data['base_branch']}`",
                'inline': True
            }, {
                'name': '⏰ Merged',
                'value': f"<t:{int(merged_at.timestamp())}:R>",
                'inline': True
            }],
            'footer': {
                'text':
                f"GitHub • {pr_data.get('commits', 0)} commit(s)",
                'icon_url':
                'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'
            }
        }

        return embed

    def send_test_message(self) -> bool:
        """Send a test message to verify webhook connectivity"""
        try:
            payload = {
                'content':
                '🧪 GitHub PR Monitor test message - service is running!',
                'username':
                'GitHub PR Monitor',
                'avatar_url':
                'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'
            }

            response = self.session.post(self.webhook_url,
                                         json=payload,
                                         timeout=10)

            if response.status_code in [200, 204]:
                logger.info("Discord test message sent successfully")
                return True
            else:
                logger.error(
                    f"Discord test message failed with status {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"Failed to send Discord test message: {str(e)}")
            return False
