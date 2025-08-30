# 视频生成器 - Docker版本

这是一个将原始bash脚本重写为Python的视频生成工具，支持Docker容器化部署和定时调度。

## 功能特性

- 🐍 **Python重写**: 将原始bash脚本转换为更易维护的Python代码
- 🐳 **Docker支持**: 完整的容器化解决方案
- ⏰ **定时调度**: 每日下午2点(CST)自动执行
- 📊 **多类别支持**: 支持蔬菜、水果、水产、肉禽蛋四个类别
- 📝 **日志记录**: 完整的执行日志和错误追踪
- 🔄 **文件同步**: 自动同步生成的文件到远程服务器

## 项目结构

```
video-gen-repeatly/
├── video_generator.py      # 主要的Python脚本
├── Dockerfile             # Docker镜像构建文件
├── docker-compose.yml     # Docker Compose配置
├── requirements.txt       # Python依赖包
├── README.md             # 项目说明文档
├── logs/                 # 日志文件目录
├── ssh-keys/             # SSH密钥目录
└── data/                 # 数据文件目录
```

## 快速开始

### 1. 准备工作

#### 创建必要的目录
```bash
mkdir -p logs ssh-keys data
```

#### 配置SSH密钥
将你的SSH私钥复制到 `ssh-keys/` 目录：
```bash
cp ~/.ssh/id_rsa ssh-keys/
chmod 600 ssh-keys/id_rsa
```

### 2. 环境配置

编辑 `docker-compose.yml` 文件中的环境变量：

```yaml
environment:
  - API_URL=http://your-api-server:3100/api/generate-video  # 修改为你的API地址
  - RSYNC_SOURCE=/root/code/price-data/data/output          # 修改为你的源目录
  - RSYNC_DEST=root@your-server.com:~/web/x                # 修改为你的目标服务器
  - SSH_KEY_PATH=/root/.ssh/id_rsa
  - TZ=Asia/Shanghai
```

### 3. 构建和运行

#### 构建Docker镜像
```bash
docker-compose build
```

#### 手动运行一次测试
```bash
docker-compose run --rm video-generator
```

#### 启动定时调度服务
```bash
docker-compose up -d scheduler
```

## 使用方法

### 手动执行

```bash
# 运行一次视频生成任务
docker-compose run --rm video-generator

# 查看日志
docker-compose logs video-generator
```

### 定时调度

启动调度服务后，系统会在每天下午2点(CST)自动执行视频生成任务：

```bash
# 启动调度服务
docker-compose up -d scheduler

# 查看调度服务状态
docker-compose ps

# 查看调度服务日志
docker-compose logs scheduler
```

### 停止服务

```bash
# 停止调度服务
docker-compose down
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `API_URL` | `http://localhost:3100/api/generate-video` | 视频生成API地址 |
| `RSYNC_SOURCE` | `/root/code/price-data/data/output` | rsync源目录 |
| `RSYNC_DEST` | `root@112.126.78.105:~/web/x` | rsync目标地址 |
| `SSH_KEY_PATH` | `/root/.ssh/id_rsa` | SSH私钥路径 |
| `TZ` | `Asia/Shanghai` | 时区设置 |

### 商品类别

脚本会为以下4个类别生成视频：
- 蔬菜
- 水果
- 水产
- 肉禽蛋

### 日志文件

日志文件保存在 `logs/video_generator.log`，包含：
- 执行时间戳
- 每个类别的处理状态
- HTTP请求详情
- 文件同步结果
- 错误信息

## 故障排除

### 常见问题

1. **SSH连接失败**
   - 检查SSH密钥权限：`chmod 600 ssh-keys/id_rsa`
   - 确认目标服务器可访问
   - 检查SSH密钥是否正确

2. **API请求失败**
   - 检查API服务是否运行
   - 确认API_URL配置正确
   - 查看网络连接状态

3. **定时任务不执行**
   - 检查调度服务状态：`docker-compose ps`
   - 查看调度服务日志：`docker-compose logs scheduler`
   - 确认时区设置正确

### 调试模式

```bash
# 进入容器调试
docker-compose run --rm video-generator bash

# 手动执行Python脚本
python video_generator.py
```

## 原始bash脚本对比

| 功能 | Bash脚本 | Python版本 |
|------|----------|------------|
| HTTP请求 | `http` 命令 | `requests` 库 |
| 日期处理 | `date` 命令 | `datetime` 模块 |
| 循环处理 | bash数组循环 | Python列表循环 |
| 文件同步 | `rsync` 命令 | `subprocess` 调用rsync |
| 错误处理 | 基础 | 完整的异常处理和日志 |
| 可维护性 | 较低 | 高 |
| 调试能力 | 有限 | 强大 |

## 许可证

MIT License