# macOS 应用公证设置指南

## 前提条件

### 1. Apple开发者账号
- 访问 https://developer.apple.com
- 注册开发者账号（年费 $99 USD）
- 等待账号激活

### 2. 创建开发者证书

#### 方法A：使用Xcode（推荐）
1. 打开 Xcode
2. 菜单：Xcode → Settings → Accounts
3. 点击 "+" 添加Apple ID
4. 选择团队，点击 "Manage Certificates"
5. 点击 "+" 创建 "Developer ID Application" 证书

#### 方法B：使用命令行
```bash
# 查看已安装的证书
security find-identity -v -p codesigning

# 输出示例：
# 1) XXXXXXXXXX "Developer ID Application: Your Name (TEAMID)"
```

### 3. 创建App专用密码
1. 访问 https://appleid.apple.com
2. 登录后，进入"登录与安全"
3. 选择"App专用密码"
4. 点击"生成密码"
5. 输入名称（如："视频下载工具公证"）
6. 保存生成的密码（格式：xxxx-xxxx-xxxx-xxxx）

### 4. 获取团队ID
```bash
# 在Xcode中查看
# 或访问 https://developer.apple.com/account
# 在 Membership 页面查看 Team ID
```

## 配置公证脚本

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入您的信息：
```bash
DEVELOPER_ID="Developer ID Application: 您的名字 (团队ID)"
APPLE_ID="您的AppleID@example.com"
APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"  # App专用密码
TEAM_ID="XXXXXXXXXX"  # 10位团队ID
```

3. 验证配置：
```bash
./load_env.sh
```

## 执行公证

```bash
# 确保有执行权限
chmod +x notarize_app.sh

# 运行公证脚本
./notarize_app.sh
```

## 公证流程说明

1. **代码签名**：使用开发者证书对应用签名
2. **提交公证**：上传应用到Apple服务器进行扫描
3. **等待审核**：通常需要几分钟到几小时
4. **装订票据**：将公证票据附加到应用
5. **创建DMG**：制作安装包
6. **公证DMG**：对安装包也进行公证

## 常见问题

### Q: 没有开发者账号怎么办？
A: 可以选择：
- 个人开发者账号：$99/年
- 公司开发者账号：$99/年（需要邓白氏编码）
- 或继续使用ad-hoc签名，让用户手动允许

### Q: 公证失败怎么办？
A: 检查：
- 证书是否有效
- entitlements.plist配置是否正确
- 代码中是否有不安全的API调用
- 查看详细日志：`xcrun notarytool log`

### Q: 公证需要多长时间？
A: 通常5-30分钟，高峰期可能需要几小时

## 免费替代方案

如果不想支付开发者年费，可以：

1. **使用ad-hoc签名**（当前方案）
   - 用户需要手动允许运行
   - 适合小范围分发

2. **使用TestFlight**
   - 需要开发者账号
   - 可以分发给测试用户

3. **开源发布**
   - 提供源代码和安装脚本
   - 用户自行编译

## 验证公证状态

```bash
# 检查应用是否已公证
spctl -a -vvv -t install "dist/智能视频下载工具.app"

# 成功输出：
# dist/智能视频下载工具.app: accepted
# source=Notarized Developer ID

# 查看公证详情
xcrun stapler validate "dist/智能视频下载工具.app"
```