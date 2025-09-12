# Git Monitor for Model/Prompt Changes

A web-based monitoring system that tracks changes to model and prompt configurations in Git repositories, with integrated S3 evaluation results and user-specific configurations.

## Features

- 🔍 **Real-time Git monitoring** - Continuously checks for new commits
- 📊 **Interactive web dashboard** - Modern card-based view with collapsible details
- 🔐 **Authentication support** - Works with private repositories
- 🌐 **External repository support** - Monitor any Git repository
- 📈 **Historical tracking** - See all changes over time with diff visualization
- 🔄 **Auto-refresh** - Updates every 30 seconds (configurable)
- 👥 **Multi-user support** - User-specific configurations and isolated monitoring
- 🗂️ **S3 integration** - Automatic detection and linking of evaluation results
- 🌍 **Multi-cluster support** - Configurable cluster domains for different environments
- 🎯 **Advanced filtering** - Filter by environment, use case, and status
- 📱 **Responsive design** - Works on desktop and mobile devices

## Quick Start

### Option 1: Standard Configuration (Environment Variables)

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
   http://localhost:5001
   ```

### Option 2: User-Specific URLs (Recommended for Multi-User)

1. **Install dependencies and run:**
   ```bash
   pip install -r requirements-monitor.txt
   python run_monitor.py
   ```

2. **Access user-specific URLs:**
   ```
   # For user1 on a specific cluster
   http://localhost:5001/user1/apps.cluster-domain.example.com
   
   # For user2 on the same cluster
   http://localhost:5001/user2/apps.cluster-domain.example.com
   
   # Using legacy format (uses default cluster)
   http://localhost:5001/user1
   ```

## Configuration

### Environment Variables (Standard Mode)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GIT_REPO_URL` | Git repository URL | Current directory | No |
| `GIT_USERNAME` | Git username for authentication | - | For private repos |
| `GIT_PASSWORD` | Git password or personal access token | - | For private repos |
| `GIT_BRANCH` | Git branch to monitor | `main` | No |
| `MONITOR_INTERVAL` | Check interval in seconds | `30` | No |
| `FLASK_HOST` | Flask server host | `0.0.0.0` | No |
| `FLASK_PORT` | Flask server port | `5001` | No |
| `FLASK_DEBUG` | Enable Flask debug mode | `false` | No |

### S3 Configuration (For Evaluation Results)

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `S3_ENDPOINT` | MinIO/S3 API endpoint | `https://minio-api.example.com` | For S3 features |
| `S3_ACCESS_KEY` | S3 access key | `your-access-key` | For S3 features |
| `S3_SECRET_KEY` | S3 secret key | `your-secret-key` | For S3 features |
| `S3_BUCKET_NAME` | S3 bucket name | `results` | No (defaults to 'results') |
| `S3_UI_URL` | MinIO UI URL | `https://minio-ui.example.com` | For result links |
| `S3_REFRESH_INTERVAL` | S3 refresh interval in seconds | `60` | No |

### User-Specific Configuration (Automatic)

When using user-specific URLs, the system automatically configures:

- **Git Repository**: `https://gitea-gitea.{cluster_domain}/{user}/canopy-be.git`
- **Git Credentials**: Username = `{user}`, Password = `thisisthepassword`
- **S3 Endpoint**: `https://minio-api-{user}-toolings.{cluster_domain}`
- **S3 Credentials**: Access Key = `{user}`, Secret Key = `thisisthepassword`
- **S3 UI**: `https://minio-ui-{user}-toolings.{cluster_domain}`

## URL Patterns

### User-Specific URLs

```
# New cluster-aware format
http://localhost:5001/user<N>/<cluster-domain>

# Examples:
http://localhost:5001/user1/apps.cluster-gm86c.gm86c.sandbox1062.opentlc.com
http://localhost:5001/user2/apps.another-cluster.example.com

# Legacy format (uses default cluster)
http://localhost:5001/user<N>

# Examples:
http://localhost:5001/user1
http://localhost:5001/user2
```

### API Endpoints

```
# Standard API endpoints
GET  /api/changes                 - Get all changes
POST /api/refresh                 - Refresh data

# User-specific API endpoints
GET  /user<N>/<cluster>/api/changes     - Get user-specific changes
POST /user<N>/<cluster>/api/refresh     - Refresh user-specific data
GET  /user<N>/<cluster>/api/s3-debug    - Debug S3 connection
POST /user<N>/<cluster>/api/s3-refresh  - Force S3 refresh

# Legacy user endpoints
GET  /user<N>/api/changes         - Get user changes (default cluster)
POST /user<N>/api/refresh         - Refresh user data (default cluster)
GET  /user<N>/api/s3-debug        - Debug S3 (default cluster)
POST /user<N>/api/s3-refresh      - Force S3 refresh (default cluster)
```

## Example Configurations

### Standard Mode - External Private Repository
```bash
export GIT_REPO_URL="https://gitea-gitea.apps.cluster.example.com/user1/canopy-be.git"
export GIT_USERNAME="user1"
export GIT_PASSWORD="thisisthepassword"
export GIT_BRANCH="main"

# S3 Configuration
export S3_ENDPOINT="https://minio-api-user1-toolings.apps.cluster.example.com"
export S3_ACCESS_KEY="user1"
export S3_SECRET_KEY="thisisthepassword"
export S3_BUCKET_NAME="results"
export S3_UI_URL="https://minio-ui-user1-toolings.apps.cluster.example.com"

python run_monitor.py
```

