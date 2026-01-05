# Phone-Agent-Web API 文档说明

## 📋 FastAPI 自动生成 API 文档

FastAPI 框架的最大优势之一就是**自动生成交互式 API 文档**，无需手动编写文档。

---

## 一、访问 API 文档

### 1.1 Swagger UI（推荐）

**访问地址：** `http://localhost:5001/docs`

**特性：**
- ✅ 交互式 API 测试界面
- ✅ 在线调试所有接口
- ✅ 自动显示请求/响应模型
- ✅ 支持认证测试
- ✅ 实时查看响应结果

**截图示例：**
```
┌─────────────────────────────────────────────────────────┐
│  Phone-Agent-Web API                          v1.0.0    │
├─────────────────────────────────────────────────────────┤
│  📱 Devices                                             │
│    GET  /api/devices              获取设备列表          │
│    POST /api/devices/connect      连接设备              │
│    POST /api/devices/screenshot   获取截图              │
│    POST /api/devices/action       执行操作              │
│                                                          │
│  📝 Test Cases                                          │
│    GET  /api/testcases            获取用例列表          │
│    POST /api/testcases            创建用例              │
│    GET  /api/testcases/{id}       获取用例详情          │
│    PUT  /api/testcases/{id}       更新用例              │
│    DELETE /api/testcases/{id}     删除用例              │
│                                                          │
│  ▶️  Execution                                          │
│    POST /api/execute              执行测试              │
│    GET  /api/execute/{id}/status  获取执行状态          │
│                                                          │
│  📊 Results                                             │
│    GET  /api/results              获取结果列表          │
│    GET  /api/results/{id}         获取结果详情          │
│    POST /api/results/{id}/report  生成报告              │
└─────────────────────────────────────────────────────────┘
```

### 1.2 ReDoc

**访问地址：** `http://localhost:5001/redoc`

**特性：**
- ✅ 美观的文档展示
- ✅ 更适合阅读和分享
- ✅ 支持搜索功能
- ✅ 响应式设计
- ✅ 可打印/导出

### 1.3 OpenAPI JSON

**访问地址：** `http://localhost:5001/openapi.json`

**用途：**
- 导出 OpenAPI 3.0 规范
- 生成客户端 SDK
- 集成到 Postman/Insomnia
- 自动化测试

---

## 二、FastAPI 应用配置

