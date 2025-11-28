#
# Docker 镜像 - 用户服务
# 这是一个标准的 Python 3.12 Alpine 镜像
# ===================================
# 此镜像适用于开发环境，包含完整的开发和运行环境
#
# 构建命令:
#   docker build -t user-service .
#
# 运行命令:
#   docker run -d -p 8000:8000 --name user-service user-service
#

# 基础镜像: Python 3.12 Slim
FROM python:3.12-slim

# 设置时区
ENV TZ=Asia/Shanghai

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements 到工作目录
COPY requirements.txt .

# 安装 Python 依赖（使用清华大学镜像源加速）
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码到工作目录
COPY . .

# 显示目录结构（用于调试）
RUN ls -la

# 默认启动命令（开发环境）
# 使用 bash 解释器启动，方便调试
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]
