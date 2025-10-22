# TodoMy 博客

![GitHub](https://img.shields.io/github/license/TodoMy/TodoMy.github.io)
![GitHub last commit](https://img.shields.io/github/last-commit/TodoMy/TodoMy.github.io)

## 博客简介

TodoMy 是一个基于 GitHub Issues 构建的个人知识库和思考记录平台。通过将 GitHub Issues 作为内容管理系统，结合 Gmeek 工具自动生成静态网站，实现了简单高效的博客管理方式。

**博客地址：** [https://todomy.github.io](https://todomy.github.io)

## 技术特点

- **基于 GitHub Issues 的内容管理**：利用 GitHub 的成熟生态系统管理博客内容
- **自动静态站点生成**：通过 Gmeek 工具将 Issues 自动转换为静态 HTML 页面
- **自动化部署**：使用 GitHub Actions 实现内容发布后的自动构建和部署
- **标签分类系统**：支持通过标签对文章进行分类和筛选
- **RSS 订阅功能**：提供 RSS 订阅，方便读者获取最新更新
- **响应式设计**：适配各种设备屏幕，提供良好的阅读体验

## 特色功能

### 文章管理
- 通过 GitHub Issues 编辑器创建和编辑文章
- 支持 Markdown 格式，方便排版
- 评论系统基于 GitHub Issues 的评论功能

### 访问统计
- 集成了页面访问统计功能
- 可查看总访问量和单篇文章浏览量

### 搜索功能
- 支持按标签筛选文章
- 提供文章列表分页浏览

## 项目结构

```
├── .github/workflows/  # GitHub Actions 工作流配置
├── backup/             # 文章备份目录
├── docs/               # 生成的静态网站文件
│   ├── index.html      # 首页
│   ├── post/           # 文章页面
│   ├── postList.json   # 文章列表数据
│   ├── rss.xml         # RSS 订阅文件
│   └── tag.html        # 标签页面
├── plugins/            # 前端插件
├── templates/          # HTML 模板文件
└── Gmeek.py            # 核心生成工具
```

## 使用说明

### 发布新文章
1. 在 GitHub 仓库的 Issues 页面创建新 Issue
2. 添加适当的标签（可选）
3. 编写 Markdown 格式的内容
4. 提交后，GitHub Actions 会自动构建并部署

### 编辑文章
- 直接在对应 Issue 中编辑内容
- 保存后会自动更新网站

### 标签管理
- 使用不同标签对文章进行分类
- 标签页面展示所有标签及其对应文章

## 开发与定制

### 本地开发
1. 克隆仓库：`git clone https://github.com/TodoMy/TodoMy.github.io.git`
2. 安装依赖：`pip install -r requirements.txt`
3. 配置 `config.json` 文件
4. 运行生成脚本：`python Gmeek.py`

### 定制化
- 修改 `templates` 目录下的 HTML 模板可自定义页面样式
- 调整 `config.json` 可配置博客基本信息

## 关于 Gmeek

Gmeek 是本博客使用的核心生成工具，它实现了：
- GitHub Issues API 的交互
- Markdown 到 HTML 的转换
- 静态页面的生成与组织
- RSS 订阅文件的创建

## 贡献指南

欢迎对本博客项目提出建议或贡献代码！您可以：
- 提交 Issue 反馈问题或建议
- 提交 Pull Request 改进代码
- 分享您对博客内容的见解和评论

## 许可证

本项目采用 MIT 许可证 - 详情请查看 [LICENSE](LICENSE) 文件

## 联系方式

- GitHub: [TodoMy](https://github.com/TodoMy)
- 博客: [https://todomy.github.io](https://todomy.github.io)

---

*感谢访问 TodoMy 博客！希望您能在这里找到有价值的内容和思考。*
>>>>>>> 7722cbd (更新代码和README)
