# News User MVP Contract

## 前端开发地址

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`

## 代理规则

- Vite 开发环境将 `/api` 代理到 `http://127.0.0.1:8000`

## 鉴权约定

- 请求头: `Authorization: Bearer <token>`
- 未登录或 token 非法时，后端返回 `401`
- 前端收到 `401` 后会清空本地登录态并跳转 `/login`

## 通用响应结构

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 页面与接口映射

### 登录页 `/login`

- `POST /api/user/login`

### 注册页 `/register`

- `POST /api/user/register`

### 首页 `/`

- `GET /api/news/categories`
- `GET /api/news/list?categoryId&page&pageSize`

### 详情页 `/news/:id`

- `GET /api/news/detail?id`
- `POST /api/history/add`
- `GET /api/favorite/check?newsId`
- `POST /api/favorite/add`
- `DELETE /api/favorite/remove?newsId`

### 收藏页 `/favorites`

- `GET /api/favorite/list?page&pageSize`
- `DELETE /api/favorite/clear`

### 历史页 `/history`

- `GET /api/history/list?page&pageSize`
- `DELETE /api/history/delete/{history_id}`
- `DELETE /api/history/clear`

### 个人中心 `/profile`

- `GET /api/user/info`

### 编辑资料 `/profile/edit`

- `PUT /api/user/update`

### 修改密码 `/profile/password`

- `PUT /api/user/password`

## 关键字段约定

- 新闻分类参数: `categoryId`
- 分页参数: `page`, `pageSize`
- 收藏参数: `newsId`
- 历史列表删除键: `historyId`
- 列表分页标记: `hasMore`

## 当前未覆盖能力

- 退出登录接口
- token 刷新
- 搜索
- 后台管理
