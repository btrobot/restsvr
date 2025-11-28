# FastAPI 微服务架构

一个开箱即用的 FastAPI 微服务开发模板，支持快速开发、测试和部署。

## 🎯 核心特性

✅ **开发友好**：代码热重载、实时日志、Volume 挂载开发
✅ **一次构建**：开发/测试/生产环境切换
✅ **三个微服务**：用户、订单、商品服务示例，可扩展
✅ **完整基础设施**：Nginx、Redis、PostgreSQL、MySQL
✅ **自动化测试**： pytest + 异步测试支持
✅ **监控与健康检查**：内建健康检查端点

---

## 📁 目录结构

```
.
├── docker-compose.dev.yml          # 开发环境配置
├── docker-compose.prod.yml         # 生产环境配置
├── Makefile                        # 快捷命令
├── .env                            # 环境配置（从 .env.dev 或 .env.prod 复制）
├── .env.dev                        # 开发环境模板
├── .env.prod                       # 生产环境模板
├── nginx/
│   ├── nginx.dev.conf              # 开发环境 Nginx 配置
│   └── nginx.prod.conf             # 生产环境 Nginx 配置
├── redis/
│   └── redis.conf                  # Redis 配置
├── services/
│   ├── user-service/               # ✅ 已实现：用户服务
│   │   ├── app/                    #   - main.py
│   │   │   ├── core/               #   - config.py, database.py
│   │   │   ├── models/             #   - user.py
│   │   │   ├── routers/            #   - health.py, users.py
│   │   │   └── schemas/            #   - user.py
│   │   ├── tests/                  #   - 完整测试用例
│   │   ├── Dockerfile              #   - 开发镜像
│   │   ├── Dockerfile.prod         #   - 生产镜像
│   │   └── requirements.txt        #   - Python 依赖
│   ├── order-service/              # 📋 待实现：订单服务
│   └── product-service/            # 📋 待实现：商品服务
└── docs/
    ├── 微服务架构需求文档.md       # 需求文档
    └── 环境差异对比.md             # 环境配置说明（本文档）
```

---

## 🚀 快速开始

### 前置要求

- `Docker Desktop` (Windows/Mac) 或 `Docker Engine` (Linux)
- Docker Compose V2
- 8GB+ 可用内存
- 2GB+ 磁盘空间

### 第一步：克隆项目

```bash
git clone <your-repo-url>
cd microservices-fastapi
```

### 第二步：配置开发环境

```bash
# 复制开发环境配置
cp .env.dev .env

# 手动检查 .env 文件确认配置正确
# 特别是数据库密码等信息
```

### 第三步：启动开发环境

```bash
# 方法 1: 使用 Makefile（推荐）
make dev

# 方法 2: 直接使用 Docker Compose
docker-compose -f docker-compose.dev.yml up --build

# 方法 3: 后台运行
docker-compose -f docker-compose.dev.yml up -d --build
```

### 第四步：访问服务

所有服务统一通过 Nginx 访问：

| 服务 | 访问地址 | Swagger 文档 |
|------|----------|--------------|
| **用户服务** | `http://localhost/api/users` | `http://localhost/api/users/docs` |
| **订单服务** | `http://localhost/api/orders` | `http://localhost/api/orders/docs` |
| **商品服务** | `http://localhost/api/products` | `http://localhost/api/products/docs` |
| **Nginx 健康检查** | `http://localhost/nginx-health` | - |

### 第五步：查看实时日志

```bash
# 方法 1: 使用 Makefile
make logs

# 方法 2: 查看所有服务
make logs

# 方法 3: 查看指定服务（如 user-service）
make logs-service SERVICE=user-service
```

### 第六步：停止服务

```bash
# 停止开发环境
make down

# 或者使用 Docker Compose
docker-compose -f docker-compose.dev.yml down
```

---

## 📊 环境配置对比

### 快速对比表

