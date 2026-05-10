# 前端整体重构设计文档

- 日期：2026-05-10
- 范围：`frontend/`（用户端 H5）+ `admin-web/`（管理后台）
- 类型：UI 重构（不动后端，不改 API 契约）

## 1. 背景与目标

当前用户端基于 Vant，是移动 H5 风格（`max-width: 750px`），与"桌面新闻门户"的产品定位不符；管理后台虽已用 Element Plus，但视觉与信息密度都偏弱。本次重构目标：

1. 用户端：从 Vant 移动样式整体改为**桌面优先的现代门户风格**（Medium / NYT 现代化混合），保留响应式以兼容平板和手机。
2. 管理后台：保留 Element Plus 与现有页面结构，整体替换为**数据看板风格**，强调密度、过滤器、状态色与图表，功能性优先。
3. 两个 app 共享一套设计 tokens（颜色 / 字体 / 间距），但物理上各自独立维护，不抽公共包。
4. **不改 API 契约、不改后端、不改 services / store / router 的对外行为**。

## 2. 决策摘要

| 维度 | 决策 |
| --- | --- |
| 实施方式 | A — 两个 app 都全量重写页面（页面级重写，service / store / router 不动） |
| 用户端 UI 库 | Naive UI + 自定义 CSS（替换 Vant） |
| 用户端风格 | 现代门户（serif 标题 + sans 正文 + 单一深红 accent，仅浅色） |
| 用户端响应式 | 桌面优先，断点 1200 / 900；手机走单列 + 抽屉导航 |
| 管理后台 UI 库 | 保留 Element Plus，覆盖 CSS 变量；新增 echarts |
| 管理后台风格 | 数据看板，深色侧栏 + 紧凑表格 + 状态 chip + 图表 |
| 鉴权门槛 | 阅读不登录；收藏 / 历史 / 个人中心需要登录（沿用现状） |
| 评论 | 不在本次范围（后端不支持） |
| 黑暗模式 | 不在本次范围 |

## 3. 共享设计系统

两个 app 各自维护一份 `styles/tokens.css`，物理重复，靠本文档保持同步。

### 3.1 颜色（仅浅色）

```
--bg-page         #ffffff
--bg-elevated     #f7f7f5
--bg-muted        #ececea
--border          #e5e5e2
--text-primary    #1a1a1a
--text-secondary  #6b6b6b
--text-muted      #9a9a9a
--accent          #b3261e   /* 深红，链接 / 主按钮 / 高亮 */
--accent-hover    #8e1c17
--success         #2e7d32
--warning         #b45309
--danger          #c62828
```

管理后台侧栏单独使用深色面：`--admin-sidebar-bg: #1f2024`，`--admin-sidebar-text: #d8d8d6`，`--admin-sidebar-active-bg: #2a2b2e`。

### 3.2 字体

- 用户端标题：`'Source Serif 4', 'Noto Serif SC', Georgia, serif`
- 用户端正文：`'Inter', 'PingFang SC', system-ui, sans-serif`
- 管理后台：仅 `'Inter', 'PingFang SC', system-ui, sans-serif`
- 字号阶梯（modular，比例 1.2）：`12 / 14 / 16 / 18 / 20 / 24 / 30 / 36 / 48 / 60` px
- 行高：标题 1.2，正文 1.6，文章正文 1.75

### 3.3 间距

4px 基础：`4 / 8 / 12 / 16 / 20 / 24 / 32 / 48 / 64 / 96`。

### 3.4 栅格与断点

- 用户端最大内容宽度 **1200px**，12 列栅格，gutter 24px
- 管理后台 fluid，侧栏固定 240px
- 用户端断点：
  - `≥1200px` 桌面（完整布局）
  - `900–1199px` 平板（减一列，gutter 缩到 16px）
  - `<900px` 手机（单列，hamburger 抽屉导航，无首页 hero 网格）

## 4. 用户端（frontend/）

### 4.1 全局壳

```
┌─────────────────────────────────────────────────────────┐
│  TOP BAR  sticky 64px 白底底部细边                      │
│  [LOGO 新闻]  首页 分类▾ 热门  [搜索▭]   [👤]          │
├─────────────────────────────────────────────────────────┤
│              MAIN  (max 1200px, centered)               │
├─────────────────────────────────────────────────────────┤
│  FOOTER  浅色三列 + 版权                                │
└─────────────────────────────────────────────────────────┘
```

