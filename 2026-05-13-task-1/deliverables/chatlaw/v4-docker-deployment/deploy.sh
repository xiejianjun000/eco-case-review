#!/bin/bash
# ============================================================
# V4 行政处罚案卷评查系统 - 生产部署脚本
# 用法: bash deploy.sh [version]
# 示例: bash deploy.sh v4.0.0
# ============================================================

set -euo pipefail

# ---- 配置 ----
readonly NAMESPACE="chatlaw"
readonly APP_NAME="v4-review"
readonly REGISTRY="chatlaw"
readonly K8S_DIR="./k8s"
readonly MAX_ROLLBACK_VERSIONS=5

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC}  $(date '+%Y-%m-%d %H:%M:%S') $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $(date '+%Y-%m-%d %H:%M:%S') $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*"; }

# ---- 参数解析 ----
VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
    log_error "缺少版本号参数"
    echo "用法: bash deploy.sh <version>"
    echo "示例: bash deploy.sh v4.0.0"
    exit 1
fi

IMAGE_TAG="${REGISTRY}/${APP_NAME}:${VERSION}"
PREVIOUS_VERSION_FILE="/tmp/v4-review-previous-version"

# ---- 前置检查 ----
check_prerequisites() {
    log_info "执行前置检查..."

    # 检查 kubectl
    if ! command -v kubectl &>/dev/null; then
        log_error "kubectl 未安装"
        exit 1
    fi

    # 检查集群连通性
    if ! kubectl cluster-info &>/dev/null; then
        log_error "无法连接 Kubernetes 集群"
        exit 1
    fi

    # 检查 namespace
    if ! kubectl get namespace "$NAMESPACE" &>/dev/null 2>&1; then
        log_info "创建 namespace: ${NAMESPACE}"
        kubectl create namespace "$NAMESPACE"
    fi

    # 检查 secrets 是否已替换占位符
    if kubectl get secret v4-review-secrets -n "$NAMESPACE" -o jsonpath='{.data.SECRET_KEY}' 2>/dev/null | grep -q "CHANGE_ME"; then
        log_error "Secrets 中仍包含占位符，请先配置真实的密钥"
        exit 1
    fi

    log_info "前置检查通过"
}

# ---- 镜像安全扫描 ----
security_scan() {
    log_info "执行镜像安全扫描..."

    if ! command -v trivy &>/dev/null; then
        log_warn "Trivy 未安装，跳过安全扫描"
        return 0
    fi

    if trivy image --severity CRITICAL,HIGH --exit-code 1 --quiet "$IMAGE_TAG"; then
        log_info "安全扫描通过"
    else
        log_error "安全扫描发现高危漏洞，部署中止"
        exit 1
    fi
}

# ---- 备份当前版本 ----
backup_current_version() {
    log_info "备份当前版本信息..."

    local current_image
    current_image=$(kubectl get deployment "$APP_NAME" -n "$NAMESPACE" \
        -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || echo "none")

    if [[ "$current_image" != "none" ]]; then
        echo "$current_image" > "$PREVIOUS_VERSION_FILE"
        log_info "当前版本: ${current_image}"
    else
        echo "none" > "$PREVIOUS_VERSION_FILE"
        log_info "首次部署，无当前版本需要备份"
    fi
}

# ---- 部署 Kubernetes 资源 ----
deploy_k8s_resources() {
    log_info "部署 Kubernetes 资源..."

    # 按顺序部署
    local resources=("configmap" "secrets" "service" "deployment" "ingress")

    for resource in "${resources[@]}"; do
        local file="${K8S_DIR}/${resource}.yaml"
        if [[ -f "$file" ]]; then
            log_info "应用 ${resource}..."
            kubectl apply -f "$file" -n "$NAMESPACE"
        else
            log_warn "文件不存在: ${file}"
        fi
    done
}

# ---- 等待部署就绪 ----
wait_for_ready() {
    log_info "等待部署就绪..."

    local timeout=300
    local interval=10
    local elapsed=0

    while [[ $elapsed -lt $timeout ]]; do
        local ready
        ready=$(kubectl get deployment "$APP_NAME" -n "$NAMESPACE" \
            -o jsonpath='{.status.availableReplicas}' 2>/dev/null || echo "0")
        local desired
        desired=$(kubectl get deployment "$APP_NAME" -n "$NAMESPACE" \
            -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "1")

        if [[ "$ready" == "$desired" ]]; then
            log_info "部署就绪: ${ready}/${desired} 副本运行中"
            return 0
        fi

        log_info "等待就绪... (${ready}/${desired}) [${elapsed}s/${timeout}s]"
        sleep "$interval"
        elapsed=$((elapsed + interval))
    done

    log_error "部署超时 (${timeout}s)"
    return 1
}

# ---- 部署后验证 ----
post_deploy_verify() {
    log_info "执行部署后验证..."

    # 检查 Pod 状态
    kubectl get pods -l app="$APP_NAME" -n "$NAMESPACE"

    # 检查 Service Endpoints
    local endpoints
    endpoints=$(kubectl get endpoints "$APP_NAME" -n "$NAMESPACE" \
        -o jsonpath='{.subsets[0].addresses[*].ip}' 2>/dev/null || echo "")
    if [[ -n "$endpoints" ]]; then
        log_info "Service Endpoints: ${endpoints}"
    else
        log_warn "Service Endpoints 为空"
    fi

    # 检查最近事件
    log_info "最近事件:"
    kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -10

    log_info "部署后验证完成"
}

# ---- 清理旧版本镜像（保留最近 N 个） ----
cleanup_old_versions() {
    log_info "清理旧版本 (保留最近 ${MAX_ROLLBACK_VERSIONS} 个)..."

    # 这里可以集成 registry API 清理旧镜像
    log_info "旧版本清理完成（如需清理 registry 镜像，请手动执行）"
}

# ---- 主流程 ----
main() {
    echo "============================================"
    echo " V4 行政处罚案卷评查系统 - 生产部署"
    echo " 版本: ${VERSION}"
    echo " 时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================"
    echo ""

    check_prerequisites
    security_scan
    backup_current_version
    deploy_k8s_resources
    wait_for_ready
    post_deploy_verify
    cleanup_old_versions

    echo ""
    echo "============================================"
    log_info "部署完成! 版本: ${VERSION}"
    echo "============================================"
}

main "$@"