| 配置项 | 开发环境 | 生产环境 |
|--------|----------|----------|
| **启动命令** | `make dev` | `make prod` |
| **配置文件** | `docker-compose.dev.yml` | `docker-compose.prod.yml` |
| **环境变量** | `.env.dev` → `.env` | `.env.prod` → `.env` |
| **Nginx 配置** | `nginx.dev.conf` | `nginx.prod.conf` |
| **代码更新** | **Volume 挂载**（实时同步） | **打包进镜像**（不可变） |
| **Web 服务器** | Uvicorn（单进程） | Gunicorn + Uvicorn（多进程） |
| **Worker 数量** | 1 个（节省资源） | CPU 核心数 × 2 + 1 |
| **热重载** | ✅ 开启 `--reload` | ❌ 关闭（提升性能） |
| **日志级别** | DEBUG（详细） | INFO（精简） |
| **数据库** | SQLite（快速启动） | PostgreSQL（高性能） |
| **调试模式** | ✅ 开启 | ❌ 关闭（提升性能） |
| **CORS 配置** | `*`（允许所有） | 明确域名（提升安全） |
| **API 文档** | ✅ 公开访问 | ❌ 可关闭或限制访问 |
| **健康检查** | 基础检查 | 深度检查 + 自动重启 |
| **资源限制** | 无限制 | CPU/Memory 限制 |
| **端口暴露** | 所有服务端口 | 仅 Nginx 80/443 |
| **服务副本** | 1 个（单实例） | 2+ 个（负载均衡） |

### 详细说明

#### 1. 🔥 代码更新机制 - 最大差异

**开发环境（Volume 挂载）**
```yaml
# docker-compose.dev.yml
volumes:
  - ./services/user-service:/app  # 本地代码直接映射到容器
  - /app/.venv                    # 排除虚拟环境
  - /app/__pycache__              # 排除编译缓存
```

**使用方法：**
- 在本地 IDE 编辑代码
- 保存后 Docker 容器内自动更新
- FastAPI/Uvicorn 自动检测变化并重载
- **1-2 秒内立即生效** ⏱️

**优点：**
- 无需重新构建镜像
- 支持断点调试
- 开发体验极佳，反馈循环短

**生产环境（代码打包进镜像）**
```yaml
# docker-compose.prod.yml
# 无 volumes，代码已打包进镜像
volumes: []  # 空列表
```

**使用方法：**
- 修改代码 → 重新构建镜像 → 重新部署
- 镜像构建命令：`make prod-build`
- 部署命令：`make prod`

**优点：**
- 镜像不可变，环境一致性高
- 支持版本回滚
- 符合 12-Factor App 准则

---

#### 2. 🚀 Web 服务器配置差异

**开发环境（Uvicorn 单进程）**
```bash
# 快速重启，便于调试
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload  # 核心：自动重载
  --log-level debug  # 详细日志
```

**生产环境（Gunicorn + Uvicorn 多进程）**
```bash
# 高性能多进程模式
gunicorn app.main:app \
  --bind 0.0.0.0:8000 \
  --workers 4  # 4 个 worker 进程
  --worker-class uvicorn.workers.UvicornWorker \
  --max-requests 1000 \
  --timeout 60 \
  --worker-tmp-dir /dev/shm
```

**性能差异：**
- 开发环境：单进程，10-50 req/s
- 生产环境：多进程，500-2000 req/s（取决于 CPU）

---

#### 3. 🗄️ 数据库差异

**开发环境（SQLite）**
- ✅ **优点：**
  - 无需安装数据库服务
  - 开箱即用，零配置
  - 文件式存储，便于备份和迁移
- ❌ **缺点：**
  - 不支持高并发
  - 无完整 SQL 支持
  - 不适合生产 data persistent

**生产环境（PostgreSQL）**
- ✅ **优点：**
  - 企业级关系型数据库
  - ACID 事务、高并发、连接池
  - 数据安全性高，支持备份恢复
- ❌ **缺点：**
  - 需要独立部署和维护
  - 配置相对复杂

---

#### 4. 📈 性能与资源限制

**开发环境（无限制）**
- CPU：无限制（使用宿主机所有核心）
- 内存：无限制（使用宿主机所有内存）
- Restart Policy: `unless-stopped`（手动停止前一直运行）

**生产环境（资源限制）**
```yaml
# docker-compose.prod.yml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
    reservations:
      cpus: '1'
      memory: 512M
```

**效果：**
- 防止单个服务占用全部资源
- 保障其他服务稳定运行
- 提升整体系统稳定性

---

#### 5. 🛡️ 安全差异

| 安全配置 | 开发环境 | 生产环境 |
|----------|----------|----------|
| **运行用户** | root | appuser（非 root） |
| **CORS** | `*`（允许所有） | 明确域名 |
| **API 文档** | 公开可访问 | 可关闭或限制访问 |
| **调试信息** | 详细错误堆栈 | 精简错误信息 |
| **密码加密** | bcrypt | bcrypt（同上） |
| **限流** | 无 | 100 req/min |

