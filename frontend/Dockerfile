# Build Stage
FROM node:20-bookworm AS build-stage
WORKDIR /app

# Proxy
ARG PROXY=""
ENV HTTP_PROXY=${PROXY}
ENV HTTPS_PROXY=${PROXY}
ENV ALL_PROXY=${PROXY}

# Install dependencies
COPY package.json yarn.lock ./
COPY package*.json ./
RUN yarn install

# Build the application
COPY ./src ./src
RUN yarn build

# Production Stage
FROM nginx:stable-alpine AS production-stage
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]