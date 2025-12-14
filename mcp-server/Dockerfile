FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY src ./src
COPY core ./core
COPY policies ./policies
COPY agents ./agents
COPY tools ./tools
COPY memory ./memory
COPY reasoning ./reasoning

# Create logs directory
RUN mkdir -p logs

# Build TypeScript
RUN npm run build

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {if (r.statusCode !== 200) throw new Error('unhealthy');})"

# Start server
CMD ["npm", "start"]
