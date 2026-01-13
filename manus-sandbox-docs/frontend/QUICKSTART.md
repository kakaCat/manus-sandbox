# 快速启动指南

## 🚀 5 分钟上手

### 步骤 1: 安装依赖

```bash
cd frontend
npm install
```

### 步骤 2: 启动开发服务器

```bash
npm run dev
```

浏览器会自动打开 http://localhost:5173

### 步骤 3: 使用组件

现在你可以：

1. **上传 Excel 文件**
   - 拖拽文件到上传区域
   - 或点击"选择文件"按钮

2. **查看数据**
   - 浏览表格数据
   - 切换不同的 Sheet
   - 点击单元格查看详情

3. **操作数据**
   - 点击"下载"重新保存文件
   - 点击"复制"复制数据到剪贴板
   - 点击"关闭"返回上传页面

## 📝 最简单的集成示例

创建一个新的 Vue 文件：

```vue
<template>
  <div>
    <h1>我的 Excel 查看器</h1>
    <ExcelViewer />
  </div>
</template>

<script setup>
import ExcelViewer from '@/components/ExcelViewer.vue'
</script>
```

就这么简单！

## 🎯 常见使用场景

### 场景 1: 文件预览

```vue
<template>
  <ExcelViewer @file-loaded="handleLoad" />
</template>

<script setup>
const handleLoad = (data) => {
  console.log('文件已加载:', data.fileName)
}
</script>
```

### 场景 2: 数据验证

```vue
<template>
  <ExcelViewer @file-loaded="validateData" />
</template>

<script setup>
const validateData = (data) => {
  const sheet1 = data.data[0].data
  const headers = sheet1[0]

  if (!headers.includes('姓名')) {
    alert('缺少"姓名"列！')
  }
}
</script>
```

### 场景 3: 数据提取

```vue
<template>
  <ExcelViewer @file-loaded="extractData" />
</template>

<script setup>
const extractData = (data) => {
  const rows = data.data[0].data

  // 跳过表头，提取数据
  const users = rows.slice(1).map(row => ({
    name: row[0],
    age: row[1],
    city: row[2]
  }))

  console.log('提取的用户数据:', users)
}
</script>
```

## 🎨 自定义样式

```vue
<template>
  <div class="my-viewer">
    <ExcelViewer height="800px" />
  </div>
</template>

<style>
.my-viewer {
  padding: 20px;
  background: #f0f0f0;
}
</style>
```

## 📦 项目结构

```
frontend/
├── src/
│   ├── components/
│   │   └── ExcelViewer.vue    # 核心组件
│   ├── views/
│   │   └── ExcelViewerDemo.vue # 演示页面
│   ├── App.vue                 # 应用入口
│   ├── main.js                 # 主文件
│   └── style.css               # 全局样式
├── index.html                  # HTML 模板
├── package.json                # 依赖配置
├── vite.config.js              # Vite 配置
└── README.md                   # 完整文档
```

## 🔧 常用命令

```bash
# 开发
npm run dev

# 构建
npm run build

# 预览构建结果
npm run preview

# 代码检查
npm run lint
```

## 💡 小贴士

1. **支持的文件格式**
   - .xlsx (推荐)
   - .xls
   - .csv

2. **最佳性能**
   - 文件大小 < 10MB
   - 行数 < 10,000
   - 列数 < 100

3. **浏览器兼容性**
   - Chrome 90+
   - Firefox 88+
   - Safari 14+
   - Edge 90+

## ❓ 常见问题

### 无法上传文件？

检查文件格式是否为 .xlsx, .xls 或 .csv

### 中文乱码？

确保 Excel 文件使用 UTF-8 编码保存

### 表格显示不全？

使用鼠标滚动或调整窗口大小

## 📚 更多资源

- [完整文档](./README.md)
- [Vue 3 官方文档](https://vuejs.org/)
- [SheetJS 文档](https://docs.sheetjs.com/)

## 🆘 需要帮助？

查看 [完整文档](./README.md) 或提交 Issue

---

开始使用吧！ 🎉
