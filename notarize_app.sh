#!/bin/bash
# macOS应用公证脚本

# ===== 加载环境变量 =====
source ./load_env.sh

if ! load_env; then
    echo "错误：无法加载环境变量"
    exit 1
fi

if ! check_env; then
    echo "错误：环境变量配置不完整"
    exit 1
fi

# ===== 配置部分 =====
# 从环境变量读取配置
DEVELOPER_ID="${DEVELOPER_ID}"
APPLE_ID="${APPLE_ID}"
APP_PASSWORD="${APP_PASSWORD}"
TEAM_ID="${TEAM_ID}"

APP_PATH="dist/${APP_NAME}.app"
APP_NAME="${APP_NAME:-智能视频下载工具}"
BUNDLE_ID="${BUNDLE_ID:-com.videodownloader.v2}"

# ===== 检查配置 =====
if [[ "$DEVELOPER_ID" == *"Your Name"* ]]; then
    echo "错误：请先配置开发者信息"
    echo ""
    echo "需要准备："
    echo "1. Apple开发者账号（年费 $99）"
    echo "2. 开发者证书（Developer ID Application）"
    echo "3. App专用密码"
    echo ""
    echo "获取步骤："
    echo "1. 访问 https://developer.apple.com 注册开发者账号"
    echo "2. 在 Xcode 中创建开发者证书"
    echo "3. 在 https://appleid.apple.com 创建App专用密码"
    exit 1
fi

echo "===== macOS应用公证流程 ====="
echo ""

# 1. 清理旧文件
echo "1. 清理旧文件..."
rm -rf "$APP_PATH"
rm -f "${APP_NAME}.zip"
rm -f "${APP_NAME}.dmg"

# 2. 重新打包
echo "2. 重新打包应用..."
./build_app.sh

# 3. 使用开发者证书签名
echo "3. 使用开发者证书签名..."
codesign --force --deep --sign "$DEVELOPER_ID" \
    --options runtime \
    --entitlements entitlements.plist \
    --timestamp \
    "$APP_PATH"

# 4. 验证签名
echo "4. 验证签名..."
codesign --verify --deep --strict --verbose=2 "$APP_PATH"

# 5. 创建ZIP文件用于公证
echo "5. 创建ZIP文件..."
ditto -c -k --keepParent "$APP_PATH" "${APP_NAME}.zip"

# 6. 提交公证
echo "6. 提交公证到Apple..."
xcrun notarytool submit "${APP_NAME}.zip" \
    --apple-id "$APPLE_ID" \
    --password "$APP_PASSWORD" \
    --team-id "$TEAM_ID" \
    --wait

# 7. 装订票据
echo "7. 装订公证票据..."
xcrun stapler staple "$APP_PATH"

# 8. 创建DMG安装包
echo "8. 创建DMG安装包..."
create-dmg \
    --volname "$APP_NAME" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "$APP_NAME.app" 175 120 \
    --hide-extension "$APP_NAME.app" \
    --app-drop-link 425 120 \
    "${APP_NAME}.dmg" \
    "$APP_PATH"

# 9. 签名DMG
echo "9. 签名DMG..."
codesign --force --sign "$DEVELOPER_ID" "${APP_NAME}.dmg"

# 10. 公证DMG
echo "10. 公证DMG..."
xcrun notarytool submit "${APP_NAME}.dmg" \
    --apple-id "$APPLE_ID" \
    --password "$APP_PASSWORD" \
    --team-id "$TEAM_ID" \
    --wait

# 11. 装订DMG
echo "11. 装订DMG..."
xcrun stapler staple "${APP_NAME}.dmg"

echo ""
echo "===== 公证完成！====="
echo "已生成文件："
echo "- ${APP_PATH} (已公证的应用)"
echo "- ${APP_NAME}.dmg (已公证的安装包)"
echo ""
echo "现在可以分发给任何用户，无需特殊权限即可运行！"