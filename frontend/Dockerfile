# Build Stage
FROM node:20-alpine AS build-stage
WORKDIR /app

# Proxy
ARG PROXY=""
ENV HTTP_PROXY=${PROXY}
ENV HTTPS_PROXY=${PROXY}
ENV ALL_PROXY=${PROXY}

# Install dependencies
ARG USE_MIRROR=false
COPY package.json package-lock.json ./
RUN if [ "${USE_MIRROR}" = "true" ]; then \
        npm --loglevel info --registry https://npmreg.proxy.ustclug.org/ install; \
    else \
        npm --loglevel info install; \
    fi

# Build the application
COPY ./src ./src
RUN npm run build

# Production Stage
FROM nginx:stable-alpine AS production-stage
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]