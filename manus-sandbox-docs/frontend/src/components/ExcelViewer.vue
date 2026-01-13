<template>
  <div class="excel-viewer">
    <!-- 文件上传区域 -->
    <div v-if="!fileLoaded" class="upload-area">
      <div
        class="drop-zone"
        :class="{ 'drag-over': isDragOver }"
        @drop.prevent="handleDrop"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
      >
        <div class="upload-icon">📊</div>
        <h3>拖拽 Excel 文件到此处</h3>
        <p>或者</p>
        <label class="upload-button">
          <input
            type="file"
            accept=".xlsx,.xls,.csv"
            @change="handleFileSelect"
            hidden
          />
          选择文件
        </label>
        <p class="hint">支持 .xlsx, .xls, .csv 格式</p>
      </div>
    </div>

    <!-- Excel 内容展示区域 -->
    <div v-else class="excel-content">
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="file-info">
          <span class="file-name">{{ fileName }}</span>
          <span class="file-size">{{ formatFileSize(fileSize) }}</span>
        </div>
        <div class="actions">
          <button @click="downloadExcel" class="action-btn" title="下载">
            💾 下载
          </button>
          <button @click="copyToClipboard" class="action-btn" title="复制">
            📋 复制
          </button>
          <button @click="resetViewer" class="action-btn danger" title="关闭">
            ✕ 关闭
          </button>
        </div>
      </div>

      <!-- Sheet 标签页 -->
      <div v-if="sheets.length > 1" class="sheet-tabs">
        <button
          v-for="(sheet, index) in sheets"
          :key="index"
          :class="['sheet-tab', { active: currentSheetIndex === index }]"
          @click="switchSheet(index)"
        >
          {{ sheet.name }}
        </button>
      </div>

      <!-- 数据统计 -->
      <div class="stats">
        <span>行数: {{ currentData.length }}</span>
        <span>列数: {{ currentData[0]?.length || 0 }}</span>
      </div>

      <!-- 表格展示 -->
      <div class="table-container">
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>
        <div v-else-if="error" class="error">
          <p>❌ {{ error }}</p>
        </div>
        <table v-else class="excel-table">
          <thead>
            <tr>
              <th class="row-number">#</th>
              <th
                v-for="(cell, colIndex) in currentData[0]"
                :key="colIndex"
                class="column-header"
              >
                {{ getColumnName(colIndex) }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, rowIndex) in currentData"
              :key="rowIndex"
              :class="{ 'even-row': rowIndex % 2 === 0 }"
            >
              <td class="row-number">{{ rowIndex + 1 }}</td>
              <td
                v-for="(cell, colIndex) in row"
                :key="colIndex"
                :class="getCellClass(cell)"
                @click="selectCell(rowIndex, colIndex)"
              >
                {{ formatCell(cell) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 选中单元格信息 -->
      <div v-if="selectedCell" class="cell-info">
        <span>
          <strong>{{ getColumnName(selectedCell.col) }}{{ selectedCell.row + 1 }}</strong>:
          {{ formatCell(currentData[selectedCell.row][selectedCell.col]) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import * as XLSX from 'xlsx'

// Props
const props = defineProps({
  // 可选：直接传入文件对象
  file: {
    type: File,
    default: null
  },
  // 可选：直接传入 Excel 数据
  data: {
    type: Array,
    default: null
  },
  // 可选：表格高度
  height: {
    type: String,
    default: '600px'
  }
})

// Emits
const emit = defineEmits(['file-loaded', 'error'])

// 状态
const fileLoaded = ref(false)
const fileName = ref('')
const fileSize = ref(0)
const sheets = ref([])
const currentSheetIndex = ref(0)
const loading = ref(false)
const error = ref('')
const isDragOver = ref(false)
const selectedCell = ref(null)
const workbook = ref(null)

// 计算属性：当前 Sheet 的数据
const currentData = computed(() => {
  if (sheets.value.length === 0) return []
  return sheets.value[currentSheetIndex.value].data
})

// 处理文件选择
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    loadFile(file)
  }
}

// 处理拖拽上传
const handleDrop = (event) => {
  isDragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    loadFile(file)
  }
}

// 加载文件
const loadFile = async (file) => {
  try {
    loading.value = true
    error.value = ''

    // 验证文件类型
    const validTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
      'text/csv'
    ]

    if (!validTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls|csv)$/i)) {
      throw new Error('不支持的文件格式，请上传 .xlsx, .xls 或 .csv 文件')
    }

    fileName.value = file.name
    fileSize.value = file.size

    // 读取文件
    const data = await file.arrayBuffer()
    workbook.value = XLSX.read(data, { type: 'array' })

    // 解析所有 Sheet
    sheets.value = workbook.value.SheetNames.map(name => {
      const worksheet = workbook.value.Sheets[name]
      const jsonData = XLSX.utils.sheet_to_json(worksheet, {
        header: 1,
        defval: '',
        blankrows: true
      })
      return {
        name,
        data: jsonData
      }
    })

    if (sheets.value.length === 0) {
      throw new Error('Excel 文件为空')
    }

    fileLoaded.value = true
    emit('file-loaded', {
      fileName: fileName.value,
      sheets: sheets.value.map(s => s.name),
      data: sheets.value
    })
  } catch (err) {
    error.value = err.message
    emit('error', err)
  } finally {
    loading.value = false
  }
}

