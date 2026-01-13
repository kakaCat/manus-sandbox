# Manus Sandbox

Manus 沙盒环境，包含 Excel 查看器等前端组件。

## 📁 项目结构

```
manus-sandbox/
├── frontend/                   # 前端 Vue 3 应用
│   ├── src/
│   │   ├── components/
│   │   │   └── ExcelViewer.vue    # Excel 查看器组件
│   │   ├── views/
│   │   │   └── ExcelViewerDemo.vue # 演示页面
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── package.json
│   ├── vite.config.js
│   ├── README.md              # 详细文档
│   ├── QUICKSTART.md          # 快速开始
│   └── TEST_FILES.md          # 测试文件说明
│
└── docs/                       # 项目文档
```

## 🚀 快速开始

### Excel 查看器

一个功能完整的 Excel 文件查看器组件，支持：

- 📤 拖拽上传 Excel 文件
- 📊 支持 .xlsx, .xls, .csv 格式
- 📑 多 Sheet 支持
- 🎨 美观的界面设计
- 💾 下载和复制功能
- 🔢 数据统计和格式化

#### 启动开发服务器

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 查看演示。

#### 使用组件

```vue
<template>
  <ExcelViewer
    @file-loaded="handleFileLoaded"
    @error="handleError"
  />
</template>

<script setup>
import ExcelViewer from '@/components/ExcelViewer.vue'

const handleFileLoaded = (data) => {
  console.log('文件:', data.fileName)
  console.log('Sheets:', data.sheets)
  console.log('数据:', data.data)
}

const handleError = (error) => {
  console.error('错误:', error)
}
</script>
```

## 📖 文档

- [Excel 查看器完整文档](./frontend/README.md)
- [快速开始指南](./frontend/QUICKSTART.md)
- [测试文件说明](./frontend/TEST_FILES.md)

## 🛠️ 技术栈

### 前端
- Vue 3 + Composition API
- SheetJS (xlsx) - Excel 文件处理
- Vite - 构建工具

## ✨ 特性

### Excel 查看器组件

- **文件上传**
  - 拖拽上传或点击选择
  - 文件类型验证
  - 文件大小显示

- **数据展示**
  - Excel 风格表格
  - 固定表头和行号
  - 列名显示（A, B, C...）
  - 斑马纹背景
  - 智能数据格式化

- **多 Sheet 支持**
  - 自动识别所有 Sheet
  - 标签页切换
  - 当前 Sheet 高亮

- **工具功能**
  - 下载 Excel 文件
  - 复制表格数据
  - 单元格选择
  - 数据统计

- **响应式设计**
  - 桌面端、平板、移动端适配
  - 流畅的滚动
  - 现代化 UI

## 📦 组件 API

### ExcelViewer

#### Props
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| file | File | null | 文件对象 |
| data | Array | null | Excel 数据 |
| height | String | '600px' | 表格高度 |

#### Events
| 事件名 | 参数 | 说明 |
|--------|------|------|
| file-loaded | { fileName, sheets, data } | 文件加载完成 |
| error | Error | 加载出错 |

## 🎯 使用场景

1. **数据预览** - 快速查看 Excel 文件内容
2. **数据验证** - 上传前验证数据格式
3. **数据导入** - 预览后提交到服务器
4. **数据分析** - 在线查看业务数据
5. **文件转换** - Excel 转 JSON/CSV

## 🔧 开发

### 安装依赖
```bash
cd frontend
npm install
```

### 开发命令
```bash
npm run dev      # 启动开发服务器
npm run build    # 构建生产版本
npm run preview  # 预览构建结果
npm run lint     # 代码检查
```

## 🌐 浏览器支持

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📊 性能指标

- 支持文件大小：< 10MB
- 推荐最大行数：10,000 行
- 推荐最大列数：100 列
- 首次加载：< 2 秒

## 🔐 安全性

- ✅ 文件仅在客户端处理
- ✅ 不上传到服务器
- ✅ 严格的文件类型验证
- ✅ XSS 防护

## 🗺️ 路线图

- [ ] 虚拟滚动（大文件优化）
- [ ] 合并单元格支持
- [ ] 公式显示
- [ ] 数据搜索和过滤
- [ ] 列排序功能
- [ ] 导出多种格式
- [ ] 打印支持

## 📄 许可证

MIT License

---

**更新日期**: 2026-01-09
**版本**: 1.0.0
