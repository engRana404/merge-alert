# GitHub PR Monitor Service

A Python service that monitors GitHub pull request merges and sends real-time notifications to Discord via webhooks.

## Features

- 🔄 **Continuous Monitoring**: Polls GitHub API at configurable intervals
- 🎯 **Branch-Specific**: Monitor specific branches (default: staging)
- 📱 **Rich Discord Notifications**: Beautiful embed notifications with PR details
- 🚫 **Duplicate Prevention**: Tracks seen PRs to avoid spam notifications
- 📊 **Comprehensive Logging**: File and console logging with configurable levels
- ⚡ **Error Recovery**: Graceful error handling with automatic retries

## Setup Instructions

### 1. Environment Variables

Create a `.env` file with the following variables:

```bash
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=owner/repository-name
TARGET_BRANCHES=staging,main  # Multiple branches supported
# Or use single branch: TARGET_BRANCH=staging

# Discord Configuration
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your/webhook/url

# Service Configuration (Optional)
POLLING_INTERVAL=300          # 5 minutes default
MAX_PRS_PER_REQUEST=100      
LOG_LEVEL=INFO
```

### 2. GitHub Token Setup

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select the following scopes:
   - `repo` (Full control of private repositories) - **Required**
   - `public_repo` (Access public repositories) - **Required**
4. For private repositories like `Fledge-Health/app`, ensure the token has access to the organization
5. Copy the token and add it to your environment variables

### 3. Discord Webhook Setup

1. Go to your Discord server
2. Navigate to Server Settings → Integrations → Webhooks
3. Click "New Webhook"
4. Choose the channel where you want notifications
5. Copy the webhook URL and add it to your environment variables

### 4. Run the Service

```bash
# Install dependencies
pip install requests python-dotenv

# Run the service
python main.py
```

## Repository Access Issues

If you see "Repository not found or not accessible" errors:

1. **Check Repository Name**: Ensure `GITHUB_REPO` is in exact format: `owner/repository`
2. **Verify Token Permissions**: The GitHub token must have access to the repository
3. **Private Repository Access**: For private repos, the token must belong to a user with repo access
4. **Organization Repositories**: For organization repos, the token may need organization permissions

## Example Discord Notification

The service sends rich embed notifications that include:
- PR title and description
- Author information with avatar
- Branch information (from/to)
- Code change statistics (+/- lines, files changed)
- Direct link to the merged PR
- Timestamp of the merge

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `POLLING_INTERVAL` | 300 | Seconds between GitHub API checks |
| `TARGET_BRANCHES` | staging | Comma-separated list of branches to monitor |
| `TARGET_BRANCH` | staging | Single branch (for backward compatibility) |
| `MAX_PRS_PER_REQUEST` | 100 | Maximum PRs to fetch per API call |
| `LOG_LEVEL` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Project Structure

```
├── main.py              # Main service entry point
├── config.py            # Configuration management
├── github_monitor.py    # GitHub API client
├── discord_notifier.py  # Discord webhook client
├── pr_tracker.py        # Duplicate prevention tracking
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Troubleshooting

### Common Issues

1. **"Configuration validation failed"**
   - Ensure all required environment variables are set
   - Check `.env` file format and variable names

2. **"Repository not found or not accessible"**
   - Verify GitHub token has repository access
   - Check repository name format (`owner/repo`)
   - For private repos, ensure token belongs to authorized user

3. **"Discord webhook failed"**
   - Verify webhook URL is correct and active
   - Check Discord channel permissions

4. **"GitHub API rate limit exceeded"**
   - Increase `POLLING_INTERVAL` to reduce API calls
   - Check rate limit with GitHub token

### Logs

The service creates detailed logs in:
- Console output (real-time)
- `github_pr_monitor.log` file

Set `LOG_LEVEL=DEBUG` for more detailed troubleshooting information.

## Author

### **Rana Gamal**  
- 🌐 [LinkedIn](https://www.linkedin.com/in/rana-gamal-daif)
- 💻 [GitHub](https://github.com/engRana404)
- ✉️ [Email](mailto:RanaGamalDaif@gmail.com) 