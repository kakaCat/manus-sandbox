# 测试文件说明

## 📝 创建测试 Excel 文件

为了测试 Excel 查看器组件，你需要准备一些测试文件。

### 方法 1: 使用 Excel/LibreOffice 创建

#### 简单测试文件

创建一个名为 `test-simple.xlsx` 的文件，包含：

**Sheet1: 用户信息**

| 姓名 | 年龄 | 城市 | 邮箱 |
|------|------|------|------|
| 张三 | 25 | 北京 | zhangsan@example.com |
| 李四 | 30 | 上海 | lisi@example.com |
| 王五 | 28 | 广州 | wangwu@example.com |
| 赵六 | 35 | 深圳 | zhaoliu@example.com |

#### 多 Sheet 测试文件

创建一个名为 `test-multiple-sheets.xlsx` 的文件，包含：

**Sheet1: 销售数据**

| 日期 | 产品 | 数量 | 单价 | 总额 |
|------|------|------|------|------|
| 2024-01-01 | 产品A | 100 | 50.00 | 5000.00 |
| 2024-01-02 | 产品B | 150 | 30.00 | 4500.00 |
| 2024-01-03 | 产品C | 200 | 25.00 | 5000.00 |

**Sheet2: 库存数据**

| 产品 | 库存 | 预警线 | 状态 |
|------|------|--------|------|
| 产品A | 500 | 100 | 正常 |
| 产品B | 80 | 100 | 预警 |
| 产品C | 1000 | 200 | 正常 |

**Sheet3: 员工信息**

| 工号 | 姓名 | 部门 | 入职日期 |
|------|------|------|----------|
| E001 | 张三 | 技术部 | 2020-01-15 |
| E002 | 李四 | 销售部 | 2019-06-20 |
| E003 | 王五 | 市场部 | 2021-03-10 |

#### 大数据测试文件

创建一个名为 `test-large.xlsx` 的文件，包含：

- 50 列
- 1000+ 行
- 测试滚动性能

### 方法 2: 使用 Python 生成

安装依赖：

```bash
pip install openpyxl
```

创建脚本 `generate_test_files.py`:

