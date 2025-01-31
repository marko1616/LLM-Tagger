FROM python:3.13-slim AS builder
WORKDIR /app

# Proxy
ARG PROXY=""
ENV HTTP_PROXY=${PROXY}
ENV HTTPS_PROXY=${PROXY}
ENV ALL_PROXY=${PROXY}

ARG USE_MIRROR=false
COPY ./requirements.txt ./
RUN if [ "${USE_MIRROR}" = "true" ]; then \
        pip install --no-cache-dir -r requirements.txt -i https://mirrors.ustc.edu.cn/pypi/simple; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Start backend
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY . .
EXPOSE 1080
CMD ["python", "-m", "src.main"]