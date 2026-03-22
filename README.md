# News App

一个面向简历强化的新闻客户端项目，采用前后端分离架构：

- 后端：FastAPI + SQLAlchemy Async + MySQL + Redis
- 前端：Vue 3 + Vite + Vant + Pinia + Vue Router
- 鉴权：JWT access token + refresh token + Redis 黑名单登出

## 当前能力

- 用户注册、登录、刷新会话、退出登录
- 首页新闻分类流、热门新闻、个性化推荐
- 新闻搜索、新闻详情、相关推荐
- 收藏、历史记录、个人资料维护
- 前端自动处理 `401`，尝试刷新 access token 后重试一次请求

## 本地启动

### 后端

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

## 环境变量

复制 `.env.example` 并按本地环境修改：

```bash
cp .env.example .env
```

后端重点变量：

- `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD`
- `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB`
- `JWT_SECRET_KEY`
- `JWT_ACCESS_EXPIRE_MINUTES`
- `JWT_REFRESH_EXPIRE_DAYS`

## Docker Compose

项目提供最小容器化编排：

```bash
docker compose up --build
```

默认会启动：

- `mysql`
- `redis`
- `backend`

前端仍建议本地运行，便于开发调试。

## 测试与构建

```bash
conda run -n normal pytest tests -q
node --test frontend/src/services/auth.test.js frontend/src/services/news.test.js frontend/src/services/news-detail.test.js frontend/src/services/profile.test.js frontend/src/utils/profile.test.js
cd frontend && npm run build
```

## 简历可写点

- 基于用户浏览历史与收藏记录实现个性化新闻推荐
- 使用 JWT + refresh token + Redis 黑名单实现无状态鉴权与登出失效
- 为新闻系统补齐搜索、推荐、热门流和前后端契约测试
- 使用 Docker Compose 组织 MySQL、Redis、FastAPI 服务，提升本地交付一致性
