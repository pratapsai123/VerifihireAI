# Stage 1: Build the React Application
FROM node:18-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy all project files and build
COPY . .
RUN npm run build

# Stage 2: Serve the Built Application with Nginx
FROM nginx:alpine

# Copy the custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built React app from the builder stage into the Nginx html folder under /admin
COPY --from=builder /app/dist /usr/share/nginx/html/admin

# Expose port 80 based on the Nginx configuration
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
