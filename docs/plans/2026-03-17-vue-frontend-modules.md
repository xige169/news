# Vue Frontend Modules Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 基于现有 Vue 3 + Vant 前端，补齐登录、注册、新闻详情、收藏、历史、个人中心及资料编辑闭环，并与当前 FastAPI 接口契约一致。

**Architecture:** 前端按 `router + views + services + stores` 分层，页面不直接拼请求。先建立认证与通用请求层，再实现新闻详情和账户能力，最后补收藏/历史页面与导航。所有行为优先通过最小前端契约测试锁定请求路径、鉴权头和关键字段映射。

**Tech Stack:** Vue 3、Vue Router、Pinia、Vant、Vite、原生 `fetch`、Node test runner

---

### Task 1: 建立前端认证与请求基础层

**Files:**
- Create: `frontend/src/services/http.js`
- Create: `frontend/src/services/auth.js`
- Create: `frontend/src/store/auth.js`
- Create: `frontend/src/services/auth.test.js`
- Modify: `frontend/src/router/index.js`

**Step 1: 写失败测试**

- 验证登录请求走 `POST /api/user/login`
- 验证注册请求走 `POST /api/user/register`
- 验证受保护请求带 `Authorization: Bearer <token>`

**Step 2: 跑测试确认失败**

Run: `node --test frontend/src/services/auth.test.js`

**Step 3: 写最小实现**

- 实现统一 JSON 请求和错误处理
- 实现登录、注册、获取个人信息接口
- 实现 Pinia 登录态存储、清理、读 token
- 在路由里加入登录页、注册页和受保护页面守卫

**Step 4: 跑测试确认通过**

Run: `node --test frontend/src/services/auth.test.js`

### Task 2: 实现登录与注册页面

**Files:**
- Create: `frontend/src/views/LoginPage.vue`
- Create: `frontend/src/views/RegisterPage.vue`
- Modify: `frontend/src/style.css`

**Step 1: 写失败测试**

- 验证认证页提交后调用服务层
- 验证成功后写入登录态并跳转首页

**Step 2: 跑测试确认失败**

Run: `node --test frontend/src/services/auth.test.js`

**Step 3: 写最小实现**

- 完成品牌化登录/注册页
- 接入表单校验、加载态、错误提示

**Step 4: 验证通过**

- `npm run build`
- 手工验证 `/login`、`/register`

### Task 3: 扩展新闻服务并实现详情页

**Files:**
- Create: `frontend/src/views/NewsDetailPage.vue`
- Modify: `frontend/src/services/news.js`
- Create: `frontend/src/services/news-detail.test.js`
- Modify: `frontend/src/router/index.js`
- Modify: `frontend/src/views/HomePage.vue`

**Step 1: 写失败测试**

- 验证详情请求走 `GET /api/news/detail?id=`
- 验证详情页加载后会触发历史写入和收藏状态查询

**Step 2: 跑测试确认失败**

Run: `node --test frontend/src/services/news-detail.test.js`

**Step 3: 写最小实现**

- 首页列表支持跳转详情
- 详情页展示标题、作者、时间、正文、相关推荐
- 接入添加历史、检查收藏、收藏切换

**Step 4: 验证通过**

- `node --test frontend/src/services/news-detail.test.js`
- `npm run build`

### Task 4: 实现收藏与历史页面

**Files:**
- Create: `frontend/src/services/favorite.js`
- Create: `frontend/src/services/history.js`
- Create: `frontend/src/services/library.test.js`
- Create: `frontend/src/views/FavoritesPage.vue`
- Create: `frontend/src/views/HistoryPage.vue`
- Modify: `frontend/src/router/index.js`

**Step 1: 写失败测试**

- 验证收藏列表、清空收藏请求路径
- 验证历史列表、删除单条、清空历史请求路径

**Step 2: 跑测试确认失败**

Run: `node --test frontend/src/services/library.test.js`

**Step 3: 写最小实现**

- 收藏页展示列表和清空动作
- 历史页展示列表、删除单条和清空动作
- 支持从列表跳转详情

**Step 4: 验证通过**

- `node --test frontend/src/services/library.test.js`
- `npm run build`

### Task 5: 实现个人中心、资料编辑与密码修改

**Files:**
- Create: `frontend/src/views/ProfilePage.vue`
- Create: `frontend/src/views/ProfileEditPage.vue`
- Create: `frontend/src/views/ProfilePasswordPage.vue`
- Create: `frontend/src/services/profile.test.js`
- Modify: `frontend/src/services/auth.js`
- Modify: `frontend/src/router/index.js`

**Step 1: 写失败测试**

- 验证获取信息、更新资料、修改密码请求路径与 payload

**Step 2: 跑测试确认失败**

Run: `node --test frontend/src/services/profile.test.js`

**Step 3: 写最小实现**

- 个人中心展示用户资料、收藏入口、历史入口、退出登录
- 编辑资料页接 `PUT /api/user/update`
- 修改密码页接 `PUT /api/user/password`

**Step 4: 验证通过**

- `node --test frontend/src/services/profile.test.js`
- `npm run build`

### Task 6: 联调收尾与验证

**Files:**
- Modify: `frontend/src/components/TabBar.vue`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/style.css`

**Step 1: 统一导航与页面状态**

- 让首页、收藏、历史、个人中心之间导航清晰
- 对空态、加载态、401 失效处理做统一体验

**Step 2: 跑完整验证**

Run:
- `node --test frontend/src/services/*.test.js`
- `conda run -n normal pytest tests/test_backend_main.py -v`
- `npm run build`

**Step 3: 手工烟测**

- 登录
- 首页切分类
- 进入详情
- 收藏/取消收藏
- 浏览历史生成与删除
- 编辑资料
- 修改密码
