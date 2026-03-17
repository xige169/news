# News User MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 基于现有 FastAPI 后端补齐最小可联调契约，并新增一个 React 用户端 MVP，覆盖登录、新闻浏览、新闻详情、收藏、历史和个人中心闭环。

**Architecture:** 先修复后端契约稳定性，再新增独立 `frontend/` 工程。前端按 `app shell + pages + services + stores` 四层组织，页面只消费稳定的 API 封装；后端仅做最小修复，不在本轮扩展搜索、推荐算法或后台管理能力。

**Tech Stack:** FastAPI, SQLAlchemy async, pytest, React, Vite, TypeScript, React Router, Zustand, Axios

---

### Task 1: 固化后端契约问题清单

**Files:**
- Modify: `docs/plans/2026-03-15-news-user-mvp-plan.md`
- Check: `backend/routers/users.py`
- Check: `backend/routers/favorite.py`
- Check: `backend/utils/auth.py`
- Check: `backend/crud/users.py`

**Step 1: 记录本轮必须修复的后端问题**

写入本计划或 issue 清单，至少包含：
- `return HTTPException(...)` 改为 `raise HTTPException(...)`
- `get_user_by_id` 查询条件错误
- 收藏接口 `newsID/newsId` 命名不一致
- 收藏分页参数别名拼写错误
- 清空收藏接口同步/异步错误
- 成功响应结构与 `hasMore` 命名统一

**Step 2: 明确本轮不做的能力**

写清以下能力延期到下一阶段：
- 搜索
- token 刷新
- 后台管理
- 推荐策略优化

**Step 3: 不写代码，只确认范围**

预期结果：所有参与实现的人都知道“先稳契约，再做前端”。

### Task 2: 为用户与鉴权修复补测试

**Files:**
- Create: `tests/test_users_router.py`
- Modify: `tests/test_backend_main.py`
- Check: `backend/routers/users.py`
- Check: `backend/utils/auth.py`

**Step 1: 写登录/注册/用户信息异常路径测试**

至少覆盖：
- 注册已存在用户时返回 400
- 登录失败时返回 401
- 无效 token 访问用户信息时返回 401

**Step 2: 运行用户相关测试，确认当前失败**

Run: `conda run -n normal pytest tests/test_users_router.py tests/test_backend_main.py -v`

Expected:
- 与异常抛出或响应结构相关的断言失败

**Step 3: 修正用户模块实现**

修改：
- `backend/routers/users.py`
- `backend/utils/auth.py`
- `backend/crud/users.py`

修复点：
- 所有错误分支使用 `raise`
- `get_current_user` 未鉴权时稳定抛 401
- `get_user_by_id` 使用真实 `user_id`

**Step 4: 重新运行测试**

Run: `conda run -n normal pytest tests/test_users_router.py tests/test_backend_main.py -v`

Expected:
- PASS

### Task 3: 为收藏接口修复补测试

**Files:**
- Create: `tests/test_favorite_router.py`
- Check: `backend/routers/favorite.py`
- Check: `backend/schemas/favorite.py`
- Check: `backend/crud/favorite.py`

**Step 1: 为收藏接口写失败测试**

至少覆盖：
- `/add` 能正确接收 `newsId`
- `/check`、`/remove`、`/list` 参数别名一致
- `/clear` 可以正确 await 并返回删除条数语义

**Step 2: 运行测试确认失败**

Run: `conda run -n normal pytest tests/test_favorite_router.py -v`

Expected:
- 因字段名、别名或 async 行为导致失败

**Step 3: 最小修复收藏实现**

修改：
- `backend/routers/favorite.py`
- `backend/schemas/favorite.py`

修复要求：
- 输入统一使用 `newsId`
- 输出统一使用 `favoriteId`、`favoriteTime`、`hasMore`
- `clear_favorite_list` 改为异步路由并正确 `await`

**Step 4: 重新运行测试**

Run: `conda run -n normal pytest tests/test_favorite_router.py tests/test_favorite_model.py -v`

Expected:
- PASS

### Task 4: 统一后端响应契约

**Files:**
- Modify: `backend/routers/news.py`
- Modify: `backend/routers/users.py`
- Modify: `backend/routers/favorite.py`
- Modify: `backend/routers/history.py`
- Check: `backend/utils/response.py`

**Step 1: 统一成功返回结构**

规则：
- 所有成功响应使用 `{ code, message, data }`
- 所有列表响应中的分页字段统一为 `hasMore`

**Step 2: 修正历史和新闻模块的命名漂移**

确认以下字段一致：
- `pageSize`
- `categoryId`
- `publishTime`
- `viewTime`

**Step 3: 跑后端冒烟测试**

Run: `conda run -n normal pytest tests -v`

Expected:
- 现有测试与新增路由契约测试通过

