# Build Stage
FROM node:20-bookworm AS build-stage
WORKDIR /app

# Install dependencies
COPY package.json yarn.lock ./
COPY package*.json ./
RUN yarn install

# Build the application
COPY . .
RUN yarn build || \
    (yarn config set registry https://registry.yarnpkg.com && yarn install) || \
    (yarn config set registry https://registry.npmjs.org && yarn install)

# Production Stage
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]