// 切换 Sheet
const switchSheet = (index) => {
  currentSheetIndex.value = index
  selectedCell.value = null
}

// 获取列名 (A, B, C, ..., AA, AB, ...)
const getColumnName = (index) => {
  let name = ''
  let num = index
  while (num >= 0) {
    name = String.fromCharCode(65 + (num % 26)) + name
    num = Math.floor(num / 26) - 1
  }
  return name
}

// 格式化单元格值
const formatCell = (value) => {
  if (value === null || value === undefined || value === '') {
    return ''
  }
  if (typeof value === 'number') {
    // 如果是日期序列号
    if (value > 40000 && value < 50000) {
      const date = XLSX.SSF.parse_date_code(value)
      return `${date.y}-${String(date.m).padStart(2, '0')}-${String(date.d).padStart(2, '0')}`
    }
    // 格式化数字
    return value.toLocaleString()
  }
  return String(value)
}

// 获取单元格样式类
const getCellClass = (value) => {
  const classes = []
  if (typeof value === 'number') {
    classes.push('number-cell')
  }
  if (value === null || value === undefined || value === '') {
    classes.push('empty-cell')
  }
  return classes
}

// 选择单元格
const selectCell = (row, col) => {
  selectedCell.value = { row, col }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 下载 Excel
const downloadExcel = () => {
  if (!workbook.value) return
  XLSX.writeFile(workbook.value, fileName.value)
}

// 复制到剪贴板
const copyToClipboard = async () => {
  try {
    const text = currentData.value
      .map(row => row.join('\t'))
      .join('\n')
    await navigator.clipboard.writeText(text)
    alert('已复制到剪贴板')
  } catch (err) {
    alert('复制失败: ' + err.message)
  }
}

// 重置查看器
const resetViewer = () => {
  fileLoaded.value = false
  fileName.value = ''
  fileSize.value = 0
  sheets.value = []
  currentSheetIndex.value = 0
  workbook.value = null
  selectedCell.value = null
  error.value = ''
}

// 如果传入了 file prop，自动加载
if (props.file) {
  loadFile(props.file)
}
</script>

<style scoped>
.excel-viewer {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 上传区域 */
.upload-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.drop-zone {
  width: 100%;
  max-width: 500px;
  padding: 60px 40px;
  border: 3px dashed #d0d0d0;
  border-radius: 12px;
  text-align: center;
  background: #fafafa;
  transition: all 0.3s ease;
  cursor: pointer;
}

.drop-zone.drag-over {
  border-color: #4CAF50;
  background: #e8f5e9;
  transform: scale(1.02);
}

.upload-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.upload-button {
  display: inline-block;
  padding: 12px 32px;
  margin: 20px 0;
  background: #4CAF50;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: background 0.3s ease;
}

.upload-button:hover {
  background: #45a049;
}

.hint {
  color: #888;
  font-size: 14px;
  margin-top: 10px;
}

/* 内容区域 */
.excel-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-name {
  font-weight: 600;
  font-size: 14px;
}

.file-size {
  color: #666;
  font-size: 12px;
}

.actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px 16px;
  border: 1px solid #d0d0d0;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #f0f0f0;
}

.action-btn.danger:hover {
  background: #ffebee;
  border-color: #f44336;
  color: #f44336;
}

/* Sheet 标签页 */
.sheet-tabs {
  display: flex;
  gap: 4px;
  padding: 8px 16px;
  background: #fafafa;
  border-bottom: 1px solid #e0e0e0;
  overflow-x: auto;
}

.sheet-tab {
  padding: 8px 20px;
  border: none;
  background: transparent;
  border-radius: 4px 4px 0 0;
  cursor: pointer;
  font-size: 13px;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.sheet-tab:hover {
  background: #e0e0e0;
}

.sheet-tab.active {
  background: white;
  font-weight: 600;
  border-bottom: 2px solid #4CAF50;
}

/* 统计信息 */
.stats {
  display: flex;
  gap: 20px;
  padding: 8px 16px;
  background: #f9f9f9;
  font-size: 12px;
  color: #666;
  border-bottom: 1px solid #e0e0e0;
}

/* 表格容器 */
.table-container {
  flex: 1;
  overflow: auto;
  position: relative;
  background: white;
}

/* 表格样式 */
.excel-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.excel-table th,
.excel-table td {
  border: 1px solid #e0e0e0;
  padding: 8px 12px;
  text-align: left;
  min-width: 80px;
}

.excel-table th {
  background: #f5f5f5;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 10;
}

.column-header {
  text-align: center;
  color: #666;
  font-size: 12px;
}

.row-number {
  background: #f9f9f9;
  color: #666;
  text-align: center;
  font-size: 11px;
  min-width: 50px !important;
  position: sticky;
  left: 0;
  z-index: 5;
}

.excel-table th.row-number {
  z-index: 15;
}

.even-row {
  background: #fafafa;
}

.excel-table tbody tr:hover {
  background: #f0f0f0;
}

.number-cell {
  text-align: right;
  font-family: 'Courier New', monospace;
}

.empty-cell {
  color: #ccc;
}

/* 单元格信息 */
.cell-info {
  padding: 8px 16px;
  background: #e3f2fd;
  border-top: 1px solid #90caf9;
  font-size: 13px;
}

/* 加载和错误状态 */
.loading,
.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  color: #f44336;
}

/* 滚动条样式 */
.table-container::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.table-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.table-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 5px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