### 2.1 基础配置

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Phone-Agent-Web API",
    description="""
    ## 自动化测试平台 API
    
    提供设备管理、测试用例管理、执行控制和结果分析的完整 API。
    
    ### 主要功能
    
    * **设备管理** - 设备发现、连接、控制
    * **用例管理** - 创建、编辑、组织测试用例
    * **执行引擎** - 自动化执行测试
    * **结果分析** - 测试报告和数据分析
    
    ### 技术栈
    
    * FastAPI - Web 框架
    * SQLAlchemy - ORM
    * WebSocket - 实时通信
    * AutoGLM - 设备控制
    """,
    version="1.0.0",
    docs_url="/docs",           # Swagger UI 路径
    redoc_url="/redoc",         # ReDoc 路径
    openapi_url="/openapi.json", # OpenAPI JSON 路径
    contact={
        "name": "开发团队",
        "email": "dev@example.com",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2.2 API 标签分组

```python
tags_metadata = [
    {
        "name": "devices",
        "description": "设备管理相关接口",
    },
    {
        "name": "testcases",
        "description": "测试用例管理接口",
    },
    {
        "name": "execution",
        "description": "测试执行控制接口",
    },
    {
        "name": "results",
        "description": "测试结果和报告接口",
    },
]

app = FastAPI(
    openapi_tags=tags_metadata,
    # ... 其他配置
)
```

---

## 三、Pydantic 模型定义

### 3.1 请求/响应模型

FastAPI 使用 Pydantic 模型自动生成文档和验证数据。

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# 枚举类型
class Platform(str, Enum):
    """设备平台"""
    IOS = "ios"
    ANDROID = "android"

class DeviceStatus(str, Enum):
    """设备状态"""
    ONLINE = "online"
    OFFLINE = "offline"

# 设备模型
class Device(BaseModel):
    """设备信息"""
    device_id: str = Field(..., description="设备唯一标识")
    name: str = Field(..., description="设备名称", example="iPhone12")
    platform: Platform = Field(..., description="设备平台")
    status: DeviceStatus = Field(..., description="设备状态")
    model: Optional[str] = Field(None, description="设备型号", example="iPhone12,1")
    connection_type: str = Field(..., description="连接类型", example="usb")
    
    class Config:
        schema_extra = {
            "example": {
                "device_id": "00008101-001D059E0481401E",
                "name": "iPhone12",
                "platform": "ios",
                "status": "online",
                "model": "iPhone12,1",
                "connection_type": "usb"
            }
        }

# 测试步骤模型
class TestStep(BaseModel):
    """测试步骤"""
    type: str = Field(..., description="步骤类型", example="action")
    action: Optional[str] = Field(None, description="动作类型", example="tap")
    params: Optional[dict] = Field(None, description="动作参数", example={"x": 100, "y": 200})
    description: Optional[str] = Field(None, description="步骤描述", example="点击登录按钮")
    timeout: int = Field(5, description="超时时间（秒）", ge=1, le=300)
    screenshot_before: bool = Field(False, description="执行前截图")
    screenshot_after: bool = Field(False, description="执行后截图")

# 测试用例模型
class TestCase(BaseModel):
    """测试用例"""
    id: Optional[str] = Field(None, description="用例 ID")
    name: str = Field(..., description="用例名称", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="用例描述")
    platform: Platform = Field(..., description="目标平台")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    steps: List[TestStep] = Field(..., description="测试步骤列表", min_items=1)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "登录测试",
                "description": "测试用户登录功能",
                "platform": "ios",
                "tags": ["登录", "冒烟测试"],
                "steps": [
                    {
                        "type": "action",
                        "action": "tap",
                        "params": {"x": 100, "y": 200},
                        "description": "点击登录按钮",
                        "screenshot_after": True
                    }
                ]
            }
        }
