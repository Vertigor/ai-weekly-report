# 人工智能行业动态周报生成器

> 国网江苏电力有限公司信息通信分公司 · 数据运营中心（人工智能中心）

面向电力行业领导的 AI 行业动态周报 PDF 生成工具。配合 Manus 定时任务，实现每周日上午 11:00 自动生成。

## 功能特性

- **专业 PDF 排版**：严格复刻参考版式，包含封面、关键数据表格、板块标题条、配图、周度洞察等
- **JSON 数据验证**：自动检查数据完整性和规范性
- **Manus 定时任务**：每周日上午 11:00（北京时间）由 Manus 自动执行完整流程（新闻搜索 → 筛选 → 撰写 → 配图 → 生成 PDF）

## 项目结构

```
ai-weekly-report/
├── main.py                     # 主入口（JSON验证 + PDF生成）
├── requirements.txt            # Python 依赖
├── src/
│   ├── pdf_renderer.py         # PDF 渲染器
│   └── validator.py            # JSON 数据验证器
├── templates/
│   └── json_schema.json        # JSON 数据结构示例
├── data/                       # 生成的 JSON 数据
└── output/                     # 生成的 PDF 文件
```

## 使用方法

### 安装依赖

```bash
pip install -r requirements.txt
sudo apt-get install -y fonts-wqy-microhei  # Linux 中文字体
```

### 从 JSON 生成 PDF

```bash
python main.py data/weekly_report.json
python main.py data/weekly_report.json -o output/
```

## JSON 数据结构

详见 `templates/json_schema.json`，主要包含：

- `report_title` / `report_period` / `report_date`：报告基本信息
- `editor_note`：编者按
- `sections`：新闻板块（核心看点、技术前沿、行业应用、政策资本）
- `weekly_insight`：周度洞察
- `data_highlights`：关键数据亮点（指标、数值、变化、来源）

## 版式说明

PDF 严格遵循以下设计规范：

- 封面页：标题 + 副标题 + 编者按 + 关键数据表格
- 板块标题：红色背景条 + 白色文字
- 电力行业启示：蓝色左竖线 + 浅灰背景
- 页眉：左"人工智能行业动态周报" 右"报告周期"
- 页脚：左"国网江苏电力有限公司信息通信分公司" 中页码 右"内部参考 请勿外传"

## 许可证

内部使用，请勿外传。
