# k8s-python-app

FastAPI + Pydantic v2 微服务，用于 K8s 集群调度与探针检测。

## 技术栈

- **Runtime**: Python 3.12 + FastAPI + uvicorn
- **包管理**: uv + pyproject.toml
- **序列化**: orjson (Rust 底层)
- **HTTP Client**: httpx[http2, brotli]
- **容器化**: 多阶段 Docker 构建，非 root 运行
- **编排**: Kubernetes Deployment + Liveness/Readiness 探针

## 本地开发

```bash
uv sync
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## 测试

```bash
uv run pytest
```

## Docker 构建

```bash
docker build -f docker/Dockerfile -t python-app:latest .
```

<img width="1394" alt="image" src="https://github.com/AIMWLI/k8s-python-app/assets/31265254/ebe04f68-bf7b-45d4-9907-7b18302665c0">
