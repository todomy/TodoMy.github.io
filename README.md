# 📝 TodoMy

## 🌐 项目介绍
**TodoMy** 是一个基于 GitHub Issues 的静态博客系统，使用 Gmeek 框架自动生成和部署。

## 📊 博客统计
| 统计项 | 数据 | 说明 |
|-------|------|------|
| 📚 文章总数 | [107](https://todomy.github.io/tag.html) | 包含所有公开文章 |
| 💬 评论总数 | 327 | 所有文章的评论统计 |
| 📝 总字数 | 209,105 | 所有文章内容字数 |
| 🌍 网站地址 | [https://todomy.github.io](https://todomy.github.io) | GitHub Pages 部署地址 |
| 🕒 最后更新 | 2025-10-30 10:52:02 | 服务器时区：UTC+8 |

## 🚀 核心特性
- ✅ 基于 GitHub Issues 的内容管理
- ✅ 自动化构建与部署（GitHub Actions）
- ✅ 响应式设计，支持多设备浏览
- ✅ 支持标签分类和文章搜索
- ✅ 提供 RSS 订阅功能
- ✅ 代码高亮与 Markdown 增强

## 📑 最近文章

### 1. [大国之难，不是公平的敌人](https://todomy.github.io/post/da-guo-zhi-nan-%EF%BC%8C-bu-shi-gong-ping-de-di-ren.html)
**发布日期**: 2025-10-17

### 2. [饥饿的齿痕：人类“人相食”全景史（公元前594 - 2023）](https://todomy.github.io/post/ji-e-de-chi-hen-%EF%BC%9A-ren-lei-%E2%80%9C-ren-xiang-shi-%E2%80%9D-quan-jing-shi-%EF%BC%88-gong-yuan-qian-594%20-%202023%EF%BC%89.html)
**发布日期**: 2025-10-15

### 3. [纸上的王冠：新王朝如何借史书证明合法性](https://todomy.github.io/post/zhi-shang-de-wang-guan-%EF%BC%9A-xin-wang-zhao-ru-he-jie-shi-shu-zheng-ming-he-fa-xing.html)
**发布日期**: 2025-10-15

### 4. [《置身事内》导读](https://todomy.github.io/post/%E3%80%8A-zhi-shen-shi-nei-%E3%80%8B-dao-du.html)
**发布日期**: 2025-10-06

### 5. [抽象自由：革命的双刃剑与个体的灾难](https://todomy.github.io/post/chou-xiang-zi-you-%EF%BC%9A-ge-ming-de-shuang-ren-jian-yu-ge-ti-de-zai-nan.html)
**发布日期**: 2025-09-17


## 🔧 技术栈
- **框架**: Gmeek 静态博客生成器
- **托管**: GitHub Pages
- **CI/CD**: GitHub Actions
- **内容源**: GitHub Issues
- **语言**: Python

## 📖 使用指南
1. 在 GitHub Issues 中创建新议题作为博客文章
2. 文章自动发布到博客网站
3. 通过标签管理文章分类
4. 支持 Markdown 格式编写内容

## 👨‍💻 本地开发模式
### 安装依赖
```bash
pip install markdown markdown-codehilite
```

### 使用命令
```bash
# 完整构建
python Gmeek.py --local

# 指定文章
python Gmeek.py --local 文章编号
```

### 注意事项
1. 使用本地开发模式前，需要先生成 blogBase.json 文件（运行一次完整构建）
2. 本地模式下使用 python-markdown 库进行转换，与 GitHub API 转换效果可能略有差异
3. 本地模式下不生成 RSS Feed
4. 本地模式仅用于开发和预览，生产环境建议使用标准构建方式

## ⭐ 欢迎支持
如果您喜欢这个项目，请给我们一个星标⭐，这是对我们最好的鼓励！

---

*本 README 由 Gmeek 自动生成和更新*