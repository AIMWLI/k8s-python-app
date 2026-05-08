# ========== Stage 1: 构建阶段 ==========
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# 启用 uv 的严格模式，跳过 bytecode 编译以加速构建，仅在最终阶段编译
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# 1. 利用 Docker 缓存层，先拷贝依赖清单
COPY pyproject.toml uv.lock* ./

# 安装依赖项 (不包含项目本身，不包含 dev 依赖)
RUN uv sync --no-install-project --no-dev

# 2. 拷贝实际业务代码并安装项目
COPY . /app
RUN uv sync --no-dev

# ========== Stage 2: 生产运行阶段 ==========
FROM python:3.12-slim-bookworm

# 工业级规范: 绝对禁止使用 root 运行服务，避免容器逃逸漏洞
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# 拷贝虚拟环境和代码，并转移所有权给 appuser
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/app /app/app

# 设置环境变量
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 8000

# 工业级规范: 在 K8s 并且 CPU Limit < 1 时，强烈建议 Worker 设为 1，将并发交给 K8s Replicas 去横向扩展。
# 若节点巨大，可通过环境变量覆盖
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
