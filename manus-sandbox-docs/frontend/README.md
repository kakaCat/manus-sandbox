# Excel Viewer 前端组件

一个功能完整的 Vue 3 Excel 文件查看器组件，支持拖拽上传、多 Sheet 切换、数据展示和导出功能。

## ✨ 特性

- 📤 **拖拽上传** - 支持拖拽文件到指定区域
- 📊 **多格式支持** - 支持 .xlsx, .xls, .csv 文件格式
- 📑 **多 Sheet 支持** - 自动识别并支持切换多个工作表
- 🎨 **美观界面** - 现代化的 UI 设计，响应式布局
- 💾 **下载功能** - 支持重新下载 Excel 文件
- 📋 **复制功能** - 一键复制表格数据到剪贴板
- 🔢 **数据统计** - 实时显示行数、列数等信息
- 🎯 **单元格选择** - 点击单元格查看详细信息
- 🎭 **数据格式化** - 自动格式化数字、日期等数据类型

## 🚀 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173 查看演示。

### 构建生产版本

```bash
npm run build
```

## 📦 核心依赖

- **Vue 3** - 现代化的渐进式 JavaScript 框架
- **SheetJS (xlsx)** - 强大的 Excel 文件处理库
- **Vite** - 下一代前端构建工具

## 📖 组件使用说明

### ExcelViewer 组件

#### 基础用法

```vue
<template>
  <div>
    <ExcelViewer />
  </div>
</template>

<script setup>
import ExcelViewer from '@/components/ExcelViewer.vue'
</script>
```

#### Props

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| file | File | null | 可选：直接传入文件对象 |
| data | Array | null | 可选：直接传入 Excel 数据 |
| height | String | '600px' | 表格显示高度 |

#### Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| file-loaded | { fileName, sheets, data } | 文件加载完成时触发 |
| error | Error | 加载出错时触发 |

#### 完整示例

```vue
<template>
  <div class="container">
    <h1>Excel 文件查看器</h1>

    <!-- 基础用法 -->
    <ExcelViewer
      @file-loaded="handleFileLoaded"
      @error="handleError"
    />

    <!-- 自定义高度 -->
    <ExcelViewer
      height="800px"
      @file-loaded="handleFileLoaded"
    />

    <!-- 显示加载信息 -->
    <div v-if="fileInfo">
      <p>文件名: {{ fileInfo.fileName }}</p>
      <p>Sheet 数量: {{ fileInfo.sheets.length }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ExcelViewer from '@/components/ExcelViewer.vue'

const fileInfo = ref(null)

const handleFileLoaded = (info) => {
  fileInfo.value = info
  console.log('文件已加载:', info)

  // info 包含以下数据:
  // - fileName: 文件名
  // - sheets: Sheet 名称数组
  // - data: 完整的 Sheet 数据数组
}

const handleError = (error) => {
  console.error('加载错误:', error)
  alert('无法加载文件: ' + error.message)
}
</script>
```

## 🎨 组件功能详解

### 1. 文件上传

支持两种上传方式：

- **拖拽上传**：将 Excel 文件拖拽到上传区域
- **点击选择**：点击"选择文件"按钮选择本地文件

支持的文件格式：
- `.xlsx` - Excel 2007+ 格式
- `.xls` - Excel 97-2003 格式
- `.csv` - 逗号分隔值文件

### 2. 数据展示

#### 表格功能

- **固定表头**：滚动时表头保持固定
- **固定行号**：滚动时行号保持固定
- **斑马纹**：偶数行使用不同背景色，提高可读性
- **数据对齐**：数字右对齐，文本左对齐
- **空单元格**：空值使用特殊样式标识

#### 列名显示

- 使用 Excel 标准列名（A, B, C, ..., AA, AB, ...）
- 自动计算列名，支持无限列

#### 数据格式化

- **数字**：自动添加千分位分隔符
- **日期**：自动识别 Excel 日期序列号并格式化
- **空值**：显示为空并标记

### 3. 多 Sheet 支持

- 自动识别文件中的所有 Sheet
- 顶部显示 Sheet 标签页
- 点击标签页切换 Sheet
- 当前 Sheet 高亮显示

### 4. 工具栏功能

#### 下载功能

点击"💾 下载"按钮可重新下载原 Excel 文件，保持原始格式。

#### 复制功能

点击"📋 复制"按钮将当前 Sheet 的数据复制到剪贴板，格式为 Tab 分隔的文本，可直接粘贴到 Excel 或其他表格软件。

#### 关闭功能

点击"✕ 关闭"按钮关闭当前文件，返回上传界面。

### 5. 单元格选择

点击任意单元格，底部会显示：
- 单元格地址（如 A1, B3）
- 单元格值

### 6. 数据统计

顶部显示当前 Sheet 的：
- 总行数
- 总列数

## 🎯 高级用法

### 编程式加载文件

```vue
<template>
  <div>
    <input type="file" @change="handleFileChange" />
    <ExcelViewer ref="viewerRef" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ExcelViewer from '@/components/ExcelViewer.vue'

const viewerRef = ref(null)

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    // 直接调用组件的 loadFile 方法
    viewerRef.value.loadFile(file)
  }
}
</script>
```

### 集成到现有表单

