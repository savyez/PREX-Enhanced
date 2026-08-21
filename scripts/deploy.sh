#!/usr/bin/env bash
# =============================================================================
# PREX Production Deployment & Management Script
# =============================================================================
# Usage:
#   ./scripts/deploy.sh [deploy|rollback|healthcheck|status|logs|restart]
#
# Environment variables recognized:
#   BACKEND_IMAGE    : Fully qualified backend image (e.g., ghcr.io/savyez/prex-backend:latest)
#   FRONTEND_IMAGE   : Fully qualified frontend image (e.g., ghcr.io/savyez/prex-frontend:latest)
#   COMPOSE_FILE     : Docker Compose file to use (default: docker-compose.prod.yml)
#   ENV_FILE         : Environment file to use (default: .env.docker or .env)
# =============================================================================

set -eo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT_DIR}"

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
STATE_FILE="${ROOT_DIR}/.last_deploy_state"
ROLLBACK_FILE="${ROOT_DIR}/.rollback_state"

if [ -f "${ROOT_DIR}/.env.docker" ]; then
    ENV_FILE="${ROOT_DIR}/.env.docker"
elif [ -f "${ROOT_DIR}/.env" ]; then
    ENV_FILE="${ROOT_DIR}/.env"
else
    log_warning "No .env.docker or .env file found in ${ROOT_DIR}."
    ENV_FILE="${ROOT_DIR}/.env.docker"
fi

export COMPOSE_FILE

check_prerequisites() {
    log_info "Verifying deployment prerequisites..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH."
        exit 1
    fi

    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose v2 is required but not installed."
        exit 1
    fi

    if [ ! -f "${COMPOSE_FILE}" ]; then
        log_error "Compose file ${COMPOSE_FILE} not found in ${ROOT_DIR}."
        exit 1
    fi
}

check_health() {
    local attempts=30
    local delay=2
    local healthy=0

    log_info "Running post-deployment health check probes (Timeout: $((attempts * delay))s)..."

    for i in $(seq 1 ${attempts}); do
        HTTP_NGINX=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/healthz || curl -s -o /dev/null -w "%{http_code}" http://localhost/healthz || true)
        HTTP_API=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/api/v1/health/ || curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/v1/health/ || true)

        if [ "${HTTP_NGINX}" = "200" ] && [ "${HTTP_API}" = "200" ]; then
            log_success "All health checks passed on probe attempt ${i}! (Nginx: ${HTTP_NGINX}, API: ${HTTP_API})"
            healthy=1
            break
        elif [ "${HTTP_API}" = "200" ]; then
            log_success "Backend API is healthy on probe attempt ${i}! (API: ${HTTP_API})"
            healthy=1
            break
        else
            echo -e "  ⏳ Attempt ${i}/${attempts} - Nginx: ${HTTP_NGINX:-down}, API: ${HTTP_API:-down} (Retrying in ${delay}s...)"
            sleep ${delay}
        fi
    done

    if [ ${healthy} -ne 1 ]; then
        log_error "Health check failed after ${attempts} attempts."
        return 1
    fi
    return 0
}

deploy() {
    check_prerequisites

    log_info "Starting PREX deployment using ${COMPOSE_FILE}..."

    if [ -f "${STATE_FILE}" ]; then
        cp "${STATE_FILE}" "${ROLLBACK_FILE}"
    fi

    if [ -n "${BACKEND_IMAGE}" ] || [ -n "${FRONTEND_IMAGE}" ]; then
        echo "BACKEND_IMAGE=${BACKEND_IMAGE}" > "${STATE_FILE}"
        echo "FRONTEND_IMAGE=${FRONTEND_IMAGE}" >> "${STATE_FILE}"
    fi

    log_info "Pulling updated container images..."
    docker compose -f "${COMPOSE_FILE}" pull backend frontend celery_worker celery_beat || true

    log_info "Starting and checking database (PostgreSQL) and broker (Redis)..."
    docker compose -f "${COMPOSE_FILE}" up -d db redis

    log_info "Waiting for database ready status..."
    local db_ready=0
    for _ in $(seq 1 20); do
        if docker compose -f "${COMPOSE_FILE}" exec -T db pg_isready &> /dev/null; then
            db_ready=1
            break
        fi
        sleep 2
    done

    if [ ${db_ready} -ne 1 ]; then
        log_error "Database did not become ready in time."
        exit 1
    fi
    log_success "Database is ready."

    log_info "Applying database migrations..."
    docker compose -f "${COMPOSE_FILE}" run --rm backend python manage.py migrate --noinput

    log_info "Collecting Django static files..."
    docker compose -f "${COMPOSE_FILE}" run --rm backend python manage.py collectstatic --noinput

    log_info "Applying container updates with rolling recreate..."
    docker compose -f "${COMPOSE_FILE}" up -d --remove-orphans

    if check_health; then
        log_success "Deployment completed and verified successfully!"
        log_info "Pruning dangling docker images..."
        docker image prune -f || true
    else
        log_error "Health check failed! Automatically triggering rollback..."
        rollback
        exit 1
    fi
}

rollback() {
    log_warning "Initiating PREX rollback..."

    if [ -f "${ROLLBACK_FILE}" ]; then
        log_info "Restoring previous environment state from ${ROLLBACK_FILE}..."
        # shellcheck disable=SC1090
        source "${ROLLBACK_FILE}"
        export BACKEND_IMAGE FRONTEND_IMAGE
        
        docker compose -f "${COMPOSE_FILE}" up -d --remove-orphans
        log_warning "Containers recreated with previous image tags."
        
        if check_health; then
            log_success "Rollback successful: Services restored to healthy state."
            cp "${ROLLBACK_FILE}" "${STATE_FILE}"
        else
            log_error "Rollback health check also failed! Immediate operator inspection required."
            docker compose -f "${COMPOSE_FILE}" logs --tail 50 backend frontend
            exit 1
        fi
    else
        log_error "No rollback state file (${ROLLBACK_FILE}) found. Manual recovery required."
        exit 1
    fi
}

show_status() {
    check_prerequisites
    echo -e "${BOLD}${CYAN}================ PREX Container Status ================${NC}"
    docker compose -f "${COMPOSE_FILE}" ps
    echo ""
    echo -e "${BOLD}${CYAN}================ Health Check Status ===================${NC}"
    check_health || true
}

show_logs() {
    check_prerequisites
    docker compose -f "${COMPOSE_FILE}" logs -f --tail 100 "$@"
}

restart_services() {
    check_prerequisites
    log_info "Restarting PREX services..."
    docker compose -f "${COMPOSE_FILE}" restart
    check_health
}

COMMAND="${1:-deploy}"
shift || true

case "${COMMAND}" in
    deploy)
        deploy "$@"
        ;;
    rollback)
        rollback "$@"
        ;;
    healthcheck|check)
        check_health "$@"
        ;;
    status)
        show_status "$@"
        ;;
    logs)
        show_logs "$@"
        ;;
    restart)
        restart_services "$@"
        ;;
    migrate)
        check_prerequisites
        docker compose -f "${COMPOSE_FILE}" exec backend python manage.py migrate
        ;;
    collectstatic)
        check_prerequisites
        docker compose -f "${COMPOSE_FILE}" exec backend python manage.py collectstatic --noinput
        ;;
    help|--help|-h)
        echo "Usage: $0 [deploy|rollback|healthcheck|status|logs|restart|migrate|collectstatic]"
        ;;
    *)
        log_error "Unknown command: ${COMMAND}"
        echo "Usage: $0 [deploy|rollback|healthcheck|status|logs|restart|migrate|collectstatic]"
        exit 1
        ;;
esac