### User-Specific Mode (No Configuration Needed)
```bash
# Just run the application
python run_monitor.py

# Access user-specific URLs in browser:
# http://localhost:5001/user1/apps.cluster.example.com
# http://localhost:5001/user2/apps.cluster.example.com
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

### Gitea Access Token
1. Go to Gitea Settings → Applications → Access Tokens
2. Generate a new token with repository permissions
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
  temperature: 0.7
  top_k: 50
  top_p: 0.9
  max_tokens: 150
  prompt: |
    Give me a good summary of the following text.
    Be concise and informative.

translate:
  enabled: false
  model: llama32
  prompt: |
    Translate the following text to Spanish.
```

## S3 Integration

### Evaluation Results Detection

The system automatically detects evaluation results stored in S3 with the pattern:
```
{commit_hash}/{usecase}_results.html
```

Examples:
- `abc1234/summarize_results.html`
- `def5678/translate_results.html`

### S3 Features

- **Automatic Detection**: Checks for evaluation results during git history scanning
- **Real-time Updates**: Periodic refresh to catch newly uploaded results
- **Direct Links**: Click "View Results" to open evaluation reports in MinIO UI
- **Status Indicators**: Visual indicators showing which changes have evaluation results
- **Manual Refresh**: Force refresh S3 status via API endpoints

## Dashboard Features

### Modern Interface
- **Card-based Layout**: Clean, modern card design with hover effects
- **Collapsible Details**: Click headers to expand/collapse change details
- **Environment Badges**: Color-coded badges for test/production environments
- **Status Indicators**: Visual indicators for enabled/disabled prompts

### Advanced Filtering
- **Environment Filter**: Show all, test only, or production only
- **Use Case Filter**: Filter by specific use cases (summarize, translate, etc.)
- **Dynamic Filters**: Filter options update based on available data

### Rich Information Display
- **Commit Details**: Full commit hash, message, author, and date
- **Model Parameters**: Temperature, top-k, top-p, max tokens
- **Prompt Comparison**: Side-by-side diff view showing changes
- **File Paths**: Source file information for each change

### S3 Integration UI
- **Result Status**: Clear indication of evaluation result availability
- **Direct Links**: One-click access to evaluation reports
- **Status Refresh**: Manual refresh buttons for S3 status updates

## Troubleshooting

### Common Issues

1. **No cards showing in UI:**
   - Check browser console for JavaScript errors
   - Verify API endpoints are responding (check Network tab)
   - Ensure git repository has the monitored files with commit history

2. **S3 evaluation results not showing:**
   - Use S3 debug endpoint: `/user1/cluster.example.com/api/s3-debug`
   - Check S3 credentials and endpoint configuration
   - Verify file naming pattern: `{commit_hash}/{usecase}_results.html`
   - Use manual S3 refresh: `/user1/cluster.example.com/api/s3-refresh`

3. **Authentication failures:**
   - Check username/password are correct
   - For GitHub, use Personal Access Token instead of password
   - Ensure token has correct permissions
   - Verify repository URL format

4. **Git clone failures:**
   - Check repository URL accessibility
   - Verify authentication credentials
   - Ensure branch exists in repository

### Debug Endpoints

```bash
# Debug S3 connection
curl http://localhost:5001/user1/cluster.example.com/api/s3-debug

# Force S3 refresh
curl -X POST http://localhost:5001/user1/cluster.example.com/api/s3-refresh

# Manual data refresh
curl -X POST http://localhost:5001/user1/cluster.example.com/api/refresh
```

### Logs

The application logs important information to the console:
- Repository cloning/pulling status
- S3 client initialization
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
├── git_monitor.py              # Main monitoring application
├── run_monitor.py              # Entry point with environment support
├── templates/
│   └── index.html             # Web dashboard template
├── requirements-monitor.txt    # Python dependencies
├── .env.example               # Environment configuration example
└── README-monitor.md          # This file
```

### Key Components

- **GitMonitor Class**: Core monitoring logic with S3 integration
- **User Configuration**: Template-based user-specific configurations
- **Flask Routes**: RESTful API endpoints for data access
- **Frontend**: Modern JavaScript-powered dashboard with real-time updates

## Multi-User Architecture

### User Isolation
- Each user gets dedicated monitoring instances
- Separate git repositories per user
- Isolated S3 storage per user
- Independent configuration management

### Cluster Support
- Dynamic cluster domain configuration
- Support for multiple OpenShift/Kubernetes clusters
- Flexible URL patterns for different environments

### Scalability
- Background monitoring threads per user
- Efficient resource management
- Configurable refresh intervals
- Memory-efficient change tracking

## Security Notes

- Store credentials in environment variables, never in code
- Use Personal Access Tokens instead of passwords when possible
- Limit token permissions to minimum required (read-only)
- Consider using `.env` files for local development only
- For production, use proper secrets management
- S3 SSL verification disabled for self-signed certificates (MinIO)
- User-specific configurations prevent cross-user data access

## API Reference

### GET /api/changes
Returns array of all changes with S3 evaluation status.

### POST /api/refresh
Triggers git pull and history rescan, returns refresh status.

### GET /user{N}/{cluster}/api/changes
Returns changes for specific user and cluster.

### GET /user{N}/{cluster}/api/s3-debug
Returns S3 configuration and connectivity status for debugging.

### POST /user{N}/{cluster}/api/s3-refresh
Forces immediate S3 status refresh for all changes.

All API responses include:
- Change metadata (commit, author, date)
- Model configuration (model, temperature, tokens, etc.)
- S3 evaluation status and URLs
- Environment and use case information