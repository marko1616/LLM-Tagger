FROM python:3.13-slim AS builder
WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || \
    (pip install --no-cache-dir -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple)

COPY ./api.py ./
COPY ./config.json ./
RUN mkdir -p datasets
RUN mkdir -p uploads

# Start backend
EXPOSE 1080
CMD ["python", "api.py"]