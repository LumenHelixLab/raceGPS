FROM node:20-slim
WORKDIR /app
COPY package*.json ./
COPY apps/backend/package.json ./apps/backend/package.json
COPY packages/protocol/package.json ./packages/protocol/package.json
COPY packages/protocol/src ./packages/protocol/src
COPY packages/protocol/tsconfig.json ./packages/protocol/tsconfig.json
COPY apps/backend/src ./apps/backend/src
COPY apps/backend/tsconfig.json ./apps/backend/tsconfig.json
RUN npm install
RUN npm run build --workspace @racegps/protocol && npm run build --workspace @racegps/backend
EXPOSE 8787
CMD ["npm", "run", "start", "--workspace", "@racegps/backend"]
