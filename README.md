# GenAIOps Lab Deployment

Infrastructure-as-code for deploying a multi-tenant GenAIOps learning environment on OpenShift.

## Overview

This repository provides a complete deployment solution for the AI501 GenAIOps lab environment. It enables instructors to rapidly provision a multi-tenant AI/ML lab where students can experiment with Large Language Models, prompt engineering, model optimization, and AI governance.

## Prerequisites

- OpenShift 4.119+ cluster with cluster-admin access
- Helm 3.x installed
- `oc` CLI configured and authenticated
- (Optional) AWS credentials for GPU machine provisioning

### GPU Requirements

This lab requires **3 GPU nodes** with two different taints:

| Component | GPU Count | Instance Type | Taint |
|-----------|-----------|---------------|-------|
| Docling Serve | 1 | g4dn (T4) | `nvidia.com/gpu=g4dn` |
| Llama 3.2 (cloud-model) | 1 | g5 (A10G) | `nvidia.com/gpu=g5` |
| Llama 3.2 FP8 (quantized-model) | 1 | g5 (A10G) | `nvidia.com/gpu=g5` |

If you have different taints, make sure you update the necessary template for the deployments' tolerations.

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd deploy-lab
   ```

2. **Configure your deployment** (Required)

   Edit `student-content/values.yaml` before running the installation:
   ```yaml
   cluster_domain: apps.your-cluster.example.com  # Your OpenShift apps domain
   attendees: 20                                   # Number of students to create
   ```

   To find your cluster domain:
   ```bash
   oc get ingresses.config.openshift.io cluster -o jsonpath='{.spec.domain}'
   ```

3. **Run the installation**
   ```bash
   ./install.sh
   ```

## Configuration

Edit `student-content/values.yaml` before installation:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `cluster_domain` | OpenShift apps domain (e.g., `apps.mycluster.example.com`) | `apps.example.com` |
| `modelName` | Default LLM model name | `llama32` |
| `attendees` | Number of student environments to create | `20` |

## Repository Structure

```
deploy-lab/
├── install.sh                 # Main deployment script
├── operators/                 # Helm chart: OpenShift operators
├── toolings/                  # Helm chart: shared infrastructure
├── student-content/           # Helm chart: student environments
│   ├── values.yaml           # Configuration values
│   └── templates/            # Kubernetes manifests
│       ├── tinyllama/        # TinyLlama model serving
│       ├── cloud-model/      # Larger model serving
│       ├── exercise-app/     # Learning portal
│       ├── gradio/           # Interactive LLM demos
│       ├── canopy-board/     # Gamification dashboard
│       ├── argocd-instance/  # Per-user GitOps
│       └── ...
├── custom-codeserver/         # Custom workbench image
├── exercise-app/              # FastAPI exercise portal
├── gradio-app/                # Gradio LLM interfaces
├── canopy-board/              # Gamification system
├── user-signup-app/           # Student registration
├── prompt-tracker/            # Git monitoring dashboard
└── rdu-website/               # Demo marketing site
```

## Components

### Operators

Installs required OpenShift operators:
- Red Hat OpenShift AI (RHOAI)
- OpenShift Pipelines (Tekton)
- OpenShift GitOps (ArgoCD)
- NVIDIA GPU Operator
- Node Feature Discovery

### Toolings

Deploys shared infrastructure:
- MinIO (S3-compatible storage)
- TrustyAI (AI explainability)
- Observability stack (Prometheus, Grafana, Tempo)
- Custom workbench templates

### Student Content

Per-student resources:
- ArgoCD instance for GitOps workflows
- Data Science project workspace
- Access to shared LLM models
- Interactive learning applications

## Applications

| Application | Description | Path |
|-------------|-------------|------|
| Exercise Portal | FastAPI gateway to learning modules | `exercise-app/` |
| Gradio App | Interactive LLM experimentation | `gradio-app/` |
| Canopy Board | Gamification with leaderboards | `canopy-board/` |
| User Signup | Student registration system | `user-signup-app/` |
| Prompt Tracker | Git-based prompt versioning | `prompt-tracker/` |

## Model Serving

Pre-configured model deployments using KServe and vLLM:

- **TinyLlama 1.1B**: CPU-optimized for basic inference
- **Llama 3.2**: Full-featured model for production use
- **Quantized Models**: FP8 compressed for efficiency

## Post-Installation

After running `install.sh`:

1. **Verify operators are ready**:
   ```bash
   oc get csv -n openshift-operators
   ```

2. **Check student namespaces**:
   ```bash
   oc get namespaces | grep user
   ```

3. **Access the signup app** to distribute credentials to students

4. **Monitor ArgoCD** for GitOps sync status:
   ```bash
   oc get applications -A
   ```

### GPU Provisioning (AWS)

For GPU workloads, use the machine provisioning script:
```bash
./machineset.sh
```
Supports: T4, A10G, A100, H100, L40 instances

## Troubleshooting

### Check Helm releases
```bash
helm list -n ai501
```

### View pod status
```bash
oc get pods -n ai501
```

