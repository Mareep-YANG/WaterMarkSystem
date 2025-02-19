# 文本水印系统架构设计

## 1. 系统概述

本系统是一个基于Web的文本水印处理平台,集成多种水印算法,支持文本水印的嵌入、检测和评估,并提供可视化呈现。系统采用前后端分离架构,提供标准化API接口。

## 2. 系统架构

### 2.1 整体架构
```
+------------------+     +-------------------+     +------------------+
|                  |     |                   |     |                  |
|  前端(Vue3)      |<--->|  后端(FastAPI)    |<--->|  LLM推理服务     |
|                  |     |                   |     |                  |
+------------------+     +-------------------+     +------------------+
                              |
                              |
                        +-----v-----+
                        |           |
                        |  数据库    |
                        |           |
                        +-----------+
```

### 2.2 主要模块

#### 2.2.1 核心模块(Core)
- LLMService: 基于transformers的模型加载与推理
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, LogitsProcessor

class LLMService:
    def __init__(self, model_name: str):
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.processors = []

    def add_logits_processor(self, processor: LogitsProcessor):
        self.processors.append(processor)

    def generate(self, prompt: str, **kwargs):
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            logits_processor=self.processors,
            **kwargs
        )
        return self.tokenizer.decode(outputs[0])
```

- WatermarkBase: 水印算法基类
- LogitsProcessor: transformers的logits处理器实现
```python
from typing import List
import torch
from transformers import LogitsProcessor

class WatermarkLogitsProcessor(LogitsProcessor):
    def __init__(self, watermark, key: str):
        self.watermark = watermark
        self.key = key

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        # 在这里实现水印算法的logits处理逻辑
        return self.watermark.process_logits(scores, input_ids, self.key)
```

#### 2.2.2 水印算法模块(Watermarks)
```python
class WatermarkBase:
    """水印算法基类"""
    def embed(self, text_or_logits, key, **kwargs):
        """嵌入水印"""
        pass
    
    def detect(self, text, key, **kwargs):
        """检测水印"""
        pass
    
    def visualize(self, text, detection_result, **kwargs):
        """可视化"""
        pass
```

- LogitsWatermark(继承WatermarkBase)
  - DIPWatermark
  - EWDWatermark 
  - SIRWatermark
  - SynthIDWatermark
  
- SemanticWatermark(继承WatermarkBase)
  - SemStampWatermark

#### 2.2.3 评估模块(Evaluation)
- Metrics
  - 安全性评估
  - 鲁棒性评估
  - 文本质量评估
- Attack
  - TextAttack: 文本层面攻击
  - SemanticAttack: 语义层面攻击
  - LogitsAttack: Logits层面攻击

#### 2.2.4 认证模块(Auth)
- JWT认证
- 用户管理
- 权限控制
- API密钥管理

### 2.3 API设计

#### 2.3.1 认证API
```
POST /api/auth/register     # 用户注册
POST /api/auth/login       # 用户登录
POST /api/auth/refresh     # 刷新token
```

#### 2.3.2 水印API
```
POST /api/watermark/embed      # 嵌入水印
POST /api/watermark/detect     # 检测水印
GET  /api/watermark/algorithms # 获取支持的算法列表
POST /api/watermark/visualize  # 获取可视化数据
```

#### 2.3.3 评估API
```
POST /api/evaluate/security    # 安全性评估
POST /api/evaluate/robustness  # 鲁棒性评估
POST /api/evaluate/quality     # 文本质量评估
POST /api/evaluate/attack      # 攻击测试
```

#### 2.3.4 LLM API(OpenAI格式)
```
POST /v1/chat/completions     # 对话补全
POST /v1/completions         # 文本补全
```

## 3. 数据库设计

### 3.1 用户表(users)
```sql
CREATE TABLE users (
    id          UUID PRIMARY KEY,
    username    VARCHAR(50) UNIQUE NOT NULL,
    password    VARCHAR(100) NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 API密钥表(api_keys)
```sql
CREATE TABLE api_keys (
    id          UUID PRIMARY KEY,
    user_id     UUID REFERENCES users(id),
    key_value   VARCHAR(100) UNIQUE NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at  TIMESTAMP
);
```

### 3.3 水印记录表(watermark_records)
```sql
CREATE TABLE watermark_records (
    id              UUID PRIMARY KEY,
    user_id         UUID REFERENCES users(id),
    algorithm_name  VARCHAR(50) NOT NULL,
    text_hash       VARCHAR(64) NOT NULL,
    params          JSONB,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. 安全设计

### 4.1 认证安全
- 使用JWT进行身份认证
- Token定期轮换
- 密码加密存储
- API请求限流

### 4.2 数据安全
- 数据传输加密(HTTPS)
- 敏感数据加密存储
- 定期数据备份
- 访问日志记录

### 4.3 接口安全
- 参数校验
- SQL注入防护
- XSS防护
- CSRF防护

## 5. 部署架构

### 开发环境
```
前端: localhost:3000
后端: localhost:8000
数据库: localhost:5432
```

### 5.1 依赖服务
- PostgreSQL: 主数据库
- Redis: 缓存和速率限制
- NGINX: 反向代理

### 5.2 目录结构
```
watermark-system/
├── frontend/            # Vue3前端
├── backend/             # FastAPI后端
│   ├── app/
│   │   ├── core/       # 核心功能
│   │   ├── models/     # 数据模型
│   │   ├── api/        # API路由
│   │   ├── watermarks/ # 水印算法
│   │   └── utils/      # 工具函数
│   ├── tests/          # 测试用例
│   └── alembic/        # 数据库迁移
└── docs/               # 文档
```

## 6. 后续优化方向

### 6.1 性能优化
- LLM推理性能优化
- 水印算法并行处理
- 数据库查询优化
- 缓存策略优化

### 6.2 功能扩展
- 支持更多水印算法
- 增强可视化功能
- 批量处理能力
- 更多评估指标

### 6.3 运维支持
- 监控告警
- 日志分析
- 自动化部署
- 容器化支持