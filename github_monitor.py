"""
GitHub API client for monitoring pull request merges
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class GitHubMonitor:
    """GitHub API client for monitoring pull requests"""
    
    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-PR-Monitor/1.0'
        })
    
    def get_merged_prs(self, branch: str, hours_back: int = 24) -> Optional[List[Dict]]:
        """
        Get recently merged pull requests for a specific branch
        
        Args:
            branch: Target branch name (e.g., 'staging')
            hours_back: How many hours back to look for merged PRs
            
        Returns:
            List of PR dictionaries or None if API call failed
        """
        try:
            # Calculate the since timestamp
            since = datetime.utcnow() - timedelta(hours=hours_back)
            since_iso = since.isoformat() + 'Z'
            
            # GitHub API endpoint for pull requests
            url = f"{self.base_url}/repos/{self.repo}/pulls"
            
            params = {
                'state': 'closed',
                'base': branch,
                'sort': 'updated',
                'direction': 'desc',
                'per_page': 100
            }
            
            logger.debug(f"Fetching PRs from {url} with params: {params}")
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                prs = response.json()
                
                # Filter for actually merged PRs within the time window
                merged_prs = []
                for pr in prs:
                    if (pr.get('merged_at') and 
                        pr.get('merged_at') >= since_iso and
                        pr.get('base', {}).get('ref') == branch):
                        
                        # Get detailed PR information with statistics
                        detailed_pr = self._get_pr_details(pr['number'])
                        
                        # Extract relevant PR information
                        pr_data = {
                            'id': pr['id'],
                            'number': pr['number'],
                            'title': pr['title'],
                            'body': pr.get('body', ''),
                            'user': {
                                'login': pr['user']['login'],
                                'avatar_url': pr['user']['avatar_url']
                            },
                            'merged_at': pr['merged_at'],
                            'html_url': pr['html_url'],
                            'base_branch': pr['base']['ref'],
                            'head_branch': pr['head']['ref'],
                            'commits': detailed_pr.get('commits', 0),
                            'additions': detailed_pr.get('additions', 0),
                            'deletions': detailed_pr.get('deletions', 0),
                            'changed_files': detailed_pr.get('changed_files', 0)
                        }
                        merged_prs.append(pr_data)
                
                logger.debug(f"Found {len(merged_prs)} merged PRs in the last {hours_back} hours")
                return merged_prs
                
            elif response.status_code == 401:
                logger.error("GitHub API authentication failed. Check your GITHUB_TOKEN.")
                return None
            elif response.status_code == 403:
                if 'rate limit' in response.text.lower():
                    logger.error("GitHub API rate limit exceeded. Consider increasing polling interval.")
                else:
                    logger.error("GitHub API access forbidden. Check repository permissions.")
                return None
            elif response.status_code == 404:
                logger.error(f"Repository {self.repo} not found or not accessible.")
                return None
            else:
                logger.error(f"GitHub API request failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("GitHub API request timed out")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to GitHub API")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching PRs: {str(e)}", exc_info=True)
            return None
    
    def _get_pr_details(self, pr_number: int) -> Dict:
        """
        Get detailed PR information including commit statistics
        
        Args:
            pr_number: Pull request number
            
        Returns:
            Dictionary with detailed PR information
        """
        try:
            url = f"{self.base_url}/repos/{self.repo}/pulls/{pr_number}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to fetch details for PR #{pr_number}: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.warning(f"Error fetching PR #{pr_number} details: {str(e)}")
            return {}
    
    def get_rate_limit_info(self) -> Optional[Dict]:
        """Get GitHub API rate limit information"""
        try:
            url = f"{self.base_url}/rate_limit"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get rate limit info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting rate limit info: {str(e)}")
            return None
