# Build Stage
FROM node:22-alpine AS build
WORKDIR /app

# Enable corepack and install deps
RUN corepack enable
COPY package.json ./
RUN npm i

# Copy sources and build static
COPY . .
RUN npm run generate

# Runtime Stage: Nginx
FROM nginx:1.27-alpine

# Copy built static site
COPY --from=build /app/.output/public/ /usr/share/nginx/html/

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose and run
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
