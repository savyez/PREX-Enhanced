# PREX Continuous Deployment (CD) & Production Guide

This guide provides an end-to-end overview of the **Continuous Deployment (CD)** pipeline, server provisioning, container registry integration, automated database migrations, zero-downtime rolling updates, and rollback strategies for **PREX**.

---

## 1. Architecture Overview

The PREX Continuous Deployment pipeline uses **GitHub Actions**, **GitHub Container Registry (GHCR)**, **Docker Compose**, and **Nginx Reverse Proxy** to deploy immutable production containers to target servers over secure SSH.

```mermaid
flowchart TD
    subgraph GitHub ["GitHub Actions (.github/workflows/cd.yml)"]
        A[Git Push to main/master or Release Tag] --> B[Build Multi-Arch Docker Images]
        B --> C[Push Images to GHCR Registry]
    end

    subgraph GHCR ["GitHub Container Registry (ghcr.io)"]
        C --> D1["ghcr.io/.../prex-backend:sha-xyz"]
        C --> D2["ghcr.io/.../prex-frontend:sha-xyz"]
    end

    subgraph Server ["Target Production Server (/opt/prex)"]
        E[SSH Deploy Execution] --> F[Pull Latest Images from GHCR]
        F --> G[Run Migrations & Collectstatic]
        G --> H[Zero-Downtime Container Recreate]
        H --> I{Health Check Probes}
        I -->|Healthy 200 OK| J[Prune Dangling Images & Complete]
        I -->|Unhealthy| K[Automated Rollback to Previous Image Tag]
    end

    D1 -.-> F
    D2 -.-> F
    E -. SSH Commands .-> Server
```

---

## 2. GitHub Actions Workflows

The repository contains two distinct workflows under `.github/workflows/`:

| Workflow | File | Trigger | Purpose |
| :--- | :--- | :--- | :--- |
| **Continuous Integration (CI)** | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Pull requests & branch pushes | Validates backend checks, database migrations, Python tests, ESLint, and Vite frontend build. |
| **Continuous Deployment (CD)** | [`.github/workflows/cd.yml`](.github/workflows/cd.yml) | Pushes to `main`/`master`, git release tags (`v*.*.*`), or `workflow_dispatch` | Pure deployment pipeline: builds & pushes Docker images to GHCR, deploys via SSH, validates health, and emits deployment summaries. |

### CD Manual Trigger Options (`workflow_dispatch`)

You can manually trigger a deployment at any time from the **Actions** tab on GitHub:
- **`environment`**: Target environment (`production` or `staging`).
- **`deploy_target`**: Component selection (`all`, `backend`, `frontend`).
- **`run_migrations`**: Automatically apply Django database migrations (`true`/`false`).

---

## 3. GitHub Secrets Configuration

To enable automated SSH deployments, configure the following secrets in your GitHub repository (**Settings > Secrets and variables > Actions**):

| Secret Name | Description | Example / Format |
| :--- | :--- | :--- |
| `SSH_HOST` | Public IP address or domain of the deployment server | `203.0.113.45` or `api.yourdomain.com` |
| `SSH_USER` | SSH username with Docker permissions | `ubuntu` or `deploy` |
| `SSH_KEY` | Private SSH Key (ed25519 or RSA) corresponding to server's `~/.ssh/authorized_keys` | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `SSH_PORT` | SSH daemon port (defaults to `22` if omitted) | `22` |
| `DEPLOY_PATH` | Target directory on the server where PREX is installed | `/opt/prex` (default) |

---

## 4. Server Provisioning (One-Time Setup)

Run the automated setup script on a fresh Ubuntu 22.04 or 24.04 LTS server:

```bash
# SSH into your server
ssh ubuntu@your-server-ip

# Run the automated setup script
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/savyez/PREX-Enhanced/main/scripts/server-setup.sh)"
```

---

## 5. Deployment Script & Commands

The project includes an idempotent deployment manager script: [`scripts/deploy.sh`](scripts/deploy.sh).

```bash
# Full deployment (pulls images, runs migrations, collectstatic, restarts containers, verifies health)
./scripts/deploy.sh deploy

# Rollback to the previous deployment if an issue is discovered
./scripts/deploy.sh rollback

# Inspect health endpoints
./scripts/deploy.sh healthcheck

# Check running container statuses
./scripts/deploy.sh status

# Follow application logs
./scripts/deploy.sh logs

# Run ad-hoc migrations
./scripts/deploy.sh migrate
```

---

## 6. Automated Health Probes & Rollback Mechanism

Every deployment triggers an automated health verification phase:

1. **Nginx Liveness Probe (`/healthz`)**: Confirms that Nginx reverse proxy is actively listening and responsive.
2. **Backend API Health Check (`/api/v1/health/`)**: Confirms Django WSGI is running and answering requests with HTTP 200 OK (`{"status": "ok"}`).
3. **Retry Strategy**: 30 attempts with 2-second intervals (60s total timeout).
4. **Automatic Rollback**: If health checks fail after 30 attempts:
   - The deployment script captures recent container logs.
   - It restores `.rollback_state` containing previous healthy image tags.
   - It recreates containers with previous tags to restore uptime immediately.
   - It exits with code `1`, alerting the GitHub Actions workflow.
