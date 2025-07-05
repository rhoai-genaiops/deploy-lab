# Git Monitor for Model/Prompt Changes

A web-based monitoring system that tracks changes to model and prompt configurations in Git repositories.

## Features

- 🔍 **Real-time Git monitoring** - Continuously checks for new commits
- 📊 **Web dashboard** - Clean table view of all changes
- 🔐 **Authentication support** - Works with private repositories
- 🌐 **External repository support** - Monitor any Git repository
- 📈 **Historical tracking** - See all changes over time
- 🔄 **Auto-refresh** - Updates every 30 seconds (configurable)

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements-monitor.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your repository details
   ```

3. **Run the monitor:**
   ```bash
   python run_monitor.py
   ```

4. **Open your browser:**
   ```
   http://localhost:5000
   ```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GIT_REPO_URL` | Git repository URL | Current directory | No |
| `GIT_USERNAME` | Git username for authentication | - | For private repos |
| `GIT_PASSWORD` | Git password or personal access token | - | For private repos |
| `GIT_BRANCH` | Git branch to monitor | `main` | No |
| `MONITOR_INTERVAL` | Check interval in seconds | `30` | No |
| `FLASK_HOST` | Flask server host | `0.0.0.0` | No |
| `FLASK_PORT` | Flask server port | `5000` | No |
| `FLASK_DEBUG` | Enable Flask debug mode | `false` | No |

### Example Configurations

#### Local Repository (Current Directory)
```bash
# No configuration needed - uses current directory
python run_monitor.py
```

#### External Public Repository
```bash
export GIT_REPO_URL="https://github.com/username/repo.git"
export GIT_BRANCH="main"
python run_monitor.py
```

#### External Private Repository (GitHub)
```bash
export GIT_REPO_URL="https://github.com/username/private-repo.git"
export GIT_USERNAME="your-username"
export GIT_PASSWORD="ghp_your_personal_access_token"
export GIT_BRANCH="main"
python run_monitor.py
```

#### External Private Repository (GitLab)
```bash
export GIT_REPO_URL="https://gitlab.com/username/private-repo.git"
export GIT_USERNAME="your-username"
export GIT_PASSWORD="glpat-your_access_token"
python run_monitor.py
```

## Authentication

### GitHub Personal Access Token
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` permissions
3. Use the token as `GIT_PASSWORD`

### GitLab Personal Access Token
1. Go to GitLab Settings → Access Tokens
2. Create a token with `read_repository` scope
3. Use the token as `GIT_PASSWORD`

## Monitored Files

The system monitors these files for changes:
- `chart/values-test.yaml`
- `chart/values-prod.yaml`

## Expected File Structure

```yaml
# chart/values-test.yaml or chart/values-prod.yaml
LLAMA_STACK_URL: "http://llama-stack"
summarize:
  enabled: true
  model: llama32
  prompt: |
    Give me a good summary of the following text.
```

## Dashboard Features

- **Environment badges** - Distinguish between test and production
- **Model tracking** - See which models are being used
- **Prompt changes** - Full prompt text with hover expansion
- **Commit information** - Hash, date, and commit message
- **Status indicators** - Enabled/disabled status
- **Auto-refresh** - Automatic updates every 30 seconds
- **Manual refresh** - Force refresh button

## Troubleshooting

### Common Issues

1. **Authentication failures:**
   - Check username/password are correct
   - For GitHub, use Personal Access Token instead of password
   - Ensure token has correct permissions

2. **Repository not found:**
   - Verify the repository URL is correct
   - Check if repository is private and requires authentication

3. **No changes showing:**
   - Ensure the monitored files exist in the repository
   - Check the git history contains commits for those files
   - Verify the branch name is correct

### Logs

The application logs important information to the console:
- Repository cloning/pulling status
- Authentication attempts
- File parsing results
- Error messages

## Development

### Running in Development Mode

```bash
export FLASK_DEBUG=true
python run_monitor.py
```

### File Structure

```
.
├── git_monitor.py          # Main monitoring application
├── run_monitor.py          # Entry point with environment support
├── templates/
│   └── index.html         # Web dashboard template
├── requirements-monitor.txt # Python dependencies
├── .env.example           # Environment configuration example
└── README-monitor.md      # This file
```

## Security Notes

- Store credentials in environment variables, never in code
- Use Personal Access Tokens instead of passwords when possible
- Limit token permissions to minimum required (read-only)
- Consider using `.env` files for local development only
- For production, use proper secrets management