- LOGO：serif 24px，点击回 `/`
- 主导航：首页 / 分类（来自 `/api/news/categories` 的下拉）/ 热门
- 搜索：图标态可展开为 ~280px 输入框，回车跳 `/search?keyword=...`
- 鉴权位：未登录显示「登录 / 注册」；已登录显示头像下拉（个人中心 / 我的收藏 / 浏览历史 / 退出登录）
- 移动断点 (<900px)：左侧 hamburger 弹出抽屉，包含全部主导航与鉴权入口
- `App.vue` 整体替换：`<TopBar /> <main class="page-container"><router-view/></main> <SiteFooter />`，去掉 `keep-alive`
- `components/TabBar.vue` 删除；`router/index.js` 中所有 `meta.showTabBar` 删除

### 4.2 页面设计

#### 4.2.1 HomePage `/`
- Hero：12 列宽，单条特稿（`/api/news/recommend` 第一条，回退到 `/api/news/hot` 第一条），含大封面 / serif 标题 / 摘要 / 元信息
- 主体两栏：
  - 左 8 列：推荐 feed，2 列卡片（封面 / 标题 / 2 行摘要 / 元信息），底部分页
  - 右 4 列：`HotList`（编号 Top 10，无图）+ `CategoryNav`（chip 列表）
- 数据：`/api/news/recommend`、`/api/news/hot`、`/api/news/categories`

#### 4.2.2 SearchPage `/search`
- 顶部大搜索框 + 历史关键词 chips（localStorage，沿用现状）
- 结果区：单列 list-row（标题命中高亮 / 摘要 / 元信息 / 右侧小缩略图），顶部「共 N 条 · 排序」，底部分页
- 空态：`未找到相关新闻`

#### 4.2.3 NewsDetailPage `/news/:id`
- 文章头（居中 max 760px）：分类 chip · 时间 / H1 标题 serif 36px / 摘要斜体 18px / 作者 · 阅读 N · 收藏 / 分享
- 封面图 max 760px 圆角
- 正文：`max 720px`，serif 正文，`prose.css` 控制段落 / 列表 / 引用 / 图片
- 相关推荐：底部 4 列卡片
  - 后端无 `related-by-id`，使用「按当前文章的 category 调 `/api/news/list` 排除自身」回退；若 category 缺失则用 `/recommend`
- 收藏按钮：未登录点击弹登录 modal；登录后 `POST /api/favorite/add`
- 滚动 600px 后右下浮 `回到顶部`

#### 4.2.4 LoginPage `/login`
- 居中卡片 420px / `--bg-elevated` 背景
- 标题「登录」serif 30px + 副标题
- 表单：用户名 / 密码 / 保持登录 / 主按钮
- 底部「还没有账号？注册」
- 成功后跳 `query.redirect` 或 `/`

#### 4.2.5 RegisterPage `/register`
- 与 Login 结构相同
- 字段：用户名 / 密码 / 确认密码（可选邮箱，需先核对 `services/auth.js` 与 `routers/users.py` 的 schema）
- 行内校验

#### 4.2.6 FavoritesPage `/favorites`
- 标题「我的收藏」+ 排序下拉（最新优先 / 最早优先）+ 「清空」（confirm）
- 2 列网格，每张卡片右上角浮「✕ 移除」
- 空态 + 分页（`/api/favorite/list?page=&pageSize=`）

#### 4.2.7 HistoryPage `/history`
- 与收藏类似，但按日分组（今天 / 昨天 / `yyyy-MM-dd`）
- 每行：时间（左，secondary）+ 标题 + 元信息 + 「删除」
- 顶部「清空历史」（confirm）

#### 4.2.8 ProfilePage `/profile`
- 两栏：
  - 左 4 列：profile 卡片，头像 / 用户名 / gender chip / 注册时间 / 「编辑资料」「修改密码」
  - 右 8 列：3 张 stat 卡（收藏数 / 历史数 / 阅读时长占位）+ 最近浏览 5 条

#### 4.2.9 ProfileEditPage `/profile/edit`
- 居中表单卡 ~560px
- 字段：头像 upload（**若 `/api/user/update` 不接受文件 / 没有上传接口，则降级为 URL 输入**，实施时确认）/ 用户名 / 性别（提交枚举 `male/female/unknown`，展示 男/女/未知）/ 邮箱 / 个性签名
- 提交 `/api/user/update`，成功 toast 后跳 `/profile`

#### 4.2.10 ProfilePasswordPage `/profile/password`
- 居中卡 ~480px，字段：当前密码 / 新密码 / 确认新密码
- 提交 `/api/user/password`

### 4.3 通用组件清单