```python
from openpyxl import Workbook
from datetime import datetime, timedelta
import random

# 创建简单测试文件
def create_simple_test():
    wb = Workbook()
    ws = wb.active
    ws.title = "用户信息"

    # 表头
    ws.append(["姓名", "年龄", "城市", "邮箱"])

    # 数据
    data = [
        ["张三", 25, "北京", "zhangsan@example.com"],
        ["李四", 30, "上海", "lisi@example.com"],
        ["王五", 28, "广州", "wangwu@example.com"],
        ["赵六", 35, "深圳", "zhaoliu@example.com"],
    ]

    for row in data:
        ws.append(row)

    wb.save("test-simple.xlsx")
    print("✅ 创建 test-simple.xlsx")


# 创建多 Sheet 测试文件
def create_multiple_sheets_test():
    wb = Workbook()

    # Sheet1: 销售数据
    ws1 = wb.active
    ws1.title = "销售数据"
    ws1.append(["日期", "产品", "数量", "单价", "总额"])

    start_date = datetime(2024, 1, 1)
    products = ["产品A", "产品B", "产品C", "产品D", "产品E"]

    for i in range(30):
        date = start_date + timedelta(days=i)
        product = random.choice(products)
        quantity = random.randint(50, 200)
        price = random.uniform(20, 100)
        total = quantity * price

        ws1.append([
            date.strftime("%Y-%m-%d"),
            product,
            quantity,
            round(price, 2),
            round(total, 2)
        ])

    # Sheet2: 库存数据
    ws2 = wb.create_sheet("库存数据")
    ws2.append(["产品", "库存", "预警线", "状态"])

    for product in products:
        stock = random.randint(50, 1000)
        warning = 100
        status = "正常" if stock > warning else "预警"
        ws2.append([product, stock, warning, status])

    # Sheet3: 员工信息
    ws3 = wb.create_sheet("员工信息")
    ws3.append(["工号", "姓名", "部门", "入职日期"])

    departments = ["技术部", "销售部", "市场部", "人事部", "财务部"]
    names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十"]

    for i, name in enumerate(names, 1):
        employee_id = f"E{i:03d}"
        department = random.choice(departments)
        join_date = start_date - timedelta(days=random.randint(365, 1825))

        ws3.append([
            employee_id,
            name,
            department,
            join_date.strftime("%Y-%m-%d")
        ])

    wb.save("test-multiple-sheets.xlsx")
    print("✅ 创建 test-multiple-sheets.xlsx")


# 创建大数据测试文件
def create_large_test():
    wb = Workbook()
    ws = wb.active
    ws.title = "大数据测试"

    # 表头（50列）
    headers = ["序号"] + [f"列{i}" for i in range(1, 50)]
    ws.append(headers)

    # 数据（1000行）
    print("生成 1000 行数据...")
    for i in range(1, 1001):
        row = [i] + [random.randint(1, 100) for _ in range(49)]
        ws.append(row)

        if i % 100 == 0:
            print(f"  已生成 {i} 行")

    wb.save("test-large.xlsx")
    print("✅ 创建 test-large.xlsx")


# 创建日期测试文件
def create_date_test():
    wb = Workbook()
    ws = wb.active
    ws.title = "日期测试"

    ws.append(["日期", "时间", "日期时间", "年份", "月份"])

    start_date = datetime(2024, 1, 1)

    for i in range(20):
        date = start_date + timedelta(days=i * 7)
        ws.append([
            date.date(),
            date.time(),
            date,
            date.year,
            date.month
        ])

    wb.save("test-dates.xlsx")
    print("✅ 创建 test-dates.xlsx")


# 创建数字格式测试文件
def create_number_test():
    wb = Workbook()
    ws = wb.active
    ws.title = "数字格式"

    ws.append(["整数", "小数", "百分比", "货币", "科学计数"])

    for i in range(10):
        ws.append([
            random.randint(1, 1000),
            round(random.uniform(0, 100), 2),
            round(random.uniform(0, 1), 4),
            round(random.uniform(100, 10000), 2),
            random.uniform(1e-10, 1e10)
        ])

    wb.save("test-numbers.xlsx")
    print("✅ 创建 test-numbers.xlsx")


# 创建空值测试文件
def create_empty_test():
    wb = Workbook()
    ws = wb.active
    ws.title = "空值测试"

    ws.append(["姓名", "年龄", "城市", "备注"])

    # 包含空值的数据
    data = [
        ["张三", 25, "北京", "完整数据"],
        ["李四", None, "上海", "年龄为空"],
        ["王五", 28, None, "城市为空"],
        [None, 30, "广州", "姓名为空"],
        ["赵六", None, None, "多个为空"],
        [None, None, None, "全部为空"],
    ]

    for row in data:
        ws.append(row)

    wb.save("test-empty.xlsx")
    print("✅ 创建 test-empty.xlsx")


if __name__ == "__main__":
    print("🚀 开始生成测试文件...\n")

    create_simple_test()
    create_multiple_sheets_test()
    create_large_test()
    create_date_test()
    create_number_test()
    create_empty_test()

    print("\n✅ 所有测试文件已生成！")
    print("\n生成的文件:")
    print("  - test-simple.xlsx           # 简单数据")
    print("  - test-multiple-sheets.xlsx  # 多 Sheet")
    print("  - test-large.xlsx            # 大数据（1000行）")
    print("  - test-dates.xlsx            # 日期格式")
    print("  - test-numbers.xlsx          # 数字格式")
    print("  - test-empty.xlsx            # 空值处理")
```

运行脚本：

```bash
python generate_test_files.py
```

### 方法 3: 下载示例文件

你也可以从以下来源下载示例 Excel 文件：

1. **Sample-Spreadsheets.com**
   - https://sample-spreadsheets.com/

2. **ExcelSampleData.com**
   - https://excelsampledata.com/

3. **Microsoft Templates**
   - https://templates.office.com/

## 🧪 测试场景

### 场景 1: 基础功能测试

使用 `test-simple.xlsx`:
- ✅ 上传文件
- ✅ 查看数据
- ✅ 滚动表格
- ✅ 下载文件
- ✅ 复制数据

### 场景 2: 多 Sheet 测试

使用 `test-multiple-sheets.xlsx`:
- ✅ 显示所有 Sheet 标签
- ✅ 切换 Sheet
- ✅ 各 Sheet 数据正确