**生产环境 Docker 用户示例：**
```dockerfile
FROM python:3.12-slim

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 切换到非 root 用户运行
USER appuser

# ...
```

---

#### 6. 📊 监控与健康检查

**开发环境（基础检查）**
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**生产环境（深度检查 + 自动重启）**
```yaml
docker-compose.prod.yml:
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s      # 每30秒检查一次
  timeout: 10s       # 超时10秒
  retries: 3         # 失败3次后重启
  start_period: 40s  # 启动后40秒开始检查

restart_policy:
  condition: on-failure  # 仅在失败时重启
  delay: 5s
  max_attempts: 3
```

**监控指标：**
- 数据库连接状态
- Redis 连接状态
- 内存使用率
- 响应时间
- 错误率

---

## 🔧 Makefile 快捷命令

### 1. 开发环境命令

```bash
# 启动开发环境（首次）
make dev

# 启动开发环境（跳过构建）
make dev-service

# 重启开发环境
make restart

# 查看所有日志
make logs

# 查看指定服务日志
make logs-service SERVICE=user-service

# 进入服务容器
make dev-exec SERVICE=user-service

# 停止开发环境
make down

# 清理开发环境
make clean-dev
```

### 2. 生产环境命令

```bash
# 构建生产镜像
make prod-build

# 启动生产环境
make prod

# 查看生产环境日志
make prod-logs

# 停止生产环境
make prod-down

# 清理生产环境
make clean-prod
```

### 3. 调试工具

```bash
# 查看服务状态
make ps

# 进入 Redis
make redis-shell

# 进入 PostgreSQL
make pg-shell

# 进入 MySQL（需启动 optional profile）
make mysql-shell

# 运行所有测试
make test

# 测试指定服务
make test-service SERVICE=user-service
```

### 4. 维护命令

```bash
# 清理所有容器、网络和卷
make clean

# 清理所有镜像（慎用！）
make clean-images

# 查看帮助
make help

# 初始化项目
make init

# 查看环境对比
make compare
```

---

## 🏗️ 从零实现完整系统

### 第一步：先让 User Service 跑起来

1. 已完成 ✅ - User Service 已完整实现，包含：
   - 用户 CRUD API
   - 健康检查端点
   - 完整的测试用例
   - 开发/生产双 Dockerfile

### 第二步：复制并修改 Order Service

```bash
# 1. 进入订单服务目录
cd services/order-service

# 2. 复制 user-service 全部内容
cp -r ../user-service/* ./

# 3. 修改业务逻辑
#   - app/main.py: 标题改为 "订单服务"
#   - app/models/order.py: 定义订单表结构
#   - app/routers/orders.py: 实现订单 CRUD
#   - app/schemas/order.py: 定义订单数据模式
#   - tests/test_orders.py: 编写订单测试
```

### 第三步：复制并修改 Product Service

与第二步相同，修改商品相关模型和业务逻辑。

### 第四步：配置服务间通信

```python
# 示例：在 Order Service 中调用 User Service
import httpx

async def create_order(user_id: int, order_data: dict):
    # 1. 验证用户存在（调用 User Service）
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://user-service:8000/api/users/{user_id}"
        )
        if response.status_code != 200:
            raise Exception("用户不存在")

    # 2. 创建订单...
```

---

## 📖 Docker Compose Profiles（可选服务）

本项目支持 Docker Compose Profiles，用于按需启动可选服务。

### 启动 PostgreSQL（开发环境已默认启动）

```bash
# docker-compose.dev.yml 已包含 postgres 服务
# 无需额外操作
```

### 启动 MySQL（需显式指定）

```bash
# 启动开发环境并带上 optional profile
docker-compose -f docker-compose.dev.yml --profile optional up

# 或者启动生产环境并带上 optional profile
docker-compose -f docker-compose.prod.yml --profile optional up
```

**为什么使用 Profiles？**
- MySQL 在大多数业务场景下不需要
- 减少资源占用
- 按需启用，按需配置

---

## 🔍 调试技巧

### 1. 查看容器日志

```bash
# 实时查看所有日志
docker-compose -f docker-compose.dev.yml logs -f

# 查看指定服务（如 user-service）
docker-compose -f docker-compose.dev.yml logs -f user-service

# 查看最后 100 行
docker-compose -f docker-compose.dev.yml logs --tail=100
```

