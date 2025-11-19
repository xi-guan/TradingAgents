# 开发阶段
FROM node:20-alpine AS development

WORKDIR /app

# 安装 pnpm
RUN npm install -g pnpm

# 复制 package.json
COPY package.json pnpm-lock.yaml ./

# 安装依赖
RUN pnpm install

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 3000

# 开发命令
CMD ["pnpm", "dev", "--host"]

# 生产构建阶段
FROM node:20-alpine AS build

WORKDIR /app

RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# 生产运行阶段
FROM nginx:alpine AS production

# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
