import os
import json
import datetime

# 模拟博客对象
class MockBlog:
    def __init__(self):
        self.TZ = datetime.timezone.utc
        self.root_dir = './'
        # 模拟blogBase数据
        self.blogBase = {
            "title": "TodoMy",
            "homeUrl": "https://todomy.github.io",
            "postListJson": [{}, {}],  # 包含一个空对象作为第一个元素
            "singeListJson": {}
        }
        # 模拟标签数据
        self.labelColorDict = {
            "技术": "blue",
            "生活": "green",
            "工作": "orange"
        }

# 设置环境变量
def test_generate_readme():
    os.environ['GITHUB_EVENT_NAME'] = 'manual'
    os.environ['GITHUB_WORKSPACE'] = os.path.abspath('.')
    
    # 创建模拟博客对象
    blog = MockBlog()
    
    # 模拟统计数据
    commentNumSum = 327
    wordCount = 211653
    
    # 计算额外统计信息
    single_page_count = len(blog.blogBase.get("singeListJson", {}))
    total_pages = single_page_count + len(blog.blogBase["postListJson"]) - 1
    
    # 计算标签数量
    label_count = len(blog.labelColorDict)
    
    # 生成更专业的README
    readme="# %s :link: [%s](%s) \r\n\r\n" % (blog.blogBase["title"], blog.blogBase["title"], blog.blogBase["homeUrl"])
    
    # 项目简介部分
    readme += "## 📝 项目简介\r\n"
    readme += "这是一个基于GitHub Issues的静态博客系统，通过Gmeek自动生成和部署。\r\n\r\n"
    
    # 统计信息卡片
    readme += "## 📊 博客统计\r\n"
    readme += "| 统计项目 | 数量 | | 统计项目 | 数据 |\r\n"
    readme += "|---------|------|---|---------|------|\r\n"
    readme += "| 📄 文章总数 | %d | | 🏷️ 标签数量 | %d |\r\n" % (len(blog.blogBase["postListJson"]) - 1, label_count)
    readme += "| 📑 单页数量 | %d | | 💬 评论总数 | %d |\r\n" % (single_page_count, commentNumSum)
    readme += "| 🔗 总页面数 | %d | | 📚 总字数 | %d |\r\n" % (total_pages, wordCount)
    readme += "| 🌍 主页链接 | [访问博客](%s) | | ⏰ 最后更新 | %s |\r\n\r\n" % (blog.blogBase["homeUrl"], datetime.datetime.now(blog.TZ).strftime('%Y-%m-%d %H:%M:%S'))
    
    # 功能特点部分
    readme += "## ✨ 功能特点\r\n"
    readme += "- 🎯 基于GitHub Issues的内容管理\r\n"
    readme += "- 🚀 自动化部署与更新\r\n"
    readme += "- 🌓 支持明暗主题切换\r\n"
    readme += "- 🌍 多语言支持\r\n"
    readme += "- 📱 响应式设计，适配各种设备\r\n"
    readme += "- 📊 文章统计与标签分类\r\n"
    readme += "- 📝 Markdown格式支持\r\n"
    readme += "- 📡 RSS订阅功能\r\n\r\n"
    
    # 技术栈部分
    readme += "## 🛠️ 技术栈\r\n"
    readme += "- 🐍 Python\r\n"
    readme += "- 📄 GitHub Pages\r\n"
    readme += "- 🤖 GitHub Actions\r\n"
    readme += "- 📝 Markdown\r\n"
    readme += "- 🌐 HTML/CSS/JavaScript\r\n\r\n"
    
    # 底部信息
    readme += "## 💡 提示\r\n"
    readme += "README由Gmeek自动生成和更新，请勿手动修改。\r\n\r\n"
    
    readme += "## 📅 最近活动\r\n"
    readme += "- 🚀 持续更新中...\r\n\r\n"
    
    readme += "## ❤️ 致谢\r\n"
    readme += "Powered by :heart: [Gmeek](https://github.com/Meekdai/Gmeek) - A beautiful GitHub Issues based blog generator.\r\n"
    
    # 写入README文件
    readmeFile=open(os.environ['GITHUB_WORKSPACE']+"/README_Test.md","w", encoding='utf-8')
    readmeFile.write(readme)
    readmeFile.close()
    
    print("README测试文件已生成: README_Test.md")

if __name__ == "__main__":
    test_generate_readme()