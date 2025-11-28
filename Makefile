# FastAPI 微服务架构 - 快捷命令
# 使用前请确保已安装 Docker 和 Docker Compose

.PHONY: help dev prod down restart logs logs-service db-shell redis-shell test clean ps

# 默认命令
help:
	@echo "FastAPI 微服务架构快捷命令"
	@echo "=========================="
	@echo ""
	@echo "开发环境:"
	@echo "  make dev          - 启动开发环境（热重载）"
	@echo "  make dev-service  - 启动开发环境（不重建）"
	@echo "  make logs         - 查看所有服务日志"
	@echo "  make logs-service - 查看指定服务日志（如: make logs-service user）"
	@echo "  make down         - 停止并删除容器"
	@echo ""
	@echo "生产环境:"
	@echo "  make prod         - 启动生产环境"
	@echo "  make prod-build   - 构建生产镜像"
	@echo "  make prod-down    - 停止生产环境"
	@echo ""
	@echo "调试工具:"
	@echo "  make ps           - 查看所有服务状态"
	@echo "  make redis-shell  - 进入 Redis 命令行"
	@echo "  make pg-shell     - 进入 PostgreSQL 命令行"
	@echo "  make mysql-shell  - 进入 MySQL 命令行（需要启用optional profile）"
	@echo ""
	@echo "测试:"
	@echo "  make test         - 运行所有单元测试"
	@echo "  make test-service - 测试指定服务（如: make test-service user）"
	@echo ""
	@echo "清理:"
	@echo "  make clean        - 清理所有容器、卷和网络"
	@echo "  make clean-images - 清理所有镜像（慎用）"

# ============================================
# 开发环境命令
# ============================================

## 启动开发环境（首次运行）
dev:
	echo "正在启动开发环境(首次运行)…"
	echo "这将构建所有服务的镜像，请耐心等待"
	cp -n .env.dev .env 2>/dev/null || true
	docker compose -f docker-compose.dev.yml --env-file .env up --build

## 启动开发环境（不重建）
dev-service:
	echo "正在启动开发环境（跳过构建）…"
	cp -n .env.dev .env 2>/dev/null || true
	docker compose -f docker-compose.dev.yml --env-file .env up

## 进入开发环境
dev-exec:
	@echo "可用服务:"
	@ls services/
	@echo ""
	@echo "使用方法: make dev-exec SERVICE=user-service"
	@if [ -z "$(SERVICE)" ]; then \
		echo "错误: 请指定服务名称 (SERVICE=xxx)"; \
		exit 1; \
	fi
	docker compose -f docker-compose.dev.yml exec $(SERVICE) /bin/sh

## 重启开发环境
restart:
	docker compose -f docker-compose.dev.yml restart
	@echo "✅ 开发环境已重启"

## 停止开发环境
down:
	docker compose -f docker-compose.dev.yml down
	@echo "✅ 开发环境已停止"

# ===========================================
# 生产环境命令
# ===========================================

## 启动生产环境
prod:
	echo "正在启动生产环境…"
	@if [ ! -f .env ]; then \
		echo "错误: .env 文件不存在，请先配置生产环境"; \
		echo "建议: cp .env.prod .env"; \
		exit 1; \
	fi
	docker compose -f docker-compose.prod.yml --env-file .env up -d
	@echo "✅ 生产环境已启动"
	@echo "等待 10 秒，让服务完成初始化…"
	@sleep 10
	@echo "服务状态:"
	@make ps

## 构建生产镜像
prod-build:
	echo "正在构建生产镜像…"
	docker compose -f docker-compose.prod.yml --env-file .env build --no-cache
	@echo "✅ 生产镜像构建完成"

## 停止生产环境
prod-down:
	docker compose -f docker-compose.prod.yml down
	@echo "✅ 生产环境已停止"

# 生产环境日志
prod-logs:
	docker compose -f docker-compose.prod.yml logs -f

===========================================
# 日志管理
===========================================

## 查看所有日志
logs:
	docker compose -f docker-compose.dev.yml logs -f

## 查看指定服务日志
logs-service:
	@if [ -z "$(SERVICE)" ]; then \
		echo "错误: 请指定服务名称 (SERVICE=xxx)"; \
		echo "例如: make logs-service user-service"; \
		exit 1; \
	fi
	docker compose -f docker-compose.dev.yml logs -f $(SERVICE)

