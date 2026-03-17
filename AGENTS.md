# AGENTS.md

本文件是本仓库的项目级协作说明。任何在本仓库内工作的智能体或开发者，都应优先遵守这里的约定，并以当前代码和运行结果为准。

## 1. 项目概况

这是一个新闻客户端项目，采用前后端分离架构：

- 后端：FastAPI + SQLAlchemy Async + MySQL + Redis
- 前端：Vue 3 + Vite + Vant + Pinia + Vue Router
- 当前目标：完成新闻浏览、用户登录注册、收藏、历史记录、个人资料维护的联调闭环

当前用户端主要页面：

- `/` 首页
- `/news/:id` 新闻详情
- `/login` 登录
- `/register` 注册
- `/favorites` 收藏页
- `/history` 历史页
- `/profile` 个人中心
- `/profile/edit` 编辑资料
- `/profile/password` 修改密码

## 2. 目录结构

```text
news/
├── AGENTS.md
├── backend/
│   ├── cache/                       # Redis 缓存封装
│   ├── config/                      # 数据库与缓存配置
│   ├── crud/                        # 数据访问层
│   ├── models/                      # ORM 模型
│   ├── routers/                     # FastAPI 路由
│   ├── schemas/                     # Pydantic 数据结构
│   ├── utils/                       # 鉴权、响应、异常、加密
│   └── main.py                      # 后端入口
├── frontend/
│   ├── src/
│   │   ├── components/              # 通用 UI 组件
│   │   ├── i18n/                    # 国际化
│   │   ├── router/                  # 前端路由与守卫
│   │   ├── services/                # 接口封装与前端契约测试
│   │   ├── store/                   # Pinia 状态
│   │   ├── utils/                   # 前端工具函数
│   │   ├── views/                   # 页面级视图
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── package.json
│   └── vite.config.js
├── tests/                           # 后端测试
└── docs/                            # 接口文档、SQL、计划文档
```

组织原则：

- 后端按 `router -> schema -> crud -> model` 分层，不要把数据库细节直接写进路由。
- 前端按 `router -> view -> service -> store` 分层，页面不要直接拼接请求逻辑。
- 新增接口优先补对应测试或最小契约验证。
- 文档若与代码不一致，先以当前代码和运行结果为准，再补文档。

## 3. 后端约定

后端入口：

- `backend.main:app`

当前已接入的后端业务域：

- `news`
- `user`
- `favorite`
- `history`

统一约定：

- 成功响应优先使用 `{ code, message, data }`
- 鉴权头使用 `Authorization: Bearer <token>`
- 认证依赖在 `backend/utils/auth.py`
- 统一异常处理在 `backend/utils/exception.py`

修改后端时要特别注意：

- `gender` 数据库存储的是枚举值：`male`、`female`、`unknown`
- 新闻、收藏、历史相关接口存在 Redis 缓存依赖
- 不要擅自改接口字段名，尤其是 `newsId`、`historyId`、`page`、`pageSize`、`hasMore`

## 4. 前端约定

当前前端技术栈是 Vue，不是 React。不要再写与 React、TSX、Zustand、Next.js 相关的说明或代码。

当前前端结构重点：

- 路由定义在 `frontend/src/router/index.js`
- 登录态在 `frontend/src/store/auth.js`
- 通用请求在 `frontend/src/services/http.js`
- 新闻接口在 `frontend/src/services/news.js`
- 用户接口在 `frontend/src/services/auth.js`
- 收藏接口在 `frontend/src/services/favorite.js`
- 历史接口在 `frontend/src/services/history.js`

开发约定：

- 页面组件只处理展示、交互和状态编排
- API 请求统一走 `services/`
- `401` 失效统一由 `http.js` + 路由守卫处理
- `showTabBar`、`requiresAuth`、`guestOnly` 等页面行为统一由路由元信息控制
- 样式保持当前移动端新闻阅读风格，不要无理由改成后台管理风或桌面工作台风格

前端已存在但不作为当前主线的页面：

- `AiChatPage.vue`
- `MyPage.vue`

如非明确需求，不要围绕这些遗留页面扩展主流程，优先维护当前真实路由入口。

## 5. 本地运行

### 后端

建议使用固定环境：

```bash
conda run -n normal uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

数据库配置默认在：

- `backend/config/db_conf.py`

缓存配置默认在：

- `backend/config/cache_conf.py`

默认依赖：

- MySQL 本地可用
- Redis 本地可用
- 数据库名为 `news_app`

SQL 初始化文件：

- `docs/02-数据库sql文件/database.sql`

### 前端

安装依赖：

```bash
cd frontend
npm install
```

启动开发服务：

```bash
npm run dev -- --host 127.0.0.1 --port 5173
```

当前代理配置：

- `/api` -> `http://127.0.0.1:8000`

对应文件：

- `frontend/vite.config.js`

## 6. 测试与验证

后端测试：

```bash
conda run -n normal pytest tests -v
```

最小后端验证：

```bash
conda run -n normal pytest tests/test_backend_main.py -v
```

前端服务层契约测试：

```bash
node --test frontend/src/services/auth.test.js \
  frontend/src/services/news.test.js \
  frontend/src/services/news-detail.test.js \
  frontend/src/services/profile.test.js \
  frontend/src/utils/profile.test.js
```

前端构建验证：

```bash
cd frontend
npm run build
```

联调时至少检查：

1. 注册并登录
2. 首页加载分类和新闻列表
3. 打开新闻详情
4. 收藏与取消收藏
5. 历史记录生成与删除
6. 编辑资料
7. 修改密码

没有验证结果时，不要声称“已经修复”或“已经联通”。

## 7. 代码风格

通用要求：

- 默认使用 UTF-8
- 注释、文档、说明优先中文
- 保持最小必要改动
- 优先读现有代码再扩展，不要凭印象重写

后端要求：

- Python 模块名使用小写下划线
- Pydantic / Model / Schema 类名使用 PascalCase
- 路由函数名使用明确的动宾结构
- 只在确有必要时提交数据库字段层面的兼容改动

前端要求：

- Vue 单文件组件使用 PascalCase 文件名
- 服务层函数优先使用明确动词命名，如 `fetchNewsDetail`、`updateProfile`
- 不要把完整后端域名写死到页面里，始终走 `/api/...`
- 性别等枚举字段必须与后端契约对齐，不能提交展示文案值

## 8. 常见风险

- `frontend/dist/` 是构建产物，通常不是主要编辑目标
- `frontend/node_modules/` 不应纳入修改范围
- 后端用户资料更新依赖数据库枚举约束，错误值会触发数据库异常
- Redis 不可用时，新闻接口可能出现缓存相关异常或性能抖动
- 本地已有服务占用 `8000` 或 `5173` 端口时，不要误判为代码错误，先查进程

## 9. 协作规则

- 不要覆盖或回滚用户未明确授权的现有改动
- 若发现工作区已有不相关脏改动，默认避开，不要清理
- 需要联网、访问本地服务、启动长期运行进程时，按权限规则申请授权
- 遇到联调问题，先复现并拿到根因证据，再改代码
- 新增功能或修 bug 时，优先补最小失败测试或契约测试

## 10. 推荐阅读顺序

开始工作前，优先查看：

1. `AGENTS.md`
2. `docs/init-项目初始化指南.md`
3. `docs/plans/2026-03-15-news-user-mvp-contract.md`
4. `frontend/src/router/index.js`
5. `backend/main.py`

如果任务涉及具体业务，再按需读：

- `backend/routers/*.py`
- `backend/crud/*.py`
- `frontend/src/services/*.js`
- `frontend/src/views/*.vue`
