#!/bin/bash
# 允许应用运行的脚本（双击运行）

cd "$(dirname "$0")"

APP_PATH="dist/智能视频下载工具.app"

if [ ! -d "$APP_PATH" ]; then
    echo "错误：找不到应用程序"
    echo "请确保在正确的目录运行此脚本"
    read -p "按回车键退出..."
    exit 1
fi

echo "====================================="
echo "   智能视频下载工具 - 权限修复"
echo "====================================="
echo ""
echo "此脚本将修复应用的运行权限"
echo "需要输入您的管理员密码"
echo ""

# 移除隔离标记
echo "1. 移除隔离标记..."
xattr -dr com.apple.quarantine "$APP_PATH"

# 重新签名
echo "2. 重新签名应用..."
codesign --force --deep --sign - "$APP_PATH"

# 添加到Gatekeeper白名单
echo "3. 添加到系统白名单（需要管理员权限）..."
sudo spctl --add "$APP_PATH"
sudo spctl --master-disable

echo ""
echo "====================================="
echo "修复完成！"
echo ""
echo "现在请尝试："
echo "1. 直接双击打开应用"
echo "2. 如果还是不行，右键点击应用 -> 选择'打开'"
echo "====================================="
echo ""
read -p "按回车键退出..."