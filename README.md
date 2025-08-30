# 视频生成器 - Python版本

这是一个将原始bash脚本重写为Python的视频生成工具，支持内置定时调度，无需Docker。

## 功能特性

- 🐍 **Python重写**: 将原始bash脚本转换为更易维护的Python代码
- ⏰ **内置调度**: 使用Python schedule库实现定时调度，无需外部依赖
- 📊 **多类别支持**: 支持蔬菜、水果、水产、肉禽蛋四个类别
- 📝 **日志记录**: 完整的执行日志和错误追踪
- 🔄 **文件同步**: 自动同步生成的文件到远程服务器
- 🚀 **简单部署**: 纯Python实现，无需Docker

## 项目结构

```
video-gen-repeatly/
├── video_generator.py      # 主要的Python脚本
├── setup.py               # 快速设置脚本
├── Dockerfile             # Docker镜像构建文件（可选）
├── docker-compose.yml     # Docker Compose配置（可选）
├── requirements.txt       # Python依赖包
├── README.md             # 项目说明文档
├── .env                  # 环境变量配置文件
├── .env.example          # 环境变量配置模板
├── logs/                 # 日志文件目录
└── data/                 # 数据文件目录
```

## 快速开始

### 1. 自动设置（推荐）

```bash
# 运行设置脚本
python setup.py
```

这将自动：
- 创建必要的目录
- 安装Python依赖
- 创建配置文件

### 2. 手动设置

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 创建必要的目录
```bash
mkdir -p logs data/output
```

#### 配置环境变量
复制并编辑配置文件：
```bash
cp .env.example .env
# 编辑 .env 文件，配置你的API地址和服务器信息
```

### 3. 配置SSH密钥

确保你的SSH密钥已正确配置：
```bash
# 检查SSH密钥
ls -la ~/.ssh/id_rsa

# 如果需要，生成新的SSH密钥
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

## 使用方法

### 查看帮助

```bash
python video_generator.py --help
```

### 手动执行一次

```bash
# 立即执行一次视频生成任务
python video_generator.py --run-once
```

### 启动定时调度

```bash
# 启动调度器，每日下午2点自动执行
python video_generator.py

# 程序将持续运行，按 Ctrl+C 停止
```

### 后台运行

```bash
# 使用 nohup 在后台运行
nohup python video_generator.py > scheduler.log 2>&1 &

# 查看进程
ps aux | grep video_generator

# 停止后台进程
kill <process_id>
```

### 查看日志

```bash
# 查看实时日志
tail -f logs/video_generator.log

# 查看最近的日志
tail -n 50 logs/video_generator.log
```

## Docker使用方法（可选）

如果你更喜欢使用Docker，项目也提供了Docker支持：

### 构建镜像

```bash
docker-compose build
```

### 启动调度器

```bash
# 启动调度器服务（后台运行）
docker-compose up -d video-generator

# 查看日志
docker-compose logs -f video-generator
```

### 手动执行一次

```bash
# 立即执行一次
docker-compose run --rm video-generator-once
```

### 停止服务

```bash
docker-compose down
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `API_URL` | `http://localhost:3100/api/generate-video` | 视频生成API地址 |
| `RSYNC_SOURCE` | `./data/output` | rsync源目录 |
| `RSYNC_DEST` | `root@112.126.78.105:~/web/x` | rsync目标地址 |
| `SSH_KEY_PATH` | `~/.ssh/id_rsa` | SSH私钥路径 |
| `SCHEDULE_TIME` | `14:00` | 每日执行时间 (24小时制) |

### 商品类别

脚本会为以下4个类别生成视频：
- 蔬菜
- 水果
- 水产
- 肉禽蛋

### 日志文件

日志文件保存在 `logs/video_generator.log`，包含：
- 执行时间戳
- 调度器状态
- 每个类别的处理状态
- HTTP请求详情
- 文件同步结果
- 错误信息

## 故障排除

### 常见问题

1. **SSH连接失败**
   - 检查SSH密钥权限：`chmod 600 ~/.ssh/id_rsa`
   - 确认目标服务器可访问
   - 检查SSH密钥是否正确
   - 测试SSH连接：`ssh -i ~/.ssh/id_rsa root@112.126.78.105`

2. **API请求失败**
   - 检查API服务是否运行
   - 确认API_URL配置正确
   - 查看网络连接状态
   - 测试API：`curl -X POST http://localhost:3100/api/generate-video`

3. **定时任务不执行**
   - 检查程序是否在运行：`ps aux | grep video_generator`
   - 查看日志文件：`tail -f logs/video_generator.log`
   - 确认SCHEDULE_TIME格式正确 (HH:MM)

4. **依赖安装失败**
   - 升级pip：`pip install --upgrade pip`
   - 使用虚拟环境：`python -m venv venv && source venv/bin/activate`

### 调试模式

```bash
# 立即执行一次，查看详细输出
python video_generator.py --run-once

# 检查配置
python -c "import os; print('API_URL:', os.getenv('API_URL', 'http://localhost:3100/api/generate-video'))"
```

## 原始bash脚本对比

| 功能 | Bash脚本 | Python版本 |
|------|----------|------------|
| HTTP请求 | `http` 命令 | `requests` 库 |
| 日期处理 | `date` 命令 | `datetime` 模块 |
| 循环处理 | bash数组循环 | Python列表循环 |
| 文件同步 | `rsync` 命令 | `subprocess` 调用rsync |
| 定时调度 | 外部cron | 内置schedule库 |
| 错误处理 | 基础 | 完整的异常处理和日志 |
| 可维护性 | 较低 | 高 |
| 调试能力 | 有限 | 强大 |
| 部署复杂度 | 中等 | 简单 |

## 许可证

MIT License