### 2. 进入容器调试

```bash
# 进入 user-service 容器
docker-compose -f docker-compose.dev.yml exec user-service /bin/sh

# 容器内安装调试工具
apk add curl vim

# 测试 Redis 连接
redis-cli -h redis ping

# 测试数据库连接（如果是 PostgreSQL）
nmap -p 5432 postgres
```

### 3. 在 VSCode 中调试

`.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Attach to User Service",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/services/user-service",
                    "remoteRoot": "/app"
                }
            ]
        }
    ]
}
```

---

## 📦 环境变量详解

### 核心环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `ENVIRONMENT` | 环境类型 | `development` / `production` |
| `DATABASE_URL` | 数据库连接 | `sqlite:///./test.db` |
| `REDIS_URL` | Redis 连接 | `redis://redis:6379/0` |
| `SERVICE_NAME` | 服务名称 | `user-service` |
| `LOG_LEVEL` | 日志级别 | `INFO` / `DEBUG` / `WARNING` |
| `ALLOWED_ORIGINS` | CORS 域名 | `http://localhost,https://your-domain.com` |

### 数据库专用变量

按优先级排序：

1. **SQLite**（最简单）
   ```bash
   DATABASE_URL=sqlite:///./test.db
   ```

2. **PostgreSQL**（生产推荐）
   ```bash
   POSTGRES_DB=microservices
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your-password
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   ```

3. **MySQL**（可选）
   ```bash
   MYSQL_DATABASE=microservices
   MYSQL_USER=user
   MYSQL_PASSWORD=your-password
   MYSQL_HOST=mysql
   MYSQL_PORT=3306
   ```

---

## 📏 性能基准

### 开发环境

```bash
# 使用 Apache Bench 测试
ab -n 100 -c 10 http://localhost/api/users/

# 预期结果（单进程）
Concurrency Level:      10
Time taken for tests:   1-3 秒
Requests per second:    30-100 [#/sec]
Time per request:       10-33 [ms]
```

### 生产环境

```bash
# 测试 4 个 worker 的性能
ab -n 1000 -c 50 http://localhost/api/users/

# 预期结果（4 个进程）
Concurrency Level:      50
Time taken for tests:   0.5-1 秒
Requests per second:    500-2000 [#/sec]
Time per request:       2-5 [ms]
```

**性能提升：10-20 倍** 🚀

---

## 🎯 常见问题

### Q1: 端口 80 已被占用怎么办？

```bash
# 方案 1: 修改 Nginx 端口
# 在 docker-compose.dev.yml 中修改
ports:
  - "8080:80"  # 改为 8080

# 方案 2: 停止占用 80 端口的进程
# Windows:
netstat -ano | findstr "80"
taskkill /PID <PID> /F

# Linux:
sudo lsof -i :80
sudo kill -9 <PID>
```

### Q2: Docker 构建很慢怎么办？

```bash
# 使用阿里云 Docker 镜像源
cat <<EOF > /etc/docker/daemon.json
{
  "registry-mirrors": ["https://<你的镜像源>.mirror.aliyuncs.com"]
}
EOF

# 重启 Docker
sudo systemctl daemon-reload
sudo systemctl restart docker

# 并且已经配置 requirements.txt 使用清华 PyPI 源
```

### Q3: 某个服务启动失败怎么办？

```bash
# 查看具体错误
make logs-service SERVICE=user-service

# 重新启动该服务
docker-compose -f docker-compose.dev.yml restart user-service

# 删除并重建容器
docker-compose -f docker-compose.dev.yml rm -f user-service
docker-compose -f docker-compose.dev.yml up user-service
```

### Q4: PostgreSQL 数据如何持久化？

```bash
# 在 docker-compose.prod.yml 中配置挂载卷
volumes:
  - postgres-data:/var/lib/postgresql/data
```

默认数据存在 Docker Volume 中，可通过以下命令备份：

```bash
# 备份 PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U postgres microservices > backup.sql

# 恢复 PostgreSQL
docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres microservices < backup.sql
```

---

## 📄 License

MIT License - 可自由使用和修改

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 🆘 技术支持

遇到问题？尝试：

1. 查阅本文档
2. 查看日志 `make logs`
3. 运行 `make help` 查看可用命令
4. 提交 Issue 到项目仓库
