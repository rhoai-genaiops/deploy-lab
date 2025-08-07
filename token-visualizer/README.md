# vLLM Token Visualizer

A modern, real-time web application for visualizing token consumption from vLLM servers.

## Features

- 🚀 Real-time token consumption monitoring
- 🎨 Modern dark theme with smooth animations
- ⚡ Configurable refresh intervals
- 🔧 Multiple environment configuration options
- 🐳 Containerized deployment ready
- 📱 Mobile responsive design

## Quick Start

### Using the Container (Recommended)

1. **Build and run with the provided script:**
   ```bash
   ./build-and-run.sh
   ```

2. **Or manually with podman/docker:**
   ```bash
   # Build the image
   podman build -t vllm-token-visualizer -f Containerfile .
   
   # Run the container
   podman run -d \
     --name token-visualizer \
     -p 3000:8080 \
     --env VLLM_SERVER_URL="http://your-vllm-server:8000" \
     vllm-token-visualizer
   ```

3. **Access the application:**
   - Open http://localhost:3000 in your browser

### Direct HTML Usage

1. Open `token-visualizer.html` directly in your browser
2. Configure the server URL in the settings panel

## Configuration

### Environment Variables

The application supports multiple ways to configure the vLLM server URL:

| Method | Example | Priority |
|--------|---------|----------|
| **URL Parameters** | `?serverUrl=http://server:8000` | Highest |
| **Container Environment** | `VLLM_SERVER_URL=http://server:8000` | High |
| **Meta Tags** | `<meta name="vllm-server-url" content="...">` | Medium |
| **JavaScript Global** | `window.VLLM_SERVER_URL = "..."` | Low |
| **UI Input** | Settings panel in the app | Lowest |

### Available Environment Variables

- `VLLM_SERVER_URL`: vLLM server URL (default: `http://localhost:8000`)
- `VLLM_REFRESH_INTERVAL`: Refresh interval in milliseconds (default: `2000`)

## Container Management

### Start/Stop/Remove
```bash
# Stop the container
podman stop token-visualizer

# Start the container
podman start token-visualizer

# View logs
podman logs -f token-visualizer

# Remove the container
podman rm token-visualizer
```

### Custom Configuration
```bash
# Run with custom vLLM server URL
VLLM_SERVER_URL="http://my-vllm-server:8000" ./build-and-run.sh

# Run with custom refresh interval (1 second)
VLLM_REFRESH_INTERVAL="1000" ./build-and-run.sh
```

## How It Works

The application fetches metrics from your vLLM server's `/metrics` endpoint and specifically tracks the `vllm:request_params_max_tokens_sum` metric to display total token consumption with smooth animations.

## Requirements

- vLLM server with metrics endpoint enabled
- Podman or Docker for containerized deployment
- Modern web browser with JavaScript enabled

## Troubleshooting

1. **Connection issues**: Ensure your vLLM server's `/metrics` endpoint is accessible
2. **CORS errors**: The container includes CORS headers for cross-origin requests
3. **Port conflicts**: Change the port mapping if 3000 is already in use: `-p 8080:8080`