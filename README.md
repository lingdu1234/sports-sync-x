# Sports Sync X

一个可以在 Garmin.cn、Garmin.com 和 Coros 三个平台之间自动同步运动记录的工具。支持自动检测和删除重复记录，并支持企业微信通知。

## 功能特性

- **多平台同步**：支持 Garmin CN、Garmin COM 和 Coros 三个运动平台
- **重复记录检测**：自动检测重复的运动记录，并可配置自动删除
- **智能同步**：根据运动时间等信息智能判断是否需要同步
- **FIT 文件处理**：支持下载和上传 FIT 格式的运动数据文件
- **数据库存储**：使用 SQLite 数据库存储运动记录，便于管理和查询
- **消息通知**：支持企业微信机器人通知同步完成状态
- **灵活配置**：通过环境变量配置同步平台和账号信息

## 环境要求

- Python >= 3.14
- uv (包管理器)

## 安装

1. 克隆项目：

```bash
git clone <repository-url>
cd sports-sync-x
```

1. 使用 uv 安装依赖：

```bash
uv sync
```

## 配置

1. 复制环境变量配置文件：

```bash
cp .env.example .env
```

1. 编辑 `.env` 文件，填写相关配置：

```env
# 需要同步的平台（多个平台用逗号分隔）
SYNC_PLATFORM=GARMINCN,GARMINCOM,COROS

# Garmin COM 账号配置
GARMIN_EMAIL_COM=your_garmin_email@example.com
GARMIN_PASSWORD_COM=your_garmin_password

# Garmin CN 账号配置
GARMIN_EMAIL_CN=your_garmin_email@example.com
GARMIN_PASSWORD_CN=your_garmin_password

# Coros 账号配置
COROS_EMAIL=your_coros_email@example.com
COROS_PASSWORD=your_coros_password

# Garmin 获取最新记录数量
GARMIN_NEWEST_NUM=10000

# 是否自动删除重复记录（1=删除，0=不删除）
DELETE_DUPLICATE=1

# 运动时间差异阈值（秒），用于判断是否为重复记录
SPORT_DIFF_SECOND=60

# 企业微信机器人 Key（可选）
QYWX_BOT_KEY=your_qywx_bot_key
```

## 使用

运行同步程序：

```bash
uv run x-sync.py
```

或使用 Python 直接运行：

```bash
python x-sync.py
```

## 工作流程

程序执行以下步骤：

1. **初始化数据库**：创建 SQLite 数据库用于存储运动记录
2. **获取运动记录**：从配置的平台获取所有运动记录
3. **处理重复记录**：
   - 将运动记录按 activity_id 排序
   - 保存到数据库，检测重复记录
   - 如果配置了 `DELETE_DUPLICATE=1`，自动删除重复记录
4. **检查同步状态**：检查每个运动记录在各平台的同步状态
5. **同步运动记录**：
   - 下载未同步的运动记录 FIT 文件
   - 上传到目标平台
   - 更新同步状态
6. **发送通知**：通过企业微信机器人发送同步完成通知

## 项目结构

```tree
sports-sync-x/
├── app/
│   ├── coros/           # Coros 平台相关代码
│   ├── database/         # 数据库操作
│   ├── garmin/          # Garmin 平台相关代码
│   ├── oss/             # OSS 客户端（阿里云/AWS）
│   ├── sync_fn/         # 同步功能实现
│   └── utils/           # 工具函数
├── tests/               # 测试文件
├── x-sync.py            # 程序入口
├── pyproject.toml       # 项目配置
├── .env.example         # 环境变量示例
└── README.md            # 项目说明
```

## 支持的运动类型

程序支持多种运动类型，包括但不限于：

- 跑步（跑步机、越野跑、虚拟跑步等）
- 骑行（公路骑行、室内骑行、砾石路骑行等）
- 游泳（泳池游泳、公开水域游泳等）
- 健身（力量训练、室内有氧、HIIT 等）
- 户外运动（徒步、登山、攀岩等）
- 球类运动（篮球、足球、网球等）
- 水上运动（皮划艇、冲浪、帆船等）

完整的运动类型映射请参考 [app/utils/const.py](app/utils/const.py)

## 数据存储

- **数据库文件**：`db/sports_sync.sqlite`
- **FIT 文件存储**：
  - Garmin COM: `fit/garmin_com/`
  - Garmin CN: `fit/garmin_cn/`
  - Coros: `fit/coros/`

## 注意事项

1. **账号安全**：请妥善保管 `.env` 文件中的账号密码信息，不要提交到版本控制系统
2. **API 限制**：各平台的 API 可能有调用频率限制，请合理设置同步间隔
3. **网络环境**：Garmin CN 需要在中国大陆网络环境下访问
4. **重复记录**：删除重复记录操作不可逆，请谨慎配置 `DELETE_DUPLICATE` 选项
5. **数据备份**：建议定期备份数据库文件和 FIT 文件

## 故障排除

### 认证失败

- 检查 `.env` 文件中的账号密码是否正确
- 确认账号是否开启了二次验证（如需要，请关闭或使用应用密码）

### 同步失败

- 检查网络连接是否正常
- 确认目标平台的 API 是否正常工作
- 查看控制台输出的错误信息

### 重复记录未删除(请注意删除风险，及时备份数据)

- 确认 `DELETE_DUPLICATE=1` 已正确配置
- 检查 `SPORT_DIFF_SECOND` 阈值设置是否合理

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
