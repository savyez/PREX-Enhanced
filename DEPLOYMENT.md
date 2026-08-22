# PREX Continuous Deployment (CD) & Production Guide

This guide provides an end-to-end overview of the **Continuous Deployment (CD)** pipeline, server provisioning, container registry integration, automated database migrations, zero-downtime rolling updates, SSL/TLS certificate configuration, and rollback strategies for **PREX**.

---

## 1. Architecture Overview

The PREX Continuous Deployment pipeline uses **GitHub Actions**, **GitHub Container Registry (GHCR)**, **Docker Compose**, and an **Nginx Reverse Proxy** to deploy immutable production containers to target servers over secure SSH.

```mermaid
flowchart TD
    subgraph GitHub ["GitHub Actions (.github/workflows/cd.yml)"]
        A["Git Push (main/master) or Release Tag"] --> B["Build Multi-Arch Docker Images"]
        B --> C["Push Images to GHCR Registry"]
    end

    subgraph GHCR ["GitHub Container Registry (ghcr.io)"]
        C --> D1["ghcr.io/.../prex-backend:sha-xyz"]
        C --> D2["ghcr.io/.../prex-frontend:sha-xyz"]
    end

    subgraph Server ["Target Production Server (/opt/prex)"]
        E["SSH Deploy Execution"] --> F["Pull Latest Images from GHCR"]
        F --> G["Run Migrations & Collectstatic"]
        G --> H["Zero-Downtime Container Recreate"]
        H --> I{"Health Check Probes"}
        I -->|"Healthy 200 OK"| J["Prune Dangling Images & Complete"]
        I -->|"Unhealthy"| K["Automated Rollback to Previous Image Tag"]
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
| **Continuous Integration (CI)** | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Pull requests & branch pushes | Validates backend checks, database migrations, Python tests (37 tests), ESLint, and Vite frontend build. |
| **Continuous Deployment (CD)** | [`.github/workflows/cd.yml`](.github/workflows/cd.yml) | Pushes to `main`/`master`, git release tags (`v*.*.*`), or `workflow_dispatch` | Pure deployment pipeline: builds & pushes Docker images to GHCR, deploys via SSH, validates health, and emits deployment summaries. |

### CD Manual Trigger Options (`workflow_dispatch`)

You can manually trigger a deployment at any time from the **Actions** tab on GitHub:
- **`environment`**: Target environment (`production` or `staging`).
- **`deploy_target`**: Component selection (`all`, `backend`, `frontend`).
- **`run_migrations`**: Automatically apply Django database migrations (`true`/`false`).

---

## 3. GitHub Secrets & Variables Configuration

To enable automated SSH deployments, configure the following secrets in your GitHub repository (**Settings > Secrets and variables > Actions**):

### Repository Secrets (Under the "Secrets" Tab)

> [!IMPORTANT]
> Ensure you add these under the **Secrets** tab (not the Variables tab). Secrets are referenced in the workflow as `${{ secrets.NAME }}`.

| Secret Name | Required | Description | Example / Format |
| :--- | :---: | :--- | :--- |
| **`SSH_HOST`** | **Yes** | Public IP address or domain of the deployment server | `203.0.113.45` or `prex.duckdns.org` |
| **`SSH_USER`** | **Yes** | SSH username with Docker & sudo permissions | `ubuntu` or `deploy` |
| **`SSH_KEY`** | **Yes** | Private SSH Key corresponding to server's `~/.ssh/authorized_keys` | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| **`SSH_PORT`** | No | SSH daemon port (defaults to `22` if omitted) | `22` |
| **`DEPLOY_PATH`** | No | Target directory on the server where PREX is installed | `/opt/prex` (default) |

### Repository Variables (Under the "Variables" Tab)

| Variable Name | Required | Description | Default |
| :--- | :---: | :--- | :--- |
| **`APP_URL`** | No | Canonical public URL of the web application | `https://prex.duckdns.org` |

---

## 4. Troubleshooting CD Deployment Issues

### Common Error: `Error: missing server host`

If your CD job fails at the step `Deploy to Remote Host via SSH` (`appleboy/ssh-action`) with the message `Error: missing server host`, verify the following:

