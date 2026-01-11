# Custom Code Server

A customized VS Code Server workbench image for Red Hat OpenShift AI.

## Overview

This image extends the RHOAI Code Server Data Science workbench with:

- Pre-configured Python interpreter settings
- Python debugger launch configuration
- Disabled telemetry and update checks
- Workspace trust prompts disabled
- Hidden dotfiles in file explorer

## Base Image

```
registry.redhat.io/rhoai/odh-workbench-codeserver-datascience-cpu-py312-rhel9
```

## Key Files

| File | Description |
|------|-------------|
| `run-code-server.sh` | Main startup script with VS Code configuration |
| `startup.sh` | Container entrypoint |
| `settings.json` | Default VS Code settings |
| `frozen-requirements.txt` | Pinned Python dependencies |

## Building Container

```bash
podman build -t custom-codeserver -f Containerfile .
```

## Ports

- **8787**: Code Server web interface
- Uses nginx and httpd for proxy/routing
