# 项目初始化指南

本文档用于帮助开发者在一台新机器上完成本项目初始化，并跑通后端、前端和本地联调环境。

## 1. 项目概览

当前仓库是一个前后端分离的新闻门户项目：

- 后端：`backend/`
  - 技术栈：FastAPI、SQLAlchemy Async、MySQL、Redis
- 前端：`frontend/`

核心页面如下：

- `/` 首页
- `/news/:id` 新闻详情
- `/login` 登录
- `/register` 注册
- `/favorites` 收藏页
- `/history` 历史页
- `/profile` 个人中心
- `/profile/edit` 编辑资料
- `/profile/password` 修改密码

推荐初始化顺序：

1. 准备 Python / Node / MySQL / Redis
2. 创建并激活 Conda 环境
3. 安装后端依赖并导入数据库初始化 SQL
4. 启动后端服务
5. 安装前端依赖并启动前端服务
6. 执行测试与构建
7. 做一轮联调烟测

## 2. 环境要求

建议环境：

- 操作系统：Linux / macOS
- Python：3.10
- Node.js：24.x
- npm：11.x
- MySQL：8.x
- Redis：6.x 或以上
- Conda：已安装，并可创建 `normal` 环境

## 3. 目录结构

关键目录如下：

```text
news/
├── backend/                         # FastAPI 后端
├── frontend/                        # React 前端
├── tests/                           # 后端测试
├── docs/
│   ├── 01-接口规范文档/
│   ├── 02-数据库sql文件/
│   ├── plans/
│   └── init-项目初始化指南.md
└── .worktrees/                      # 本地隔离工作树（已加入 .gitignore）
```

## 4. 后端初始化

### 4.1 创建 Conda 环境

如果本地还没有 `normal` 环境，可先创建：

```bash
conda create -n normal python=3.10 -y
conda activate normal
```

### 4.2 安装后端依赖

仓库当前没有现成的 `requirements.txt`，建议先按项目实际依赖安装：

```bash
conda activate normal
pip install fastapi uvicorn sqlalchemy aiomysql passlib bcrypt redis pydantic pytest pytest-asyncio httpx
```

如果后续补了依赖文件，以依赖文件为准。

### 4.3 准备 MySQL

默认数据库连接配置在 [db_conf.py](/home/xige/project/news/backend/config/db_conf.py)。

初始化前请确认：

- MySQL 已启动
- 存在数据库 `news_app`
- 本地数据库账号密码与配置一致，或你已经更新为自己的本地配置

### 4.4 导入数据库初始化 SQL

初始化 SQL 文件位于：

- [database.sql](/home/xige/project/news/docs/02-数据库sql文件/database.sql)

执行示例：

```bash
mysql -uroot -p news_app < docs/02-数据库sql文件/database.sql
```

### 4.5 准备 Redis

缓存配置位于 [cache_conf.py](/home/xige/project/news/backend/config/cache_conf.py)。

默认假设 Redis 运行在本机。若你的 Redis 不在默认地址，请同步修改配置。

### 4.6 启动后端

在项目根目录执行：

```bash
conda run -n normal uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

启动后可做基础检查：

```bash
curl http://127.0.0.1:8000/
```

预期返回：

```json
{"message":"Hello World"}
```

## 5. 前端初始化

### 5.1 安装依赖

```bash
cd frontend
npm install
```

### 5.2 启动前端

```bash
npm run dev -- --host 127.0.0.1 --port 5173
```

默认访问地址：

- `http://127.0.0.1:5173`

### 5.3 前端当前结构说明

当前前端采用统一编辑化视觉，重点包括：

- 顶部媒体式导航与登录态展示
- 首页“导语 + 栏目切换 + 新闻流 + 编辑侧栏”结构
- 详情页“标题 + 元信息 + 正文 + 侧栏推荐”结构
- 登录 / 注册统一为品牌型双栏认证页
- 收藏 / 历史 / 个人中心统一为一致的账户与阅读管理界面

### 5.4 代理说明

Vite 已配置开发代理：

- `/api` -> `http://127.0.0.1:8000`

对应配置文件：

- [vite.config.ts](/home/xige/project/news/frontend/vite.config.ts)

这意味着前端开发时直接请求 `/api/...` 即可，无需手动写死后端完整地址。

## 6. 验证步骤

### 6.1 后端测试

在项目根目录执行：

```bash
conda run -n normal pytest tests -v
```

说明：

- 测试数量会随仓库演进变化，不要把文档中的通过数写死
- 以“全部通过且无新增失败”为准

### 6.2 前端测试

在 `frontend/` 目录执行：

```bash
npm test
```

### 6.3 前端构建

在 `frontend/` 目录执行：

```bash
npm run build
```

### 6.4 手工烟测

建议至少检查这些路径：

1. 打开首页 `/`
2. 切换新闻分类
3. 打开新闻详情页
4. 注册新用户并登录
5. 查看个人中心
6. 收藏一条新闻并进入收藏页
7. 浏览一条新闻并进入历史页

## 7. 当前联调契约

联调细节文档在：

- [2026-03-15-news-user-mvp-contract.md](/home/xige/project/news/docs/plans/2026-03-15-news-user-mvp-contract.md)

重点约定包括：

- 鉴权头：`Authorization: Bearer <token>`
- 收藏参数：`newsId`
- 历史删除键：`historyId`
- 分页参数：`page`、`pageSize`
- 前端收到 `401` 后会清空本地登录态并跳转 `/login`

## 8. 常见问题

### 8.1 前端能打开，但接口 404 或代理失败

优先检查：

- 后端是否运行在 `127.0.0.1:8000`
- 前端是否通过 `npm run dev -- --host 127.0.0.1 --port 5173` 启动
- [vite.config.ts](/home/xige/project/news/frontend/vite.config.ts) 的代理配置是否被改动

### 8.2 登录后接口返回 `401`

优先检查：

- 是否使用了最新登录返回的 token
- 请求头是否为 `Authorization: Bearer <token>`
- 后端是否已重启到最新代码

### 8.3 MySQL 能连接，但接口报数据库错误

优先检查：

- `news_app` 数据库是否已导入初始化 SQL
- [db_conf.py](/home/xige/project/news/backend/config/db_conf.py) 中账号密码是否与你本地一致

### 8.4 Redis 未启动

现有新闻模块会使用缓存。Redis 不可用时，部分接口可能异常或联调不稳定，建议初始化阶段就先启动 Redis。

### 8.5 Conda 环境有旧依赖告警

若出现类似 `_distutils_hack` 的告警，通常不会直接阻塞本地开发，但建议后续统一整理 Conda 环境，避免持续噪音。

## 9. 推荐开发顺序

如果你是第一次接手这个项目，建议按下面顺序推进：

1. 跑通数据库、Redis、后端服务
2. 跑通前端 dev 服务
3. 执行后端测试和前端测试 / 构建
4. 从首页、详情页开始联调
5. 再联调登录、收藏、历史、个人中心

## 10. 相关文档

- [项目后端设计说明文档.md](/home/xige/project/news/docs/项目后端设计说明文档.md)
- [API接口规范文档.md](/home/xige/project/news/docs/01-接口规范文档/API接口规范文档.md)
- [2026-03-15-news-user-mvp-plan.md](/home/xige/project/news/docs/plans/2026-03-15-news-user-mvp-plan.md)
- [2026-03-15-news-user-mvp-contract.md](/home/xige/project/news/docs/plans/2026-03-15-news-user-mvp-contract.md)
