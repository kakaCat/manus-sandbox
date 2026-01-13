<template>
  <div class="demo-container">
    <h1>📊 Excel 查看器演示</h1>

    <div class="demo-section">
      <h2>示例 1: 基础用法</h2>
      <p>拖拽或选择 Excel 文件进行查看</p>
      <div class="viewer-wrapper">
        <ExcelViewer
          @file-loaded="handleFileLoaded"
          @error="handleError"
        />
      </div>
    </div>

    <div class="demo-section">
      <h2>示例 2: 指定高度</h2>
      <p>可以自定义表格显示高度</p>
      <div class="viewer-wrapper" style="height: 400px;">
        <ExcelViewer height="400px" />
      </div>
    </div>

    <div v-if="loadedInfo" class="info-panel">
      <h3>已加载文件信息:</h3>
      <ul>
        <li><strong>文件名:</strong> {{ loadedInfo.fileName }}</li>
        <li><strong>Sheet 数量:</strong> {{ loadedInfo.sheets.length }}</li>
        <li><strong>Sheet 名称:</strong> {{ loadedInfo.sheets.join(', ') }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ExcelViewer from '../components/ExcelViewer.vue'

const loadedInfo = ref(null)

const handleFileLoaded = (info) => {
  loadedInfo.value = info
  console.log('文件已加载:', info)
}

const handleError = (error) => {
  console.error('加载错误:', error)
  alert('加载 Excel 文件时出错: ' + error.message)
}
</script>

<style scoped>
.demo-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 40px;
}

.demo-section {
  margin-bottom: 60px;
}

.demo-section h2 {
  color: #4CAF50;
  margin-bottom: 10px;
}

.demo-section p {
  color: #666;
  margin-bottom: 20px;
}

.viewer-wrapper {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 600px;
}

.info-panel {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #4CAF50;
}

.info-panel h3 {
  margin-top: 0;
  color: #333;
}

.info-panel ul {
  list-style: none;
  padding: 0;
}

.info-panel li {
  padding: 8px 0;
  border-bottom: 1px solid #e0e0e0;
}

.info-panel li:last-child {
  border-bottom: none;
}
</style>
