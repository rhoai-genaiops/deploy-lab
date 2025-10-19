# RDU - Redwood Digital University Website

A modern, responsive website for Redwood Digital University featuring their four undergraduate programs: Biotechnology, Computer Engineering, Liberal Arts, and Mechanical Engineering.

## Project Structure

```
rdu-website/
├── src/                    # Website source files
│   ├── index.html         # Main HTML file
│   ├── styles.css         # CSS styling
│   └── script.js          # JavaScript functionality
├── docker/                # Docker configuration
│   ├── Dockerfile         # Container image definition
│   └── nginx.conf         # Nginx web server configuration
├── k8s/                   # Kubernetes manifests
│   ├── deployment.yaml    # Kubernetes deployment
│   ├── service.yaml       # Service and OpenShift route
│   ├── hpa.yaml          # Horizontal Pod Autoscaler
│   └── kustomization.yaml # Kustomize configuration
├── helm/                  # Helm chart
│   └── rdu-website/       # Helm chart for deployment
└── README.md             # This file
```

## Features

### Website Features
- **Responsive Design**: Mobile-friendly layout that works on all devices
- **Academic Programs**: Showcases all four 240 ECTS programs
- **Interactive Elements**: Smooth scrolling, animations, and hover effects
- **Professional Styling**: University-themed color scheme with redwood brown
- **Performance Optimized**: Fast loading with optimized assets

### Technical Features
- **Secure Container**: Runs as non-root user on port 8080
- **Health Checks**: Built-in health endpoint for monitoring
- **Security Headers**: Comprehensive security headers in nginx
- **High Availability**: 3 replicas with auto-scaling
- **Production Ready**: Includes monitoring, logging, and observability

## Academic Programs

### 1. Bachelor of Science in Biotechnology (240 ECTS)
- Lab-intensive, industry-aligned curriculum
- Molecular & cell biology, bioprocess engineering
- Bioinformatics, regulatory affairs, and quality systems
- 8 semesters with integrated research experiences

### 2. Bachelor of Science in Computer Engineering (240 ECTS)
- Hardware, software, and systems engineering
- Embedded systems, digital design, AI/ML fundamentals
- Cybersecurity, VLSI/FPGA, and IoT applications
- Strong lab and project components

### 3. Bachelor of Arts in Liberal Arts (240 ECTS)
- Interdisciplinary, writing-intensive program
- Humanities, social sciences, arts, quantitative reasoning
- Critical inquiry, global citizenship, digital fluency
- Research excellence with senior thesis/capstone

### 4. Bachelor of Science in Mechanical Engineering (240 ECTS)
- Comprehensive practice-heavy curriculum
- Mechanics, materials, thermofluids, manufacturing
- Sustainable energy, robotics, advanced materials
- Design & CAD/CAE, dynamics & control systems

## Quick Start

### Using Docker

```bash
# Build the image
docker build -t rdu-website ./docker

# Run the container
docker run -p 8080:8080 rdu-website

# Access the website
open http://localhost:8080
```

### Using Kubernetes

```bash
# Apply the manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=rdu-website

# Port forward to access locally
kubectl port-forward svc/rdu-website-service 8080:80
```

### Using Helm

```bash
# Install the chart
helm install rdu-website ./helm/rdu-website

# Upgrade the chart
helm upgrade rdu-website ./helm/rdu-website

# Check status
helm status rdu-website

# Uninstall
helm uninstall rdu-website
```

### Using OpenShift

```bash
# Create project
oc new-project rdu-website

# Apply OpenShift manifests
oc apply -f k8s/

# Get route URL
oc get route rdu-website-route
```

## Configuration

### Helm Values

Key configuration options in `helm/rdu-website/values.yaml`:

```yaml
# Image configuration
image:
  registry: image-registry.openshift-image-registry.svc:5000
  repository: rdu-website/rdu-website
  tag: latest

# Scaling configuration
deployment:
  replicaCount: 3

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10

# OpenShift Route
route:
  enabled: true
  host: rdu-website.apps.cluster.local
```

### Environment Variables

- `NGINX_PORT`: Web server port (default: 8080)
- `NGINX_HOST`: Bind address (default: 0.0.0.0)

## Security

### Container Security
- Runs as non-root user (UID 1001)
- Read-only root filesystem
- Dropped all capabilities
- Security context constraints compliant

### Network Security
- Network policies for ingress/egress control
- TLS termination at the route/ingress
- Security headers (CSP, HSTS, etc.)

### Pod Security
- Pod Security Standards compliant
- Resource limits and requests
- Health checks and monitoring

## Monitoring

### Health Checks
- **Liveness Probe**: `/health` endpoint
- **Readiness Probe**: `/health` endpoint  
- **Startup Probe**: Automatic detection

### Metrics
- Prometheus scraping enabled
- CPU and memory utilization
- Request count and response times

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking and alerting

## Development

### Local Development

```bash
# Serve files locally
python3 -m http.server 8080 --directory src/

# Or use Node.js
npx http-server src/ -p 8080
```

### Building Images

```bash
# Build with Docker
docker build -t rdu-website:dev ./docker

# Build with Podman
podman build -t rdu-website:dev ./docker

# Build with OpenShift BuildConfig
oc new-build --strategy docker --binary --name rdu-website
oc start-build rdu-website --from-dir=./docker --follow
```

## Deployment Environments

### Development
```bash
helm install rdu-website-dev ./helm/rdu-website \
  --set image.tag=dev \
  --set route.host=rdu-dev.apps.cluster.local
```

### Staging
```bash
helm install rdu-website-staging ./helm/rdu-website \
  --set image.tag=staging \
  --set route.host=rdu-staging.apps.cluster.local \
  --set deployment.replicaCount=2
```

### Production
```bash
helm install rdu-website-prod ./helm/rdu-website \
  --set image.tag=v1.0.0 \
  --set route.host=rdu.university.edu \
  --set autoscaling.enabled=true
```

## Support

For technical support, contact:
- **Email**: it@rdu.edu
- **Documentation**: https://rdu.university.edu/it/docs
- **Status Page**: https://status.rdu.university.edu

## License

Copyright © 2024 Redwood Digital University. All rights reserved.

This project is proprietary software owned by Redwood Digital University. Unauthorized use, reproduction, or distribution is prohibited.

---

**Redwood Digital University** - Excellence in Innovation
📍 Redwood Valley, CA | 📞 (555) 123-4567 | ✉️ info@rdu.edu