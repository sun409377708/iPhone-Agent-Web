# Phone-Agent-Web UI 设计规范

> 自动化测试平台前端设计指南 - 基于现代化设计系统

## 📋 目录

- [技术栈](#技术栈)
- [整体布局](#整体布局)
- [配色方案](#配色方案)
- [页面设计](#页面设计)
- [组件规范](#组件规范)
- [用户流程](#用户流程)
- [开发指南](#开发指南)

---

## 🎨 技术栈

### 核心技术

```json
{
  "框架": "Vue 3.4+ (纯 JavaScript)",
  "路由": "Vue Router 4",
  "样式": "TailwindCSS 4.x",
  "组件库": "shadcn-vue (基于 Radix Vue)",
  "图标": "Lucide Vue Next",
  "图表": "Vue-ECharts",
  "状态管理": "Pinia",
  "数据请求": "TanStack Query Vue (VueQuery)",
  "实时通信": "Socket.IO Client",
  "构建工具": "Vite"
}
```

> **说明：不使用 TypeScript**，使用纯 JavaScript 开发，降低学习成本。

### 现有代码情况

**当前架构（v0.1）：**
- 后端：Flask + SQLAlchemy
- 前端：纯 HTML + 原生 JavaScript
- 单页面应用，无需构建工具

**迁移方案：**
1. **短期**：保持现有 HTML/JS，继续开发
2. **中期**：新建 Vue 项目，逐页迁移
3. **长期**：完全切换到 Vue

---

### 为什么选择 Vue 技术栈？

| 技术 | 优势 |
|------|------|
| **TailwindCSS** | 原子化 CSS，快速开发，文件体积小，易于维护 |
| **shadcn-vue** | 可复制组件，完全可定制，不是 npm 依赖 |
| **Radix Vue** | 无障碍访问，键盘导航，完美交互体验 |
| **OKLCH 色彩** | 现代色彩空间，色彩更准确，过渡更自然 |
| **Lucide Vue** | 现代图标库，一致的设计风格，轻量级 |
| **VueQuery** | 强大的数据同步，自动缓存，乐观更新 |

---

## 🏗️ 整体布局

### 布局结构

```
┌─────────────────────────────────────────────────────────────────┐
│  Header (固定顶部 - 64px)                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 📱 Phone-Agent-Web  [设备] [用例] [执行] [结果] [🌙][🌐]│   │
│  └──────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────┬──────────────────────────────────────────────┐  │
│  │            │                                               │  │
│  │  Sidebar   │           Main Content Area                  │  │
│  │  (240px)   │           (flex-1, 可滚动)                   │  │
│  │            │                                               │  │
│  │  📱 设备   │                                               │  │
│  │  📝 用例   │                                               │  │
│  │  ▶️  执行   │                                               │  │
│  │  📊 结果   │                                               │  │
│  │  ⚙️  设置   │                                               │  │
│  │            │                                               │  │
│  └────────────┴──────────────────────────────────────────────┘  │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  Footer (固定底部 - 48px)                                       │
│  v1.0.0  |  中文/English  |  GitHub  |  API 文档               │
└─────────────────────────────────────────────────────────────────┘
```

### 响应式断点

```css
/* TailwindCSS 默认断点 */
sm: 640px   /* 小屏幕 */
md: 768px   /* 平板 */
lg: 1024px  /* 笔记本 */
xl: 1280px  /* 桌面 */
2xl: 1536px /* 大屏 */

/* 布局适配 */
- 移动端 (< 768px): 隐藏侧边栏，使用底部导航
- 平板 (768px - 1024px): 可折叠侧边栏
- 桌面 (> 1024px): 固定侧边栏
```

---

## 🎨 配色方案

### 主色调 - 活力橙 (#FF8800)

```css
/* 主色调 */
:root {
  --primary: #FF8800;           /* 主要按钮、链接 */
  --primary-hover: #E67700;     /* 悬停状态 */
  --primary-active: #CC6600;    /* 激活状态 */
  --primary-light: #FFB366;     /* 浅色变体 */
  --primary-dark: #B35F00;      /* 深色变体 */
}

/* OKLCH 格式（推荐） */
:root {
  --primary: oklch(0.72 0.18 50);           /* #FF8800 */
  --primary-hover: oklch(0.65 0.18 50);     /* 悬停 */
  --primary-light: oklch(0.80 0.12 50);     /* 浅色 */
}
```

### 完整配色系统

```css
:root {
  /* 主色调 - 活力橙 */
  --primary: oklch(0.72 0.18 50);
  --primary-foreground: oklch(1 0 0);
  
  /* 状态色 */
  --success: oklch(0.65 0.15 145);    /* 绿色 #10B981 */
  --warning: oklch(0.75 0.15 85);     /* 黄色 #F59E0B */
  --error: oklch(0.63 0.22 25);       /* 红色 #EF4444 */
  --info: oklch(0.60 0.18 250);       /* 蓝色 #3B82F6 */
  
  /* 背景色 */
  --background: oklch(1 0 0);         /* 白色 */
  --foreground: oklch(0.13 0.04 265); /* 深灰 */
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.13 0.04 265);
  
  /* 次级色 */
  --secondary: oklch(0.97 0.01 248);
  --secondary-foreground: oklch(0.21 0.04 266);
  --muted: oklch(0.97 0.01 248);
  --muted-foreground: oklch(0.55 0.05 257);
  --accent: oklch(0.97 0.01 248);
  --accent-foreground: oklch(0.21 0.04 266);
  
  /* 边框和输入 */
  --border: oklch(0.93 0.01 256);
  --input: oklch(0.93 0.01 256);
  --ring: oklch(0.70 0.04 257);
  
  /* 圆角 */
  --radius: 0.625rem;  /* 10px */
}

/* 暗黑模式 */
.dark {
  --background: oklch(0.13 0.04 265);
  --foreground: oklch(0.98 0.00 248);
  --card: oklch(0.21 0.04 266);
  --card-foreground: oklch(0.98 0.00 248);
  
  --primary: oklch(0.72 0.18 50);     /* 橙色在暗黑模式下保持 */
  --primary-foreground: oklch(0.13 0.04 265);
  
  --border: oklch(1 0 0 / 10%);
  --input: oklch(1 0 0 / 15%);
}
```

### 语义化颜色

```css
/* 设备状态 */
.status-online {
  @apply bg-success shadow-[0_0_8px_rgba(16,185,129,0.6)];
}

.status-offline {
  @apply bg-muted-foreground;
}

/* 执行状态 */
.status-running {
  @apply bg-primary shadow-[0_0_8px_rgba(255,136,0,0.6)];
}

.status-success {
  @apply bg-success shadow-[0_0_8px_rgba(16,185,129,0.6)];
}

.status-failed {
  @apply bg-error shadow-[0_0_8px_rgba(239,68,68,0.6)];
}

.status-pending {
  @apply bg-muted-foreground;
}
```

---

## 📱 页面设计

### 1. 设备管理页 (Dashboard)

**布局：** 网格卡片布局

```tsx
<div className="p-6">
  <div className="flex items-center justify-between mb-6">
    <h1 className="text-2xl font-bold">📱 设备管理</h1>
    <div className="flex gap-2">
      <Button variant="outline" onClick={handleRefresh}>
        <RefreshCw className="w-4 h-4 mr-2" />
        刷新
      </Button>
      <Button variant="default" onClick={handleAddDevice}>
        <Plus className="w-4 h-4 mr-2" />
```

**设备卡片组件：**

```javascript
// DeviceCard.js
class DeviceCard {
  constructor(device) {
    this.device = device;
  }

  render() {
    return `
      <div class="device-card">
        <div class="device-card-header">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full status-online"></div>
              ${this.device.name}
            </div>
            <button class="btn btn-ghost" onclick="handleDisconnect(${this.device.id})">
              断开
            </button>
          </div>
        </div>
        <div class="device-card-content">
          <div class="space-y-2 text-sm text-muted-foreground">
            <div>iOS ${this.device.osVersion}</div>
            <div>USB 连接</div>
            <div>电量: ${this.device.battery}%</div>
          </div>
        </div>
        <div class="device-card-footer">
          <button class="btn btn-outline" onclick="handleScreenshot(${this.device.id})">
            查看截图
          </button>
        </div>
      </div>
    `;
  }
}
<Card className="hover:shadow-lg transition-shadow">
  <CardHeader>
    <div className="flex items-center justify-between">
      <CardTitle className="flex items-center gap-2">
        <div className="w-3 h-3 rounded-full status-online" />
        iPhone 12
      </CardTitle>
      <Badge variant="outline">iOS</Badge>
    </div>
  </CardHeader>
  <CardContent>
    <div className="space-y-2 text-sm text-muted-foreground">
      <div>iOS 17.2</div>
      <div>USB 连接</div>
      <div>电量: 85%</div>
    </div>
  </CardContent>
  <CardFooter className="flex gap-2">
    <Button variant="outline" size="sm" className="flex-1">
      查看截图
    </Button>
    <Button variant="ghost" size="sm">
      断开
    </Button>
  </CardFooter>
</Card>
```

---

### 2. 测试用例管理页

**布局：** 左右分栏布局

```tsx
<div className="flex h-full">
  {/* 左侧：用例列表 */}
  <div className="w-80 border-r p-4 overflow-auto">
    <Input 
      placeholder="🔍 搜索用例..." 
      className="mb-4"
    />
    <ScrollArea className="h-full">
      <Collapsible>
        <CollapsibleTrigger>
          📂 登录模块 (3)
        </CollapsibleTrigger>
        <CollapsibleContent>
          <div className="ml-4 space-y-1">
            <div className="p-2 hover:bg-accent rounded cursor-pointer">
              ✅ 登录测试
            </div>
            <div className="p-2 hover:bg-accent rounded cursor-pointer">
              ✅ 登出测试
            </div>
          </div>
        </CollapsibleContent>
      </Collapsible>
    </ScrollArea>
  </div>
  
  {/* 右侧：用例编辑器 */}
  <div className="flex-1 p-6 overflow-auto">
    <TestCaseEditor />
  </div>
</div>
```

**步骤编辑器：**

```tsx
<div className="space-y-4">
  {steps.map((step, index) => (
    <Card key={index}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <span className="font-medium">{index + 1}. {step.description}</span>
          <div className="flex gap-2">
            <Button variant="ghost" size="sm">编辑</Button>
            <Button variant="ghost" size="sm">删除</Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>动作: {step.action}</div>
          <div>参数: {JSON.stringify(step.params)}</div>
        </div>
      </CardContent>
    </Card>
  ))}
  
  <Button variant="outline" className="w-full">
    <Plus className="w-4 h-4 mr-2" />
    添加步骤
  </Button>
</div>
```

---

### 3. 执行监控页

**布局：** 上中下三栏布局

```tsx
<div className="p-6 space-y-6">
  {/* 执行信息 */}
  <Card>
    <CardContent className="pt-6">
      <div className="grid grid-cols-4 gap-4">
        <div>
          <div className="text-sm text-muted-foreground">用例</div>
          <div className="font-medium">登录测试</div>
        </div>
        <div>
          <div className="text-sm text-muted-foreground">设备</div>
          <div className="font-medium">iPhone 12</div>
        </div>
        <div>
          <div className="text-sm text-muted-foreground">状态</div>
          <Badge variant="warning">🟡 执行中</Badge>
        </div>
        <div>
          <div className="text-sm text-muted-foreground">耗时</div>
          <div className="font-medium">00:00:45</div>
        </div>
      </div>
      
      <div className="mt-4">
        <Progress value={50} className="h-2" />
        <div className="text-sm text-muted-foreground mt-1">
          50% (5/10 步骤)
        </div>
      </div>
    </CardContent>
  </Card>
  
  {/* 实时截图 + 日志 */}
  <div className="grid grid-cols-2 gap-6">
    <Card>
      <CardHeader>
        <CardTitle>实时截图</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="aspect-[9/16] bg-muted rounded-lg flex items-center justify-center">
          <img src={screenshot} alt="设备截图" className="max-h-full" />
        </div>
      </CardContent>
    </Card>
    
    <Card>
      <CardHeader>
        <CardTitle>执行日志</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-96">
          <div className="space-y-1 font-mono text-sm">
            <div className="text-info">[INFO] 开始执行测试</div>
            <div className="text-success">[SUCCESS] 步骤1: 点击登录</div>
            <div className="text-info">[INFO] 步骤2: 输入用户名</div>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  </div>
  
  {/* 步骤详情 */}
  <Card>
    <CardHeader>
      <CardTitle>步骤详情</CardTitle>
    </CardHeader>
    <CardContent>
      <div className="space-y-2">
        {steps.map((step, index) => (
          <div key={index} className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
            <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
              step.status === 'success' ? 'bg-success text-white' :
              step.status === 'running' ? 'bg-primary text-white' :
              'bg-muted-foreground text-white'
            }`}>
              {index + 1}
            </div>
            <div className="flex-1">{step.description}</div>
            <div className="text-sm text-muted-foreground">{step.duration}s</div>
          </div>
        ))}
      </div>
    </CardContent>
  </Card>
</div>
```

---

### 4. 结果分析页

**布局：** 统计卡片 + 图表 + 表格

```tsx
<div className="p-6 space-y-6">
  {/* 统计概览 */}
  <div className="grid grid-cols-4 gap-4">
    <Card>
      <CardContent className="pt-6">
        <div className="text-2xl font-bold">156</div>
        <div className="text-sm text-muted-foreground">总执行数</div>
      </CardContent>
    </Card>
    <Card>
      <CardContent className="pt-6">
        <div className="text-2xl font-bold text-success">85.5%</div>
        <div className="text-sm text-muted-foreground">通过率</div>
      </CardContent>
    </Card>
    <Card>
      <CardContent className="pt-6">
        <div className="text-2xl font-bold">120s</div>
        <div className="text-sm text-muted-foreground">平均耗时</div>
      </CardContent>
    </Card>
    <Card>
      <CardContent className="pt-6">
        <div className="text-2xl font-bold text-error">23</div>
        <div className="text-sm text-muted-foreground">失败次数</div>
      </CardContent>
    </Card>
  </div>
  
  {/* 趋势图 */}
  <Card>
    <CardHeader>
      <CardTitle>通过率趋势</CardTitle>
    </CardHeader>
    <CardContent>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={trendData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="passRate" stroke="#FF8800" />
        </LineChart>
      </ResponsiveContainer>
    </CardContent>
  </Card>
  
  {/* 执行记录表格 */}
  <Card>
    <CardHeader>
      <CardTitle>最近执行记录</CardTitle>
    </CardHeader>
    <CardContent>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>时间</TableHead>
            <TableHead>用例名称</TableHead>
            <TableHead>设备</TableHead>
            <TableHead>状态</TableHead>
            <TableHead>耗时</TableHead>
            <TableHead>操作</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {results.map(result => (
            <TableRow key={result.id}>
              <TableCell>{result.time}</TableCell>
              <TableCell>{result.name}</TableCell>
              <TableCell>{result.device}</TableCell>
              <TableCell>
                <Badge variant={result.status === 'PASS' ? 'success' : 'destructive'}>
                  {result.status}
                </Badge>
              </TableCell>
              <TableCell>{result.duration}s</TableCell>
              <TableCell>
                <Button variant="ghost" size="sm">查看详情</Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </CardContent>
  </Card>
</div>
```

---

## 🧩 组件规范

### 按钮组件

```vue
<!-- 主要按钮 - 使用橙色主题 -->
<Button variant="default">执行测试</Button>

<!-- 次要按钮 -->
<Button variant="secondary">取消</Button>

<!-- 轮廓按钮 -->
<Button variant="outline">查看详情</Button>

<!-- 幽灵按钮 -->
<Button variant="ghost">删除</Button>

<!-- 危险按钮 -->
<Button variant="destructive">强制停止</Button>

<!-- 尺寸 -->
<Button size="sm">小按钮</Button>
<Button size="default">默认</Button>
<Button size="lg">大按钮</Button>

<!-- 带图标 -->
<Button>
  <Play class="w-4 h-4 mr-2" />
  执行
</Button>
```

### 徽章组件

```vue
<!-- 状态徽章 -->
<Badge variant="success">在线</Badge>
<Badge variant="warning">执行中</Badge>
<Badge variant="destructive">失败</Badge>
<Badge variant="default">默认</Badge>
<Badge variant="outline">轮廓</Badge>

<!-- 自定义颜色 -->
<Badge class="bg-primary text-primary-foreground">
  自定义
</Badge>
```

### 卡片组件

```vue
<Card>
  <CardHeader>
    <CardTitle>标题</CardTitle>
    <CardDescription>描述文字</CardDescription>
  </CardHeader>
  <CardContent>
    内容区域
  </CardContent>
  <CardFooter>
    <Button>操作</Button>
  </CardFooter>
</Card>
```

### 表单组件

```vue
<!-- 输入框 -->
<Input 
  type="text" 
  placeholder="请输入..." 
  class="w-full"
/>

<!-- 标签 -->
<Label for="name">名称</Label>
<Input id="name" />

<!-- 选择器 -->
<Select v-model="platform">
  <SelectTrigger>
    <SelectValue placeholder="选择平台" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="ios">iOS</SelectItem>
    <SelectItem value="android">Android</SelectItem>
  </SelectContent>
</Select>

<!-- 开关 -->
<Switch v-model="enabled" />
```

---

## 👥 用户使用流程

### 典型工作流

```
1. 连接设备
   ↓
   打开应用 → 设备管理 → 扫描设备 → 查看状态
   
2. 创建用例
   ↓
   用例管理 → 新建用例 → 添加步骤 → 保存
   
3. 执行测试
   ↓
   选择用例 → 选择设备 → 执行 → 实时监控
   
4. 查看结果
   ↓
   结果分析 → 查看详情 → 导出报告
```

---

## 🚀 开发指南

### 项目结构

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn-vue 组件
│   │   │   ├── button.vue
│   │   │   ├── card.vue
│   │   │   ├── badge.vue
│   │   │   └── ...
│   │   ├── DeviceCard.vue
│   │   ├── TestCaseEditor.vue
│   │   └── ExecutionMonitor.vue
│   ├── pages/
│   │   ├── Dashboard.vue
│   │   ├── TestCases.vue
│   │   ├── Execution.vue
│   │   └── Results.vue
│   ├── api/
│   │   └── client.ts
│   ├── composables/
│   │   ├── useDevices.ts
│   │   └── useTestCases.ts
│   ├── stores/
│   │   ├── device.ts
│   │   └── testCase.ts
│   ├── router/
│   │   └── index.ts
│   ├── styles/
│   │   └── globals.css
│   ├── App.vue
│   └── main.ts
├── package.json
├── tailwind.config.js
└── vite.config.ts
```

### 全局样式 (globals.css)

```css
@import 'tailwindcss';

@theme inline {
  --color-primary: oklch(0.72 0.18 50);
  --color-primary-foreground: oklch(1 0 0);
  /* ... 其他颜色变量 */
}

:root {
  --radius: 0.625rem;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground) / 0.3);
  border-radius: 4px;
}

/* 自定义动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
```

### 安装 shadcn-vue

```bash
# 初始化
npx shadcn-vue@latest init

# 添加组件
npx shadcn-vue@latest add button
npx shadcn-vue@latest add card
npx shadcn-vue@latest add badge
npx shadcn-vue@latest add input
npx shadcn-vue@latest add table
npx shadcn-vue@latest add dialog
npx shadcn-vue@latest add select
npx shadcn-vue@latest add tabs
npx shadcn-vue@latest add progress
npx shadcn-vue@latest add scroll-area
```

### 快速启动

```bash
# 安装依赖
cd frontend
npm install

# 开发模式
npm run dev

# 构建
npm run build

# 预览
npm run preview
```

---

## 📦 依赖清单

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "@tanstack/vue-query": "^5.14.0",
    "socket.io-client": "^4.6.0",
    "vue-echarts": "^6.6.0",
    "echarts": "^5.4.0",
    "lucide-vue-next": "^0.300.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.2.0",
    "class-variance-authority": "^0.7.0",
    "radix-vue": "^1.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.8",
    "tailwindcss": "^4.0.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "eslint": "^8.56.0",
    "prettier": "^3.1.0"
  }
}
```

> **注意：已移除 TypeScript 相关依赖**（`typescript`, `vue-tsc`）

---

## ✨ 设计原则

1. **一致性** - 所有页面使用统一的设计语言
2. **可访问性** - 支持键盘导航和屏幕阅读器
3. **响应式** - 适配各种屏幕尺寸
4. **性能优先** - 懒加载、虚拟滚动、代码分割
5. **用户友好** - 清晰的反馈、合理的默认值

---

**文档版本：v1.1**  
**更新日期：2026-01-05**  
**主色调：#FF8800 (活力橙)**  
**技术栈：Vue 3 + JavaScript（不使用 TypeScript）**
