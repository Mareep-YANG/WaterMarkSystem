# 文本水印系统

基于Vue3和FastAPI的文本水印系统，支持多种水印算法，包括DIP、EWD、SIR、SynthID和SemStamp等。

## 功能特性

- 多种文本水印算法支持
- 水印嵌入和检测
- 算法性能评估
- 攻击测试
- API接口支持
- 用户认证系统

## 技术栈

### 前端
- Vue 3
- TypeScript
- Element Plus
- Vue Router
- Pinia
- ECharts

### 后端
- Python FastAPI
- SQLAlchemy
- Transformers
- PyJWT
- PostgreSQL

## 开发环境要求

- Node.js >= 16.x
- Python >= 3.9
- PostgreSQL >= 12
- CUDA支持（可选，用于GPU加速）

## 安装步骤

1. 克隆项目:
```bash
git clone <repository-url>
cd WaterMarkSystem
```

2. 后端设置:
```bash
# 创建Python虚拟环境
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/MacOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
# 创建.env文件并设置必要的环境变量，例如：
# DATABASE_URL=postgresql://user:password@localhost:5432/watermark
# SECRET_KEY=your-secret-key
# etc.

# 初始化数据库
alembic upgrade head
```

3. 前端设置:
```bash
cd frontend
npm install
```

## 运行开发环境

1. 启动后端服务:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. 启动前端服务:
```bash
cd frontend
npm run dev
```

访问 http://localhost:3000 查看应用。

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看Swagger API文档。

## 主要功能使用说明

### 水印处理
1. 登录系统
2. 进入水印处理页面
3. 选择水印算法
4. 输入文本和密钥
5. 点击"嵌入水印"进行处理
6. 使用"检测水印"功能验证

### 评估功能
1. 进入评估页面
2. 输入原始文本和水印文本
3. 选择评估指标
4. 查看评估结果和可视化数据

### API使用
1. 在个人中心创建API密钥
2. 使用API密钥访问系统API
3. 参考API文档进行集成

## 安全说明

- 所有API请求需要认证
- 密码使用bcrypt加密存储
- JWT用于用户会话管理
- 支持API密钥认证

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 发起Pull Request

## 许可证

[MIT License](LICENSE)