# 文本水印系统

一个功能全面的文本水印系统，基于Vue 3前端和FastAPI后端，支持多种主流水印算法，用于LLM文本水印的嵌入、检测和评估。

## 📋 功能特性

- **多种文本水印算法**：支持DIP、EWD、SIR、SynthID、SemStamp等多种主流水印算法
- **完整的水印处理流程**：水印嵌入、检测和可视化分析
- **算法性能评估**：支持各项指标的性能评估和对比
- **攻击测试与鲁棒性分析**：提供多种攻击测试方法
- **高性能API接口**：支持批量处理和异步任务
- **完善的用户认证系统**：基于JWT的安全认证

## 🛠️ 技术栈

### 前端
- **框架**：Vue 3 + TypeScript
- **UI组件库**：Element Plus
- **状态管理**：Pinia
- **路由**：Vue Router
- **数据可视化**：ECharts
- **构建工具**：Vite

### 后端
- **框架**：Python FastAPI
- **ORM**：Tortoise-ORM
- **人工智能**：PyTorch + Transformers
- **认证**：PyJWT
- **数据库**：MySQL
- **异步任务管理**：内置异步任务系统

## 💻 开发环境要求

- **Node.js** >= 16.x
- **Python** >= 3.9
- **MySQL** >= 8.0
- **CUDA支持**（可选，用于GPU加速）

## 🚀 安装与部署

### 1. 克隆项目

```bash
git clone <repository-url>
cd WaterMarkSystem
```

### 2. 后端设置

```bash
# 创建Python虚拟环境
cd backend
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 创建.env文件并设置必要的环境变量

# 初始化数据库
alembic upgrade head
```

### 3. 前端设置

```bash
cd frontend
npm install
```

## 🖥️ 运行项目

### 1. 启动后端服务

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 2. 启动前端服务

```bash
cd frontend
npm run dev
```

服务启动后，访问 http://localhost:3000 查看应用。

## 📚 API文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的Swagger API文档。

## 🔍 主要功能使用说明

### 水印处理

1. 登录系统
2. 进入水印处理页面
3. 从支持的算法列表中选择所需水印算法
4. 输入待处理文本和密钥
5. 点击"嵌入水印"进行处理
6. 使用"检测水印"功能验证水印效果

### 性能评估

1. 进入评估页面
2. 输入原始文本和带水印文本
3. 选择评估指标（如流畅度、语义保持度等）
4. 查看评估结果和可视化数据

### API使用

1. 在个人中心创建API密钥
2. 使用API密钥访问系统提供的各项API服务
3. 参考API文档进行集成开发

## 🔐 安全说明

- 所有API请求需要认证
- 密码采用bcrypt加密存储
- 用户会话管理基于JWT
- 支持API密钥认证机制

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

[MIT License](LICENSE)