```
components/layout/TopBar.vue
components/layout/SiteFooter.vue
components/layout/MobileNavDrawer.vue
components/news/NewsCard.vue          # 卡片：封面 + 标题 + 摘要 + 元信息
components/news/NewsListRow.vue       # 长行：标题 + 摘要 + 右缩略图
components/news/HotList.vue           # 编号热门列表
components/news/CategoryNav.vue       # chip 分类导航
components/feedback/EmptyState.vue
components/feedback/LoadingSkeleton.vue
```

### 4.4 依赖变化

```
+ naive-ui
- vant
保留: marked, dompurify, pinia, vue-router, axios, pinia-plugin-persistedstate, vue-i18n
```

## 5. 管理后台（admin-web/）

### 5.1 全局壳

```
┌──────────┬──────────────────────────────────────────────┐
│          │  TOP BAR (56px) — 面包屑 · 头像 · 退出       │
│ SIDEBAR  ├──────────────────────────────────────────────┤
│ 240px    │                                              │
│ #1f2024  │  CONTENT (fluid, padding 24px)              │
│          │                                              │
│ 仪表盘   │                                              │
│ 内容▾    │                                              │
│  └新闻   │                                              │
│  └栏目   │                                              │
│ 用户     │                                              │
└──────────┴──────────────────────────────────────────────┘
```

- 侧栏深色，唯一深色面，标识"管理上下文"
- 当前 active 项：左侧 accent-red 竖条 + 略亮背景
- Login 页不渲染壳（全屏居中卡片）

**Element Plus 主题覆盖** `admin-web/src/styles/element-overrides.css`：

- `--el-color-primary` 替换为 accent
- `el-table` cell padding 12px（默认 16px）
- `el-tag` 状态色绑定到 `--success / --warning / --danger / --text-muted`
- `el-input` `el-select` 高度 32 / 36 px

### 5.2 页面设计

#### 5.2.1 LoginPage `/login`
- 居中卡 420px on `#f7f7f5`，标题「新闻管理后台 · 登录」，无主题切换、无注册

#### 5.2.2 DashboardPage `/`
- Stat 行：6 张紧凑卡片（稿件总数 / 已发布 / 草稿 / 已下线 / 栏目 / 管理员），平板回退 4 列
- 两列下半区：
  - 左 8 列：最近更新表（10 行），列：标题 / 状态 / 作者 / 浏览 / 更新时间，行点击跳编辑
  - 右 4 列：状态分布 donut（published / draft / offline）+ 栏目分布水平 bar（来自 `/api/admin/categories` 的 `news_count`，若返回则显示）
- 图表用 `echarts`，统一 `BaseChart.vue` 包装
- **不显示伪造的趋势 Δ%**：后端无历史端点，相关字段一律省略

#### 5.2.3 NewsManagementPage `/news`
- Toolbar（sticky）：搜索标题 / 状态过滤 / 栏目过滤 / 作者过滤 / 「+ 新建稿件」
- 选中 ≥1 行时显示批量操作：批量发布 / 批量下线 / 批量删除
- 表格：勾选 / 标题（链接到编辑）/ 栏目 / 状态 chip / 浏览 / 更新时间 / 操作（编辑 / 发布或下线 / 删除）
- 状态色：published=success，draft=warning，offline=muted

#### 5.2.4 NewsEditorPage `/news/create`、`/news/:id/edit`
- 顶部条：返回 / 保存草稿 / 发布 / 当前状态显示
- 两栏：
  - 左 8 列：标题大输入 / 摘要 textarea / 正文 markdown 编辑器（textarea + 实时预览 tabs，使用 marked + dompurify）
  - 右 4 列：栏目 select / 作者 input / 封面图 URL + 预览 / 发布时间（自动）
- 保存 `/api/admin/news`（POST）或 `/api/admin/news/:id`（PUT），发布 `/api/admin/news/:id/status`
- 离开未保存校验通过 `beforeRouteLeave`

#### 5.2.5 CategoriesPage `/categories`
- 单栏，简表：名称 / 排序 / 关联稿件数 / 操作
- 顶部「+ 新建栏目」开 modal
- 行内编辑（点击铅笔 → 行变输入框）
- 删除 confirm，若关联稿件数 > 0 给出明确提示

#### 5.2.6 UsersPage `/users`
- Toolbar：用户名搜索 / 角色过滤
- 表格：头像 / 用户名 / 邮箱 / 角色 chip / 注册时间 / 操作（角色下拉：admin / user）
- 改角色 confirm 强调后果（提升或降权）

### 5.3 通用组件清单

```
components/layout/AdminSidebar.vue
components/layout/AdminTopBar.vue
components/charts/BaseChart.vue
components/charts/StatusDonut.vue
components/charts/CategoryBar.vue
components/common/PageToolbar.vue       # sticky 过滤 / 操作条
components/common/StatusChip.vue
```

