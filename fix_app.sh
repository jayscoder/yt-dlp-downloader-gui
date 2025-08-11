#!/bin/bash
# 修复应用程序权限和属性的脚本

APP_PATH="dist/智能视频下载工具.app"

if [ ! -d "$APP_PATH" ]; then
    echo "错误：找不到应用程序 $APP_PATH"
    exit 1
fi

echo "正在修复应用程序..."

# 1. 移除所有扩展属性
echo "移除扩展属性..."
xattr -cr "$APP_PATH"

# 2. 修复权限
echo "修复权限..."
chmod -R 755 "$APP_PATH"

# 3. 重新签名（使用ad-hoc签名）
echo "重新签名应用..."
codesign --force --deep --sign - "$APP_PATH"

# 4. 验证签名
echo "验证签名..."
codesign --verify --verbose "$APP_PATH"

# 5. 检查签名详情
echo ""
echo "签名详情："
codesign -dvv "$APP_PATH" 2>&1 | grep -E "Signature|Authority|TeamIdentifier|Flags"

# 6. 手动允许应用运行（需要管理员权限）
echo ""
echo "允许应用通过Gatekeeper..."
sudo spctl --add "$APP_PATH"
sudo spctl --enable --label "智能视频下载工具"

echo ""
echo "修复完成！"
echo "现在可以尝试打开应用了。"