```

### 3.2 响应模型

```python
from typing import Generic, TypeVar

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    """统一响应格式"""
    success: bool = Field(..., description="请求是否成功")
    message: Optional[str] = Field(None, description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")

class DeviceListResponse(BaseModel):
    """设备列表响应"""
    devices: List[Device] = Field(..., description="设备列表")
    total: int = Field(..., description="设备总数")

class TestCaseCreateResponse(BaseModel):
    """创建用例响应"""
    id: str = Field(..., description="用例 ID")
    success: bool = Field(..., description="是否成功")
```

---

## 四、接口文档示例

### 4.1 设备管理接口

```python
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/devices", tags=["devices"])

@router.get(
    "",
    response_model=DeviceListResponse,
    summary="获取设备列表",
    description="获取所有已连接的设备列表，包括 iOS 和 Android 设备",
    responses={
        200: {
            "description": "成功获取设备列表",
            "content": {
                "application/json": {
                    "example": {
                        "devices": [
                            {
                                "device_id": "00008101-001D059E0481401E",
                                "name": "iPhone12",
                                "platform": "ios",
                                "status": "online",
                                "model": "iPhone12,1",
                                "connection_type": "usb"
                            }
                        ],
                        "total": 1
                    }
                }
            }
        }
    }
)
async def list_devices():
    """
    获取所有已连接的设备列表
    
    返回当前系统中所有可用的设备，包括：
    - iOS 设备（通过 WebDriverAgent）
    - Android 设备（通过 ADB）
    
    设备状态：
    - online: 设备在线且可用
    - offline: 设备连接但不可用
    """
    devices = device_manager.get_devices()
    return DeviceListResponse(devices=devices, total=len(devices))

@router.post(
    "/screenshot",
    response_model=ScreenshotResponse,
    summary="获取设备截图",
    description="获取指定设备的当前屏幕截图",
    responses={
        200: {"description": "成功获取截图"},
        404: {"description": "设备不存在"},
        500: {"description": "截图失败"}
    }
)
async def take_screenshot(request: ScreenshotRequest):
    """
    获取设备截图
    
    Args:
        request: 包含 device_id 的请求
    
    Returns:
        ScreenshotResponse: 截图数据（base64 编码）
    
    Raises:
        HTTPException: 设备不存在或截图失败
    """
    try:
        screenshot = device_manager.get_screenshot(request.device_id)
        return ScreenshotResponse(
            success=True,
            image=screenshot.base64_data,
            width=screenshot.width,
            height=screenshot.height
        )
    except DeviceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {request.device_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Screenshot failed: {str(e)}"
        )
```

### 4.2 测试用例接口

```python
router = APIRouter(prefix="/api/testcases", tags=["testcases"])

@router.post(
    "",
    response_model=TestCaseCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建测试用例",
    description="创建新的测试用例"
)
async def create_test_case(test_case: TestCase):
    """
    创建新的测试用例
    
    Args:
        test_case: 测试用例数据
    
    Returns:
        TestCaseCreateResponse: 创建结果（包含用例 ID）
    
    Example:
        ```json
        {
            "name": "登录测试",
            "description": "测试用户登录功能",
            "platform": "ios",
            "tags": ["登录", "冒烟测试"],
            "steps": [
                {
                    "type": "action",
                    "action": "tap",
                    "params": {"x": 100, "y": 200},
                    "description": "点击登录按钮"
                }
            ]
        }
        ```
    """
    case_id = test_case_manager.create(test_case)
    return TestCaseCreateResponse(id=case_id, success=True)

@router.get(
    "",
    response_model=TestCaseListResponse,
    summary="获取测试用例列表",
    description="获取测试用例列表，支持分页和过滤"
)
async def list_test_cases(
    platform: Optional[Platform] = None,
    tag: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    获取测试用例列表
    
    Args:
        platform: 平台过滤（ios/android）
        tag: 标签过滤
        skip: 跳过数量（分页）
        limit: 返回数量（分页）
    
    Returns:
        TestCaseListResponse: 用例列表
    """
    cases = test_case_manager.list(
        platform=platform,
        tag=tag,
        skip=skip,
        limit=limit
    )
    return TestCaseListResponse(testcases=cases, total=len(cases))
```

---

## 五、前端使用 API 文档

### 5.1 TypeScript 类型生成

使用 `openapi-typescript` 自动生成 TypeScript 类型：

```bash
# 安装工具
npm install -D openapi-typescript

# 生成类型定义
npx openapi-typescript http://localhost:5001/openapi.json -o src/types/api.ts
```

生成的类型文件：

```typescript
// src/types/api.ts
export interface paths {
  "/api/devices": {
    get: {
      responses: {
        200: {
          content: {
            "application/json": {
              devices: components["schemas"]["Device"][];
              total: number;
            };
          };
        };
      };
    };
  };
  // ... 其他接口
}

export interface components {
  schemas: {
    Device: {
      device_id: string;
      name: string;
      platform: "ios" | "android";
      status: "online" | "offline";
      model?: string;
      connection_type: string;
    };
    // ... 其他模型
  };
}
```

### 5.2 API 客户端封装

```typescript
// src/api/client.ts
import axios from 'axios';
import type { components } from '@/types/api';

type Device = components['schemas']['Device'];
type TestCase = components['schemas']['TestCase'];

const client = axios.create({
  baseURL: 'http://localhost:5001',
  timeout: 10000,
});

export const deviceAPI = {
  list: async () => {
    const { data } = await client.get<{ devices: Device[]; total: number }>('/api/devices');
    return data;
  },
  
  screenshot: async (deviceId: string) => {
    const { data } = await client.post('/api/devices/screenshot', { device_id: deviceId });
    return data;
  },
};

export const testCaseAPI = {
  list: async (params?: { platform?: string; tag?: string }) => {
    const { data } = await client.get('/api/testcases', { params });
    return data;
  },
  
  create: async (testCase: TestCase) => {
    const { data } = await client.post('/api/testcases', testCase);
    return data;
  },
};
```

---

## 六、API 文档最佳实践

### 6.1 文档注释规范

```python
@router.post("/api/execute")
async def execute_test(request: ExecuteRequest):
    """
    执行测试用例
    
    执行指定的测试用例，支持实时进度推送。
    
    Args:
        request: 执行请求
            - test_case_id: 测试用例 ID
            - device_id: 目标设备 ID
    
    Returns:
        ExecuteResponse: 执行结果
            - execution_id: 执行 ID
            - status: 执行状态
    
    Raises:
        HTTPException:
            - 404: 用例或设备不存在
            - 409: 设备正在执行其他任务
            - 500: 执行失败
    
    Example:
        Request:
        ```json
        {
            "test_case_id": "uuid-123",
            "device_id": "00008101-001D059E0481401E"
        }
        ```
        
        Response:
        ```json
        {
            "execution_id": "uuid-456",
            "status": "running"
        }
        ```
    """
    pass
```

### 6.2 错误响应标准化

```python
from fastapi import HTTPException, status
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    detail: Optional[dict] = Field(None, description="详细信息")

# 统一错误处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.status_code,
            message=exc.detail
        ).dict()
    )
```

### 6.3 版本控制

```python
from fastapi import APIRouter

# v1 API
v1_router = APIRouter(prefix="/api/v1")

@v1_router.get("/devices")
async def list_devices_v1():
    """V1 版本的设备列表接口"""
    pass

# v2 API
v2_router = APIRouter(prefix="/api/v2")

@v2_router.get("/devices")
async def list_devices_v2():
    """V2 版本的设备列表接口（增强版）"""
    pass

app.include_router(v1_router)
app.include_router(v2_router)
```

---

## 七、导出和分享

### 7.1 导出 OpenAPI 规范

```bash
# 导出 JSON
curl http://localhost:5001/openapi.json > openapi.json

# 导出 YAML
pip install pyyaml
python -c "import yaml, json; yaml.dump(json.load(open('openapi.json')), open('openapi.yaml', 'w'))"
```

### 7.2 导入到 Postman

1. 打开 Postman
2. Import → Link → 输入 `http://localhost:5001/openapi.json`
3. 自动生成完整的 API 集合

### 7.3 生成客户端 SDK

```bash
# 安装 openapi-generator
npm install -g @openapitools/openapi-generator-cli

# 生成 Python 客户端
openapi-generator-cli generate \
  -i http://localhost:5001/openapi.json \
  -g python \
  -o ./client-python

# 生成 JavaScript 客户端
openapi-generator-cli generate \
  -i http://localhost:5001/openapi.json \
  -g javascript \
  -o ./client-js
```

---

## 八、总结

### FastAPI API 文档的优势

1. ✅ **零配置** - 自动生成，无需手动编写
2. ✅ **类型安全** - Pydantic 模型自动验证
3. ✅ **交互式** - Swagger UI 支持在线测试
4. ✅ **标准化** - 遵循 OpenAPI 3.0 规范
5. ✅ **易于维护** - 代码即文档，同步更新
6. ✅ **多格式** - 支持 Swagger、ReDoc、JSON
7. ✅ **可扩展** - 支持自定义主题和插件

### 推荐工作流

1. **开发阶段** - 使用 Swagger UI 测试接口
2. **前端对接** - 导出 TypeScript 类型定义
3. **文档分享** - 使用 ReDoc 生成美观文档
4. **自动化测试** - 导入 Postman 进行接口测试
5. **客户端开发** - 使用 openapi-generator 生成 SDK

---

**文档版本：v1.0**  
**更新日期：2026-01-05**
