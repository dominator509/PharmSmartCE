FROM node:20-alpine AS deps
WORKDIR /app
COPY pnpm-workspace.yaml package.json* pnpm-lock.yaml* ./
COPY apps/web/package.json apps/web/package.json
COPY packages/shared/package.json packages/shared/package.json
RUN corepack enable && pnpm install --frozen-lockfile

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/apps/web/node_modules ./apps/web/node_modules
COPY . .
RUN corepack enable && pnpm --filter web build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/apps/web/.next ./apps/web/.next
COPY --from=builder /app/apps/web/package.json ./apps/web/package.json
COPY --from=builder /app/apps/web/node_modules ./apps/web/node_modules
WORKDIR /app/apps/web
CMD ["node_modules/.bin/next", "start", "-H", "0.0.0.0"]
