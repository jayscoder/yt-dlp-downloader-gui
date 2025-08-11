#!/bin/bash
# 用于其他脚本加载环境变量的辅助脚本

# 加载.env文件
load_env() {
    if [ -f .env ]; then
        # 导出.env中的变量，忽略注释和空行
        set -a
        source <(grep -v '^#' .env | grep -v '^$')
        set +a
        return 0
    else
        echo "警告：未找到 .env 文件"
        echo "使用 .env.example 中的默认值"
        return 1
    fi
}

# 验证必需的环境变量
check_env() {
    local missing=0
    
    if [ -z "$DEVELOPER_ID" ] || [[ "$DEVELOPER_ID" == *"Your Name"* ]]; then
        echo "❌ DEVELOPER_ID 未配置"
        missing=1
    fi
    
    if [ -z "$APPLE_ID" ] || [[ "$APPLE_ID" == *"example.com"* ]]; then
        echo "❌ APPLE_ID 未配置"
        missing=1
    fi
    
    if [ -z "$APP_PASSWORD" ] || [[ "$APP_PASSWORD" == "xxxx-xxxx-xxxx-xxxx" ]]; then
        echo "❌ APP_PASSWORD 未配置"
        missing=1
    fi
    
    if [ -z "$TEAM_ID" ] || [[ "$TEAM_ID" == "XXXXXXXXXX" ]]; then
        echo "❌ TEAM_ID 未配置"
        missing=1
    fi
    
    if [ $missing -eq 1 ]; then
        echo ""
        echo "请编辑 .env 文件并填入您的Apple开发者信息"
        echo "参考 setup_notarization.md 获取详细说明"
        return 1
    fi
    
    echo "✅ 所有环境变量已配置"
    return 0
}

# 如果直接运行此脚本，显示当前配置状态
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    echo "===== 环境变量配置检查 ====="
    echo ""
    
    if load_env; then
        echo "已加载 .env 文件"
        echo ""
        echo "当前配置："
        echo "DEVELOPER_ID: ${DEVELOPER_ID:0:30}..."
        echo "APPLE_ID: ${APPLE_ID}"
        echo "APP_PASSWORD: ****-****-****-****"
        echo "TEAM_ID: ${TEAM_ID}"
        echo "APP_NAME: ${APP_NAME}"
        echo "BUNDLE_ID: ${BUNDLE_ID}"
        echo ""
        check_env
    else
        echo ""
        echo "请执行以下步骤："
        echo "1. cp .env.example .env"
        echo "2. 编辑 .env 文件，填入您的信息"
        echo "3. 再次运行此脚本验证配置"
    fi
fi