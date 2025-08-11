#!/bin/bash
# 智能视频下载工具打包脚本

echo "开始打包智能视频下载工具..."

# 清理之前的构建
echo "清理旧的构建文件..."
rm -rf build dist

# 使用PyInstaller打包
echo "开始使用PyInstaller打包..."
pyinstaller video_downloader.spec

# 检查打包结果
if [ -d "dist/智能视频下载工具.app" ]; then
    echo "打包成功！"
    echo "应用程序位置: dist/智能视频下载工具.app"
    
    # 创建DMG（可选）
    # echo "创建DMG安装包..."
    # hdiutil create -volname "智能视频下载工具" -srcfolder dist/智能视频下载工具.app -ov -format UDZO dist/智能视频下载工具.dmg
else
    echo "打包失败！"
    exit 1
fi

echo "完成！"