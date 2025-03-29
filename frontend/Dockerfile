# 1. Build stage
FROM node:20-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install

# Copy rest of frontend source
COPY . .

# Build React app for production
RUN npm run build

# 2. Production stage (Nginx)
FROM nginx:alpine

# Copy the compiled build from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 in the container
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]