### 场景 3: 性能测试

使用 `test-large.xlsx`:
- ✅ 加载速度
- ✅ 滚动流畅度
- ✅ 内存占用

### 场景 4: 数据类型测试

使用 `test-dates.xlsx` 和 `test-numbers.xlsx`:
- ✅ 日期格式化
- ✅ 数字格式化
- ✅ 空值处理

### 场景 5: 边界测试

使用 `test-empty.xlsx`:
- ✅ 空单元格显示
- ✅ 空行处理
- ✅ 全空数据

## 📋 测试清单

创建一个测试清单文件 `test-checklist.md`:

```markdown
# Excel Viewer 测试清单

## 文件上传
- [ ] 拖拽上传 .xlsx 文件
- [ ] 拖拽上传 .xls 文件
- [ ] 拖拽上传 .csv 文件
- [ ] 点击选择文件
- [ ] 上传不支持的格式（应报错）
- [ ] 上传空文件（应报错）
- [ ] 上传损坏的文件（应报错）

## 数据展示
- [ ] 正确显示表头
- [ ] 正确显示数据行
- [ ] 行号正确
- [ ] 列名正确（A, B, C...）
- [ ] 数字右对齐
- [ ] 文本左对齐
- [ ] 空单元格标识

## 多 Sheet
- [ ] 显示所有 Sheet 标签
- [ ] 点击切换 Sheet
- [ ] 当前 Sheet 高亮
- [ ] 单 Sheet 不显示标签

## 工具栏
- [ ] 显示文件名
- [ ] 显示文件大小
- [ ] 下载按钮工作
- [ ] 复制按钮工作
- [ ] 关闭按钮工作

## 交互功能
- [ ] 横向滚动
- [ ] 纵向滚动
- [ ] 点击单元格
- [ ] 显示单元格信息
- [ ] 表头固定
- [ ] 行号固定

## 数据格式
- [ ] 日期格式化
- [ ] 数字千分位
- [ ] 百分比显示
- [ ] 货币符号

## 性能
- [ ] 小文件加载快（< 1秒）
- [ ] 大文件可用（可能较慢）
- [ ] 滚动流畅
- [ ] 内存使用合理

## 响应式
- [ ] 桌面端正常
- [ ] 平板端可用
- [ ] 手机端可用

## 错误处理
- [ ] 文件格式错误提示
- [ ] 加载失败提示
- [ ] 网络错误处理
```

## 🔍 调试技巧

### 查看加载的数据

在浏览器控制台：

```javascript
// 文件加载后
console.log('Sheets:', data.sheets)
console.log('数据:', data.data)

// 查看第一个 Sheet 的第一行
console.log(data.data[0].data[0])
```

### 监控性能

```javascript
console.time('文件加载')
// ... 加载文件
console.timeEnd('文件加载')

console.time('Sheet 切换')
// ... 切换 Sheet
console.timeEnd('Sheet 切换')
```

### 内存监控

```javascript
// 加载前
console.log('内存使用:', performance.memory.usedJSHeapSize / 1048576, 'MB')

// 加载后
console.log('内存使用:', performance.memory.usedJSHeapSize / 1048576, 'MB')
```

## 📊 测试报告模板

```markdown
# Excel Viewer 测试报告

**测试日期**: 2026-01-09
**测试人**: XXX
**浏览器**: Chrome 120

## 测试文件
- test-simple.xlsx (4 行 x 4 列)
- test-multiple-sheets.xlsx (3 个 Sheet)
- test-large.xlsx (1000 行 x 50 列)

## 测试结果

### 功能测试
- ✅ 文件上传: 通过
- ✅ 数据展示: 通过
- ✅ 多 Sheet: 通过
- ✅ 工具栏: 通过
- ⚠️  大文件: 较慢但可用

### 性能测试
- 小文件加载: < 1 秒
- 大文件加载: ~ 5 秒
- Sheet 切换: < 100ms
- 滚动: 流畅

### 发现的问题
1. 大文件（1000+ 行）滚动略有卡顿
2. 日期格式暂不完美
3. 移动端体验待优化

### 建议
1. 添加虚拟滚动
2. 优化日期格式化
3. 移动端适配
```

---

**提示**: 测试前请确保浏览器控制台打开，以便查看错误和调试信息。