# ===========================================
# 调试工具
# ===========================================

## 查看服务状态
ps:
	@echo "======== 开发环境 ========"
	@docker-compose -f docker-compose.dev.yml ps 2>/dev/null || echo "开发环境未启动"
	@echo ""
	@echo "======== 生产环境 ========"
	@docker-compose -f docker-compose.prod.yml ps 2>/dev/null || echo "生产环境未启动"

## 进入 Redis 命令行
redis-shell:
	docker compose -f docker-compose.dev.yml exec redis redis-cli

## 进入 PostgreSQL 命令行
pg-shell:
	docker compose -f docker-compose.dev.yml exec postgres psql -U postgres -d microservices

## 进入 MySQL 命令行
mysql-shell:
	docker compose -f docker-compose.dev.yml --profile optional exec mysql mysql -uroot -p$${MYSQL_ROOT_PASSWORD}

# ===========================================
# 测试
# ===========================================

## 运行所有测试
test:
	@echo "运行所有服务的测试…"
	@cd services/user-service && pytest tests/ -v
	@cd services/order-service && pytest tests/ -v
	@cd services/product-service && pytest tests/ -v

## 测试指定服务
test-service:
	@if [ -z "$(SERVICE)" ]; then \
		echo "错误: 请指定服务名称 (SERVICE=xxx)"; \
		echo "例如: make test-service user-service"; \
		exit 1; \
	fi
	docker compose -f docker-compose.dev.yml exec $(SERVICE) pytest tests/ -v

## 快速测试（开发中）
test-quick:
	@cd services/user-service && pytest tests/ -v --tb=short

# ===========================================
# 清理和维护
# ===========================================

## 清理开发环境
clean-dev:
	docker compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f
	@echo "✅ 开发环境已清理"

## 清理生产环境
clean-prod:
	docker compose -f docker-compose.prod.yml down -v --remove-orphans
	docker system prune -f
	@echo "✅ 生产环境已清理"

## 清理所有
clean:
	docker compose -f docker-compose.dev.yml down -v --remove-orphans 2>/dev/null || true
	docker compose -f docker-compose.prod.yml down -v --remove-orphans 2>/dev/null || true
	docker system prune -af --volumes
	@echo "✅ 所有容器、网络和卷已清理"

## 清理镜像（慎用）
clean-images:
	@echo "⚠️  即将删除所有未使用的 Docker 镜像"
	@echo "是否继续? [y/N]"
	@read -r ans && [ "$${ans}" = "y" ] || exit 1
	docker image prune -a -f
	@echo "✅ 镜像已清理"

# ===========================================
# 快速开始
# ===========================================

init:
	@echo "=============================="
	@echo "  FastAPI 微服务项目初始化"
	@echo "=============================="
	@echo ""
	@echo "步骤 1: 配置开发环境"
	@cp -n .env.dev .env 2>/dev/null && echo "✓ 已创建 .env（从 .env.dev 复制）" || echo "✓ .env 已存在"
	@echo ""
	@echo "步骤 2: 首次启动开发环境"
	@echo "命令: make dev"
	@echo ""
	@echo "步骤 3: 在浏览器中访问服务"
	@echo "用户服务: http://localhost/api/users/docs"
	@echo "订单服务: http://localhost/api/orders/docs"
	@echo "商品服务: http://localhost/api/products/docs"
	@echo ""
	@echo "步骤 4: 查看日志"
	@echo "命令: make logs"
	@echo ""
	@echo "步骤 5: 停止服务"
	@echo "命令: make down"

# 显示环境对比
compare:
	@echo "开发环境与生产环境对比"
	@echo "=============================="
	@echo ""
	@echo "开发环境:"
	@echo "  make dev        → 代码热重载，适合开发"
	@echo "  数据库: SQLite  → 快速启动，无需配置"
	@echo "  日志: DEBUG    → 详细信息，便于调试"
	@echo "  端口: 全暴露   → 直接访问每个服务"
	@echo ""
	@echo "生产环境:"
	@echo "  make prod       → 高性能，适合部署"
	@echo "  数据库: PostgreSQL → 稳定可靠"
	@echo "  日志: INFO     → 精简信息，节省空间"
	@echo "  Worker: 4个     → 处理高并发"
