#!/bin/bash
# ============================================================
# V4 行政处罚案卷评查系统 - 回滚脚本
# 用法: bash rollback.sh [target_version]
#   不指定版本则回滚到上一个版本
# 示例: bash rollback.sh
#       bash rollback.sh v3.9.0
# ============================================================

set -euo pipefail

# ---- 配置 ----
readonly NAMESPACE="chatlaw"
readonly APP_NAME="v4-review"
readonly K8S_DIR="./k8s"
readonly PREVIOUS_VERSION_FILE="/tmp/v4-review-previous-version"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC}  $(date '+%Y-%m-%d %H:%M:%S') $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $(date '+%Y-%m-%d %H:%M:%S') $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*"; }

# ---- 确认操作 ----
confirm() {
    read -rp "$1 (y/N): " answer
    case "$answer" in
        [yY]|[yY][eE][sS]) return 0 ;;
        *) return 1 ;;
    esac
}

# ---- 获取当前版本 ----
get_current_version() {
    kubectl get deployment "$APP_NAME" -n "$NAMESPACE" \
        -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || echo "unknown"
}

# ---- 获取上一个版本 ----
get_previous_version() {
    if [[ -f "$PREVIOUS_VERSION_FILE" ]]; then
        cat "$PREVIOUS_VERSION_FILE"
    else
        echo ""
    fi
}

# ---- 获取部署历史 ----
get_deployment_history() {
    log_info "部署历史（最近 10 个 ReplicaSet）:"
    kubectl get rs -n "$NAMESPACE" -l app="$APP_NAME" \
        --sort-by='.metadata.creationTimestamp' \
        -o custom-columns='NAME:.metadata.name,IMAGE:.spec.template.spec.containers[0].image,REPLICAS:.spec.replicas,CREATED:.metadata.creationTimestamp' \
        | tail -10
}

# ---- 执行回滚 ----
do_rollback() {
    local target_image="$1"
    local target_version="$2"

    log_info "回滚目标: ${target_image}"

    # 方式一：使用 kubectl rollout undo（回滚到上一个版本）
    if [[ "$target_version" == "previous" ]]; then
        log_info "执行 kubectl rollout undo..."
        kubectl rollout undo deployment/"$APP_NAME" -n "$NAMESPACE"
    else
        # 方式二：指定镜像版本回滚
        log_info "更新镜像到: ${target_image}"
        kubectl set image deployment/"$APP_NAME" \
            "${APP_NAME}=${target_image}" -n "$NAMESPACE"
    fi

    # 等待回滚完成
    log_info "等待回滚完成..."
    if kubectl rollout status deployment/"$APP_NAME" -n "$NAMESPACE" --timeout=180s; then
        log_info "回滚成功"
    else
        log_error "回滚超时，请手动检查"
        exit 1
    fi
}

# ---- 回滚后验证 ----
post_rollback_verify() {
    log_info "执行回滚后验证..."

    local current_version
    current_version=$(get_current_version)
    log_info "当前版本: ${current_version}"

    # 检查 Pod 状态
    kubectl get pods -l app="$APP_NAME" -n "$NAMESPACE"

    # 检查健康状态
    local pod_name
    pod_name=$(kubectl get pods -l app="$APP_NAME" -n "$NAMESPACE" \
        -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [[ -n "$pod_name" ]]; then
        log_info "检查 Pod ${pod_name} 健康状态..."
        kubectl exec "$pod_name" -n "$NAMESPACE" -- curl -sf http://localhost:8000/health \
            && log_info "健康检查通过" \
            || log_warn "健康检查失败，请手动验证"
    fi

    log_info "回滚后验证完成"
}

# ---- 主流程 ----
main() {
    local target_version="${1:-previous}"

    echo "============================================"
    echo " V4 行政处罚案卷评查系统 - 版本回滚"
    echo " 时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================"
    echo ""

    # 显示当前状态
    local current_version
    current_version=$(get_current_version)
    log_info "当前版本: ${current_version}"

    # 确定回滚目标
    local target_image
    if [[ "$target_version" == "previous" ]]; then
        target_image=$(get_previous_version)
        if [[ -z "$target_image" || "$target_image" == "none" ]]; then
            log_error "无法获取上一个版本信息"
            log_info "使用 kubectl rollout undo 回滚到上一个 ReplicaSet..."
            get_deployment_history
        fi
    else
        target_image="chatlaw/${APP_NAME}:${target_version}"
    fi

    # 显示历史并确认
    get_deployment_history
    echo ""

    if [[ -n "$target_image" && "$target_image" != "none" ]]; then
        log_info "回滚方案: ${current_version} -> ${target_image}"
    else
        log_info "回滚方案: ${current_version} -> 上一个 ReplicaSet"
    fi

    if ! confirm "确认执行回滚？此操作将影响线上服务"; then
        log_info "回滚已取消"
        exit 0
    fi

    echo ""

    # 执行回滚
    do_rollback "$target_image" "$target_version"

    # 回滚后验证
    post_rollback_verify

    echo ""
    echo "============================================"
    log_info "回滚完成!"
    echo "============================================"
}

main "$@"