1. **Secret vs. Variable Misplacement:**
   Ensure `SSH_HOST` is created under **Secrets** (accessible via `${{ secrets.SSH_HOST }}`), not **Variables** (`${{ vars.SSH_HOST }}`).
2. **Environment Scoping (`environment: production`):**
   The deploy job specifies `environment: production`. If a `production` environment exists under **Settings > Environments**, verify that `SSH_HOST`, `SSH_USER`, and `SSH_KEY` are either added directly to **Environment secrets** within `production`, or defined globally as **Repository secrets** with no conflicting blank environment entries.
3. **Exact Secret Naming:**
   Secret names are case-sensitive. Verify there are no typos (e.g. use `SSH_HOST`, not `HOST`, `SERVER_HOST`, or `SSH_IP`).
4. **SSH Key Format:**
   Ensure `SSH_KEY` includes the full private key headers:
   ```text
   -----BEGIN OPENSSH PRIVATE KEY-----
   ... (key body) ...
   -----END OPENSSH PRIVATE KEY-----
   ```

---

## 5. Server Provisioning (One-Time Setup)

Run the automated setup script on a fresh Ubuntu 22.04 or 24.04 LTS server:

```bash
# SSH into your server
ssh ubuntu@your-server-ip

# Run the automated setup script
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/savyez/PREX-Enhanced/main/scripts/server-setup.sh)"
```

The setup script automatically:
- Installs Docker Engine, Docker Compose plugin, Git, curl, and UFW firewall.
- Configures firewall rules (allows ports `22`, `80`, `443`).
- Creates the deployment directory `/opt/prex` with appropriate user permissions.
- Sets up systemd service unit for automated container restarts on system boot.

---

## 6. Deployment Manager Script & Commands

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

## 7. Automated Health Probes & Rollback Mechanism

Every deployment triggers an automated health verification phase:

1. **Nginx Liveness Probe (`/healthz`)**: Confirms that the Nginx reverse proxy is actively listening and responsive.
2. **Backend API Health Check (`/api/v1/health/`)**: Confirms Django WSGI / Gunicorn is running and answering requests with HTTP 200 OK (`{"status": "ok"}`).
3. **Retry Strategy**: 30 attempts with 2-second intervals (60s total timeout).
4. **Automatic Rollback**: If health checks fail after 30 attempts:
   - The deployment script captures recent container logs.
   - It restores `.rollback_state` containing previous healthy image tags.
   - It recreates containers with previous tags to restore uptime immediately.
   - It exits with code `1`, alerting the GitHub Actions workflow.

---

## 8. SSL / TLS Certificate Setup (Let's Encrypt for prex.duckdns.org)

For production HTTPS termination on `prex.duckdns.org`:

### 1. Point DuckDNS Domain to Server IP
Ensure your DuckDNS domain (`prex.duckdns.org`) is pointing to your server's public IP address.

### 2. Issue SSL Certificate via Certbot
```bash
# Install Certbot
sudo apt-get update && sudo apt-get install -y certbot

# Issue certificate (ensure port 80 is temporarily available or use webroot)
sudo certbot certonly --standalone -d prex.duckdns.org
```

### 3. Mount Certificate Files to Nginx Directory
```bash
sudo mkdir -p /etc/nginx/ssl/live
sudo ln -sf /etc/letsencrypt/live/prex.duckdns.org/fullchain.pem /etc/nginx/ssl/live/fullchain.pem
sudo ln -sf /etc/letsencrypt/live/prex.duckdns.org/privkey.pem /etc/nginx/ssl/live/privkey.pem
```

### 4. Enable Nginx SSL Configuration
In `docker-compose.prod.yml`, switch the Nginx configuration volume mount to use `nginx.ssl.conf`:
```yaml
frontend:
  volumes:
    - ./frontend/nginx.ssl.conf:/etc/nginx/conf.d/default.conf:ro
    - /etc/nginx/ssl/live:/etc/nginx/ssl/live:ro
```
Restart the stack:
```bash
docker compose -f docker-compose.prod.yml up -d
```
