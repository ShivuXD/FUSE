FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY src/vigil_fuse /app/vigil_fuse
USER 65532:65532
ENTRYPOINT ["python", "-m", "vigil_fuse.execution_worker"]
