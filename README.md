# 📚 SL-Platform 家教课时管理系统

一个完整可运行的家教课时管理系统，采用**家长-学生分离**的业务模型。家长账号可绑定多个孩子（Student 档案），所有课时包和上课记录归属于具体 Student。系统包含管理端、教师端、家长端三个前端入口，共享同一后端 API。

## 业务模型

```
User (账号) ──≠ Student (学生档案)
  │                  │
  ├─ admin           │ 每个 Student 必须关联一个 role=parent 的 User
  ├─ teacher ─── 多对多 ──┘
  └─ parent ── 一对多 ── Student ── 一对多 ── Package (课时包)
                                    ── 一对多 ── LessonRecord (上课记录)
```

- **管理员** 创建家长账号 → 创建学生档案（关联家长） → 分配师生 → 购买课时包 → 审核上课记录
- **教师** 为分配到的学生创建上课记录 → 管理员审核通过 → 自动扣减课时
- **家长** 查看名下孩子列表 → 查看课时明细、上课记录、授课教师

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.10+ / FastAPI |
| ORM | SQLAlchemy 2.0 (异步) |
| 数据库 | MySQL 8.0 |
| 认证 | JWT (python-jose) + bcrypt |
| 前端框架 | Vue 3 + TypeScript + Vite |
| UI 库 | Element Plus |
| 状态管理 | Pinia |
| HTTP 客户端 | Axios |
| Excel 导出 | openpyxl |

## 项目结构

```
SL-Platform/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置（数据库、JWT等）
│   │   ├── database.py          # 异步数据库引擎
│   │   ├── models/              # ORM 模型（8张表）
│   │   ├── schemas/             # Pydantic 请求/响应模型
│   │   ├── api/                 # 路由处理（auth/admin/teacher/parent）
│   │   ├── services/            # 业务逻辑层
│   │   └── utils/               # 工具（JWT、权限、响应）
│   ├── init_db.sql              # 数据库初始化脚本
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.ts              # 前端入口
│   │   ├── App.vue
│   │   ├── router/              # 路由配置 + 守卫
│   │   ├── stores/              # Pinia 状态管理
│   │   ├── api/                 # Axios API 封装
│   │   ├── layouts/             # 布局组件（3套）
│   │   └── views/               # 页面组件
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 快速开始

### 1. 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Git (可选)

### 2. 数据库初始化

```bash
# 登录 MySQL，执行初始化脚本
mysql -u root -p < backend/init_db.sql
```

脚本将自动：
- 创建 `sl_platform` 数据库
- 创建 8 张业务表
- 插入初始测试数据

### 3. 后端配置

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 修改数据库连接配置（如需）
# 编辑 app/config.py，修改 DB_USER、DB_PASSWORD 等
# 或通过环境变量设置：
# export DB_HOST=127.0.0.1
# export DB_PORT=3306
# export DB_USER=root
# export DB_PASSWORD=your_password
# export DB_NAME=sl_platform

# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. 前端配置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端开发服务器运行在 http://localhost:5173，自动代理 `/api` 到后端。

### 5. 登录测试

打开浏览器访问 http://localhost:5173，使用以下测试账号登录：

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 超级管理员 | `root` | `root123` | 全部权限，仅服务器可修改 |
| 教师 | `teacher1` | `teacher123` | 查看学生、创建记录 |
| 家长 | `parent1` | `parent123` | 查看孩子课时明细 |

## 核心业务流程

### 审批通过的课时扣减（FIFO）

```
1. 管理员点击"通过审核"
2. 开启数据库事务
3. 锁定记录行 → 更新 status='approved'
4. 查找同学生+同课程类型的有效课时包
   → 按 expire_date ASC 排序（先到期先扣）
   → FOR UPDATE 锁定所有相关课时包行
5. 依次扣减课时（FIFO）
6. 若课时不足 → 回滚事务，返回错误
7. 若扣减成功 → 提交事务 → 发送通知给教师
```

## API 概览

### 认证接口 `/api/auth`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /login | 用户登录 |
| GET | /me | 当前用户信息 |

### 管理端 `/api/admin`（需 admin 角色）
- `CRUD /users` — 用户管理（支持角色过滤）
- `CRUD /students` — 学生档案管理
- `CRUD /teacher-students` — 师生分配
- `CRUD /course-types` — 课程类型管理
- `GET/POST /packages` — 课时包管理
- `PUT /packages/{id}` — 手动调整课时包
- `GET /records/pending` — 待审核记录
- `PUT /records/{id}/approve` — ★ 通过审核
- `PUT /records/{id}/reject` — 驳回
- `GET /statistics/overview` — 统计概览
- `GET /statistics/export` — Excel 导出

### 教师端 `/api/teacher`（需 teacher 角色）
- `GET /course-types` — 课程类型列表
- `GET /students` — 我的学生
- `POST /records` — 创建上课记录
- `GET /records` — 我的记录（分页+筛选）
- `GET /statistics` — 个人统计

### 家长端 `/api/parent`（需 parent 角色）
- `GET /children` — 我的孩子列表
- `GET /children/{id}/packages` — 孩子课时明细
- `GET /children/{id}/records` — 孩子上课记录
- `GET /children/{id}/teachers` — 孩子分配的教师
- `GET /notifications` — 我的通知

## 统一响应格式

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

## 数据库表结构

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `user` | 用户表 | role ENUM('admin','teacher','parent') |
| `teacher` | 教师扩展 | user_id FK, subject, bio |
| `student` | 学生档案 | parent_user_id FK (必填) |
| `teacher_student` | 师生分配 | UNIQUE(teacher_id, student_id) |
| `course_type` | 课程类型 | name, default_hourly_rate |
| `package` | 课时包 | student_id FK, 按 expire_date FIFO 扣减 |
| `lesson_record` | 上课记录 | 审批通过后触发课时扣减 |
| `notification` | 站内通知 | user_id FK |

## 生产部署建议

1. 修改 `app/config.py` 中的 JWT_SECRET_KEY 为随机字符串
2. 设置 `DEBUG=false`
3. 使用 Gunicorn + Uvicorn workers 部署后端
4. 前端执行 `npm run build`，将 `dist/` 部署到 Nginx
5. 配置 Nginx 反向代理，统一前后端端口
6. 数据库使用独立的 MySQL 用户，设置强密码
7. 定期备份数据库

## License

MIT