```vue
<template>
  <div class="form">
    <h2>上传 Excel 文件</h2>

    <div class="form-field">
      <label>选择文件:</label>
      <input type="file" @change="handleFileSelect" accept=".xlsx,.xls,.csv" />
    </div>

    <div v-if="selectedFile" class="preview">
      <h3>文件预览:</h3>
      <ExcelViewer
        :file="selectedFile"
        height="500px"
        @file-loaded="onFileLoaded"
      />
    </div>

    <button @click="submitForm" :disabled="!fileData">提交</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ExcelViewer from '@/components/ExcelViewer.vue'

const selectedFile = ref(null)
const fileData = ref(null)

const handleFileSelect = (event) => {
  selectedFile.value = event.target.files[0]
}

const onFileLoaded = (data) => {
  fileData.value = data
}

const submitForm = async () => {
  if (!fileData.value) return

  // 提交表单数据
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('sheets', JSON.stringify(fileData.value.sheets))

  // 发送到后端
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData
  })

  console.log('上传成功:', await response.json())
}
</script>
```

## 🔧 自定义样式

所有样式都使用 scoped CSS，可以通过 CSS 变量或覆盖特定类来自定义：

```vue
<template>
  <div class="custom-viewer">
    <ExcelViewer />
  </div>
</template>

<style>
.custom-viewer {
  /* 自定义上传区域背景色 */
  --upload-bg: #e3f2fd;

  /* 自定义主题色 */
  --primary-color: #2196F3;
}

/* 覆盖表格样式 */
.custom-viewer .excel-table th {
  background: #1976D2 !important;
  color: white !important;
}

.custom-viewer .excel-table td {
  font-size: 14px !important;
}
</style>
```

## 📊 数据结构

### file-loaded 事件返回的数据结构

```javascript
{
  fileName: "example.xlsx",  // 文件名
  sheets: ["Sheet1", "Sheet2"],  // Sheet 名称数组
  data: [
    {
      name: "Sheet1",  // Sheet 名称
      data: [
        ["姓名", "年龄", "城市"],  // 第一行（表头）
        ["张三", 25, "北京"],      // 数据行
        ["李四", 30, "上海"]
      ]
    },
    {
      name: "Sheet2",
      data: [...]
    }
  ]
}
```

### 单元格数据类型

组件会自动识别以下数据类型：

- **字符串**：普通文本
- **数字**：整数或浮点数
- **日期**：Excel 日期序列号（自动转换）
- **空值**：null, undefined, ""

## 🐛 错误处理

### 常见错误

1. **不支持的文件格式**
   - 错误信息：`不支持的文件格式，请上传 .xlsx, .xls 或 .csv 文件`
   - 解决方法：确保文件扩展名正确

2. **Excel 文件为空**
   - 错误信息：`Excel 文件为空`
   - 解决方法：确保文件包含至少一个 Sheet 和数据

3. **文件损坏**
   - 错误信息：`无法读取文件`
   - 解决方法：尝试用 Excel 重新保存文件

### 错误监听

```vue
<template>
  <ExcelViewer @error="handleError" />
</template>

<script setup>
const handleError = (error) => {
  console.error('错误:', error)

  // 显示友好的错误提示
  if (error.message.includes('格式')) {
    alert('请上传有效的 Excel 文件')
  } else {
    alert('文件加载失败，请重试')
  }
}
</script>
```

## 🎨 主题定制

### 颜色方案

组件使用以下主要颜色：

- **主题色**：#4CAF50（绿色）
- **背景色**：#f5f5f5（浅灰）
- **边框色**：#e0e0e0（灰色）
- **悬停色**：#f0f0f0（浅灰）

### 修改主题色

```css
/* 在全局样式中定义 */
:root {
  --excel-primary: #2196F3;
  --excel-hover: #1976D2;
}

/* 组件中使用 */
.action-btn {
  background: var(--excel-primary, #4CAF50);
}

.action-btn:hover {
  background: var(--excel-hover, #45a049);
}
```

## 📱 响应式设计

组件完全响应式，在不同屏幕尺寸下都能正常使用：

- **桌面**：完整功能，横向滚动
- **平板**：自适应宽度，触摸滚动
- **手机**：垂直布局，优化触摸操作

## ⚡ 性能优化

### 大文件处理

对于包含大量数据的 Excel 文件：

1. **虚拟滚动**（待实现）：只渲染可见区域的行
2. **分页加载**（待实现）：按需加载数据
3. **Web Worker**（待实现）：在后台线程处理文件

当前版本建议：
- 文件大小 < 10MB
- 行数 < 10,000
- 列数 < 100

## 🔐 安全性

- ✅ 文件仅在客户端处理，不上传到服务器
- ✅ 使用标准的 FileReader API
- ✅ 严格的文件类型验证
- ✅ 防止 XSS 攻击（文本内容自动转义）

## 🧪 测试

```bash
# 运行单元测试（待实现）
npm run test

# 运行 E2E 测试（待实现）
npm run test:e2e
```

## 📦 打包和部署

### 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

### Docker 部署

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

构建和运行：

```bash
docker build -t excel-viewer .
docker run -p 8080:80 excel-viewer
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [Vue 3 文档](https://vuejs.org/)
- [SheetJS 文档](https://docs.sheetjs.com/)
- [Vite 文档](https://vitejs.dev/)

## 📞 联系方式

如有问题或建议，请联系开发团队。

---

**更新日期**: 2026-01-09
**版本**: 1.0.0