### Task 5: 初始化前端工程

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/styles/variables.css`
- Create: `frontend/src/styles/global.css`

**Step 1: 使用 Vite 初始化 React + TypeScript 工程**

要求：
- 目录固定为 `frontend/`
- 不污染现有 `backend/`

**Step 2: 建立基础依赖**

至少包含：
- `react-router-dom`
- `zustand`
- `axios`

**Step 3: 建立全局样式和设计基调**

要求：
- 响应式布局
- 首页采用新闻门户流
- 避免后台管理台视觉风格

**Step 4: 启动前端开发服务器**

Run: `cd frontend && npm install && npm run dev`

Expected:
- Vite 正常启动

### Task 6: 搭建前端基础骨架

**Files:**
- Create: `frontend/src/router/index.tsx`
- Create: `frontend/src/layouts/AppShell.tsx`
- Create: `frontend/src/components/navigation/Header.tsx`
- Create: `frontend/src/components/feedback/EmptyState.tsx`
- Create: `frontend/src/components/feedback/ErrorState.tsx`
- Create: `frontend/src/stores/authStore.ts`
- Create: `frontend/src/lib/http.ts`
- Create: `frontend/src/types/api.ts`

**Step 1: 配置路由**

路由至少包含：
- `/login`
- `/register`
- `/`
- `/news/:id`
- `/favorites`
- `/history`
- `/profile`
- `/profile/edit`
- `/profile/password`

**Step 2: 配置 Axios 拦截器**

要求：
- 自动附带 token
- 401 时清空登录态并跳回登录页

**Step 3: 建立登录态 Store**

要求：
- 保存 token
- 保存用户信息
- 支持本地持久化

**Step 4: 冒烟验证**

Run: `cd frontend && npm run build`

Expected:
- 构建通过

### Task 7: 实现认证与用户中心页面

**Files:**
- Create: `frontend/src/pages/LoginPage.tsx`
- Create: `frontend/src/pages/RegisterPage.tsx`
- Create: `frontend/src/pages/ProfilePage.tsx`
- Create: `frontend/src/pages/ProfileEditPage.tsx`
- Create: `frontend/src/pages/ProfilePasswordPage.tsx`
- Create: `frontend/src/services/userService.ts`

**Step 1: 先写用户服务层**

封装接口：
- `login`
- `register`
- `getUserInfo`
- `updateUserInfo`
- `updatePassword`

**Step 2: 实现登录和注册页**

要求：
- 表单校验明确
- 成功后写入登录态
- 失败提示显示后端 message

**Step 3: 实现个人中心与设置页**

要求：
- 展示当前用户信息
- 支持编辑资料
- 支持修改密码

**Step 4: 验证认证闭环**

Run:
- `cd frontend && npm run build`
- 手工联调 `/api/user/*`

Expected:
- 登录注册和获取用户信息闭环可用

### Task 8: 实现新闻门户首页与详情页

**Files:**
- Create: `frontend/src/pages/HomePage.tsx`
- Create: `frontend/src/pages/NewsDetailPage.tsx`
- Create: `frontend/src/components/news/CategoryTabs.tsx`
- Create: `frontend/src/components/news/NewsCard.tsx`
- Create: `frontend/src/components/news/Pagination.tsx`
- Create: `frontend/src/components/news/RelatedNews.tsx`
- Create: `frontend/src/services/newsService.ts`

**Step 1: 封装新闻接口**

接口：
- `getCategories`
- `getNewsList`
- `getNewsDetail`

**Step 2: 实现首页**

要求：
- 分类切换
- 传统分页
- 卡片式新闻列表
- 空态和错误态

**Step 3: 实现详情页**

要求：
- 正文展示
- 相关推荐
- 页面级加载状态

**Step 4: 构建验证**

Run: `cd frontend && npm run build`

Expected:
- PASS

### Task 9: 实现收藏与历史闭环

**Files:**
- Create: `frontend/src/pages/FavoritesPage.tsx`
- Create: `frontend/src/pages/HistoryPage.tsx`
- Create: `frontend/src/components/news/FavoriteButton.tsx`
- Create: `frontend/src/services/favoriteService.ts`
- Create: `frontend/src/services/historyService.ts`

**Step 1: 先封装收藏与历史服务**

接口：
- `checkFavorite`
- `addFavorite`
- `removeFavorite`
- `getFavoriteList`
- `clearFavoriteList`
- `addHistory`
- `getHistoryList`
- `deleteHistory`
- `clearHistory`

**Step 2: 在详情页接入收藏与历史动作**

要求：
- 详情加载成功后写历史
- 收藏状态可切换

**Step 3: 实现收藏页与历史页**

要求：
- 传统分页
- 单条删除
- 清空操作

**Step 4: 联调验证**

Run:
- `cd frontend && npm run build`
- 手工验证收藏和历史闭环

Expected:
- PASS

### Task 10: 收尾与交付

**Files:**
- Create: `frontend/README.md`
- Create: `docs/plans/2026-03-15-news-user-mvp-contract.md`
- Modify: `task_plan.md`

**Step 1: 输出联调契约文档**

内容至少包含：
- 页面与接口映射表
- token 使用方式
- 字段命名约定
- 已知未实现能力

**Step 2: 更新根级规划跟踪**

将 `task_plan.md` 各阶段改为完成，并补充执行建议。

**Step 3: 最终验证**

Run:
- `conda run -n normal pytest tests -v`
- `cd frontend && npm run build`

Expected:
- 后端测试通过
- 前端构建通过
- 文档齐全
