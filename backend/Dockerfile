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
        echo "Using PyPI mirror: https://mirrors.ustc.edu.cn/pypi/simple" && \
        pip install --no-cache-dir -r requirements.txt -i https://mirrors.ustc.edu.cn/pypi/simple; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

COPY ./api.py ./
COPY ./config.json ./
RUN mkdir -p datasets
RUN mkdir -p uploads

# Start backend
EXPOSE 1080
CMD ["python", "api.py"]