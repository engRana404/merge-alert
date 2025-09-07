"""
Configuration module for GitHub PR Monitor Service
Handles environment variable loading and validation.
"""

import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration class that loads and validates environment variables"""
    
    def __init__(self):
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        # GitHub configuration
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.github_repo = os.getenv('GITHUB_REPO', '')
        
        # Support multiple target branches
        target_branches_str = os.getenv('TARGET_BRANCHES', os.getenv('TARGET_BRANCH', 'staging'))
        self.target_branches = [branch.strip() for branch in target_branches_str.split(',')]
        
        # Backward compatibility
        self.target_branch = self.target_branches[0] if self.target_branches else 'staging'
        
        # Discord configuration
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')
        
        # Service configuration
        self.polling_interval = int(os.getenv('POLLING_INTERVAL', '300'))  # 5 minutes default
        self.max_prs_per_request = int(os.getenv('MAX_PRS_PER_REQUEST', '100'))
        
        # Logging configuration
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.log_level = getattr(logging, log_level, logging.INFO)
    
    def validate(self):
        """Validate that all required configuration is present"""
        errors = []
        
        if not self.github_token:
            errors.append("GITHUB_TOKEN environment variable is required")
        
        if not self.github_repo:
            errors.append("GITHUB_REPO environment variable is required (format: owner/repo)")
        
        if not self.discord_webhook_url:
            errors.append("DISCORD_WEBHOOK_URL environment variable is required")
        
        if '/' not in self.github_repo:
            errors.append("GITHUB_REPO must be in format 'owner/repository'")
        
        if self.polling_interval < 60:
            errors.append("POLLING_INTERVAL must be at least 60 seconds to respect GitHub API rate limits")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Configuration validation passed")
    
    def __str__(self):
        """String representation of config (without sensitive data)"""
        return f"""Config:
  GitHub Repo: {self.github_repo}
  Target Branches: {', '.join(self.target_branches)}
  Polling Interval: {self.polling_interval}s
  Max PRs per request: {self.max_prs_per_request}
  Log Level: {logging.getLevelName(self.log_level)}
"""