### 5.4 依赖变化

```
+ echarts
保留: element-plus, @element-plus/icons-vue, pinia, vue-router
```

## 6. 文件改动清单

### frontend/src/
```
NEW    styles/tokens.css
NEW    styles/base.css
NEW    styles/prose.css
NEW    components/layout/{TopBar,SiteFooter,MobileNavDrawer}.vue
NEW    components/news/{NewsCard,NewsListRow,HotList,CategoryNav}.vue
NEW    components/feedback/{EmptyState,LoadingSkeleton}.vue
DEL    components/TabBar.vue
REW    App.vue
REW    views/{HomePage,SearchPage,NewsDetailPage,LoginPage,RegisterPage,FavoritesPage,HistoryPage,ProfilePage,ProfileEditPage,ProfilePasswordPage}.vue
UPD    main.js                                  # 注册 naive-ui，移除 vant
UPD    router/index.js                          # 删除 meta.showTabBar
UNCH   services/, store/, utils/, i18n/         # API / 状态层不动
```

### admin-web/src/
```
NEW    styles/tokens.css
NEW    styles/base.css
NEW    styles/element-overrides.css
NEW    components/layout/{AdminSidebar,AdminTopBar}.vue
NEW    components/charts/{BaseChart,StatusDonut,CategoryBar}.vue
NEW    components/common/{PageToolbar,StatusChip}.vue
REW    views/layout/*
REW    views/{DashboardPage,NewsManagementPage,NewsEditorPage,CategoriesPage,UsersPage}.vue
RES    views/LoginPage.vue                      # 仅样式
UNCH   services/, store/, router/
```

## 7. 测试与验证

- 后端：`conda run -n normal pytest tests -v` 全部通过（无后端改动）
- 前端契约：`node --test frontend/src/services/auth.test.js frontend/src/services/news.test.js frontend/src/services/news-detail.test.js frontend/src/services/profile.test.js frontend/src/utils/profile.test.js` 全部通过
- 构建：`cd frontend && npm run build`、`cd admin-web && npm run build` 均无错误
- 手工联调（按 AGENTS.md §6）：
  1. 注册 → 登录 → 自动 token refresh
  2. 首页（hero / 推荐 / 热门 / 分类）
  3. 搜索（有结果 / 无结果 / 历史关键词）
  4. 详情（登出可读 / 收藏触发登录 / 登录后收藏成功）
  5. 收藏（列表 / 移除 / 清空 / 空态）
  6. 历史（按日分组 / 删除 / 清空 / 空态）
  7. 改资料 / 改密码
  8. 管理后台：登录 → 仪表盘 → 新建/编辑/发布稿件 → 栏目 CRUD → 用户改角色
- 响应式：用户端在 1440 / 1024 / 768 / 375 px 浏览器宽度下逐页验证

## 8. 风险与开放问题

1. **头像上传接口未确认**：实施前先读 `services/profile.js` 与 `routers/users.py`，若无文件上传则降级为头像 URL 输入。
2. **详情页相关推荐**：后端无 `related-by-id`，使用「按 category 取 list 排除自身」回退；若没有 category 字段则降级为 `/api/news/recommend`。
3. **仪表盘趋势**：无历史数据端点，**禁止伪造 Δ%**，统计卡仅显示当前数值。
4. **i18n**：用户端新文案统一加入 `frontend/src/i18n/`；管理后台沿用硬编码 zh-CN（保持现状）。
5. **`keep-alive` 移除**：首页滚动位置不再保留；如需保留位置需另行设计，本次默认放弃。
6. **栏目 `news_count` 字段**：dashboard 栏目分布图依赖此字段。若 `/api/admin/categories` 不返回，需在实施时回退（隐藏图表或临时聚合）。

## 9. 显式不在范围内

- 评论功能（后端无支持）
- 任何后端 trend / stats 端点
- 黑暗模式
- 头像上传后端
- 移动端 App / PWA
- 替换 axios / pinia / vue-router / marked / dompurify
- 重构 `services/` / `store/` / `router/`（除 `meta.showTabBar` 标志移除外）
- 重构后端任何代码

## 10. 后续

本设计批准后进入实施计划阶段（writing-plans skill），按页面 / 模块拆分为可独立 review 的提交批次，建议执行顺序：

1. 共享 tokens & 全局壳（两端各自）
2. 用户端：HomePage → 列表类（Search / Favorites / History）→ Detail → Profile 系列 → Login/Register
3. 管理后台：Dashboard → NewsManagement → NewsEditor → Categories → Users → Login
4. 联调清单全量回归 + 构建验证
