#!/bin/bash
# 智能视频下载工具打包脚本

echo "开始打包智能视频下载工具..."

# 检查logo文件是否存在
if [ ! -f "logo.png" ]; then
    echo "错误: logo.png 文件不存在！"
    echo "请确保 logo.png 文件在当前目录中"
    exit 1
fi

echo "找到 logo.png 文件"

# 清理之前的构建
echo "清理旧的构建文件..."
rm -rf build dist

# 使用PyInstaller打包
echo "开始使用PyInstaller打包..."
echo "正在将 logo.png 作为应用图标打包..."
pyinstaller --clean video_downloader.spec

# 检查打包结果
if [ -d "dist/智能视频下载工具.app" ]; then
    echo "打包成功！"
    echo "应用程序位置: dist/智能视频下载工具.app"
    echo "应用图标: logo.png 已成功集成"
    
    # 移除隔离属性，允许应用运行
    echo "移除隔离属性..."
    xattr -cr "dist/智能视频下载工具.app"
    
    # 创建DMG（可选）
    # echo "创建DMG安装包..."
    # hdiutil create -volname "智能视频下载工具" -srcfolder dist/智能视频下载工具.app -ov -format UDZO dist/智能视频下载工具.dmg
else
    echo "打包失败！"
    exit 1
fi

echo "完成！"