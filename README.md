# QuickReview - 刷题小网页

一个简洁高效的本地刷题系统，支持多题库管理、智能推荐、答题记录和统计分析。

## 功能特点

- 📚 **多题库管理**: 支持创建和管理多个独立题库，不同主题分开练习
- 📝 **题目管理**: 支持JSON格式批量上传题目到指定题库
- 🎲 **智能推荐**: 优先推荐错误率高的题目，加强薄弱环节
- ✅ **答题记录**: 自动记录每次答题的正确/错误情况和时间
- 📊 **统计分析**: 详细的复习情况统计，支持按题库筛选
- 🎨 **美观界面**: 现代化的渐变设计，良好的用户体验

## 技术栈

- **后端**: Python 3.12 + Flask + SQLAlchemy
- **前端**: HTML + CSS + JavaScript
- **数据库**: SQLite

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python app.py
```

应用将在 http://127.0.0.1:5000 启动

VScode SSH端口转发用户：确保已设置5000端口转发，然后访问 http://localhost:5000

### 3. 访问页面

- **刷题页面**: http://127.0.0.1:5000
- **题库管理**: http://127.0.0.1:5000/banks
- **统计页面**: http://127.0.0.1:5000/stats
- **上传页面**: http://127.0.0.1:5000/upload

## 使用指南

### 创建题库

1. 访问题库管理页面 `/banks`
2. 输入题库名称和描述（可选）
3. 点击"创建题库"

### 上传题目

1. 访问上传页面 `/upload`
2. 输入题库名称（新建或已存在的题库）
3. 准备JSON格式的题目文件（参考 `example_questions.json`）
4. 选择文件上传或直接粘贴JSON内容

JSON格式示例：
```json
[
  {
    "question": "什么是Python？",
    "answer": "Python是一种高级编程语言..."
  },
  {
    "question": "什么是Flask？",
    "answer": "Flask是一个轻量级的Python Web框架..."
  }
]
```

### 刷题流程

1. 在刷题页面选择题库
2. 点击"下一题"获取题目
3. 在脑海中思考答案
4. 点击"显示答案"查看正确答案
5. 根据自己的回答情况选择"答对了"或"答错了"
6. 系统自动记录并跳转到下一题

### 查看统计

访问统计页面可以看到：
- 可选择题库或查看全部统计
- 题目总数、答题次数、正确率
- 每道题的详细统计（答题次数、正确率、最近复习时间）

题目按照正确率排序，红色边框表示错误率高，需要重点复习。

## 项目结构

```
quickreview/
├── app.py                      # 主应用入口
├── requirements.txt            # Python依赖
├── example_questions.json      # 示例题目
├── backend/
│   ├── models/                 # 数据库模型
│   │   ├── __init__.py
│   │   ├── question_bank.py   # 题库模型
│   │   ├── question.py        # 题目模型
│   │   └── answer_record.py   # 答题记录模型
│   ├── routes/                 # API路由
│   │   ├── bank_routes.py     # 题库相关API
│   │   ├── question_routes.py # 题目相关API
│   │   └── stats_routes.py    # 统计相关API
│   └── repository.py           # 数据库操作封装
├── templates/                  # HTML模板
│   ├── index.html             # 刷题页面
│   ├── banks.html             # 题库管理页面
│   ├── stats.html             # 统计页面
│   └── upload.html            # 上传页面
├── static/
│   └── style.css              # 样式文件
└── data/
    └── quickreview.db         # SQLite数据库（自动生成）
```

## API接口

### 题库相关

- `GET /api/banks/` - 获取所有题库
- `GET /api/banks/<id>` - 获取指定题库
- `POST /api/banks/` - 创建题库
- `DELETE /api/banks/<id>` - 删除题库

### 题目相关

- `GET /api/questions/?bank_id=<id>` - 获取题库的所有题目
- `GET /api/questions/<id>` - 获取指定题目
- `GET /api/questions/random?bank_id=<id>` - 获取题库的随机题目
- `GET /api/questions/<id>/answer` - 获取题目答案
- `POST /api/questions/<id>/record` - 记录答题结果
- `POST /api/questions/upload` - 批量上传题目到题库
- `DELETE /api/questions/<id>` - 删除题目

### 统计相关

- `GET /api/stats/?bank_id=<id>` - 获取题库统计或全部统计
- `GET /api/stats/questions?bank_id=<id>` - 获取题库题目详细统计

## 数据库设计

### QuestionBank 表（题库）
- id: 主键
- name: 题库名称（唯一）
- description: 题库描述
- created_at: 创建时间

### Question 表（题目）
- id: 主键
- bank_id: 关联的题库ID
- question: 题目内容
- answer: 答案内容
- created_at: 创建时间

### AnswerRecord 表（答题记录）
- id: 主键
- question_id: 关联的题目ID
- is_correct: 是否正确
- created_at: 答题时间

## 智能推荐算法

系统使用加权随机算法在当前题库中推荐题目：
- 从未做过的题目：权重 = 10
- 从未答对的题目：权重 = 错误次数 + 5
- 其他题目：权重 = 错误次数 + 1

这样可以确保错误率高的题目有更高概率被抽到，帮助用户加强薄弱环节。

## 多题库使用场景

- **分学科学习**: 创建"Python基础"、"算法题"、"面试题"等不同题库
- **分难度练习**: 创建"入门"、"进阶"、"高级"等不同难度题库
- **分阶段复习**: 创建"第一轮"、"第二轮"等复习题库
- **独立统计**: 每个题库的答题记录和统计独立，方便针对性复习

## 许可证

MIT License
