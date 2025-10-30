# -*- coding: utf-8 -*-
import os
import re
import json
import time
import datetime
import shutil
import urllib
import requests
import argparse
import html
from github import Github
from xpinyin import Pinyin
from feedgen.feed import FeedGenerator
from jinja2 import Environment, FileSystemLoader
from transliterate import translit
from collections import OrderedDict
######################################################################################
i18n={"Search":"Search","switchTheme":"switch theme","home":"home","comments":"comments","run":"run ","days":" days","Previous":"Previous","Next":"Next"}
i18nCN={"Search":"搜索","switchTheme":"切换主题","home":"首页","comments":"评论","run":"网站运行","days":"天","Previous":"上一页","Next":"下一页"}
i18nRU={"Search":"Поиск","switchTheme": "Сменить тему","home":"Главная","comments":"Комментарии","run":"работает ","days":" дней","Previous":"Предыдущая","Next":"Следующая"}
IconBase={
    "post":"M0 3.75C0 2.784.784 2 1.75 2h12.5c.966 0 1.75.784 1.75 1.75v8.5A1.75 1.75 0 0 1 14.25 14H1.75A1.75 1.75 0 0 1 0 12.25Zm1.75-.25a.25.25 0 0 0-.25.25v8.5c0 .138.112.25.25.25h12.5a.25.25 0 0 0 .25-.25v-8.5a.25.25 0 0 0-.25-.25ZM3.5 6.25a.75.75 0 0 1 .75-.75h7a.75.75 0 0 1 0 1.5h-7a.75.75 0 0 1-.75-.75Zm.75 2.25h4a.75.75 0 0 1 0 1.5h-4a.75.75 0 0 1 0-1.5Z",
    "link":"m7.775 3.275 1.25-1.25a3.5 3.5 0 1 1 4.95 4.95l-2.5 2.5a3.5 3.5 0 0 1-4.95 0 .751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018 1.998 1.998 0 0 0 2.83 0l2.5-2.5a2.002 2.002 0 0 0-2.83-2.83l-1.25 1.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042Zm-4.69 9.64a1.998 1.998 0 0 0 2.83 0l1.25-1.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-1.25 1.25a3.5 3.5 0 1 1-4.95-4.95l2.5-2.5a3.5 3.5 0 0 1 4.95 0 .751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018 1.998 1.998 0 0 0-2.83 0l-2.5 2.5a1.998 1.998 0 0 0 0 2.83Z",
    "about":"M10.561 8.073a6.005 6.005 0 0 1 3.432 5.142.75.75 0 1 1-1.498.07 4.5 4.5 0 0 0-8.99 0 .75.75 0 0 1-1.498-.07 6.004 6.004 0 0 1 3.431-5.142 3.999 3.999 0 1 1 5.123 0ZM10.5 5a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z",
    "sun":"M8 10.5a2.5 2.5 0 100-5 2.5 2.5 0 000 5zM8 12a4 4 0 100-8 4 4 0 000 8zM8 0a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0V.75A.75.75 0 018 0zm0 13a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 018 13zM2.343 2.343a.75.75 0 011.061 0l1.06 1.061a.75.75 0 01-1.06 1.06l-1.06-1.06a.75.75 0 010-1.06zm9.193 9.193a.75.75 0 011.06 0l1.061 1.06a.75.75 0 01-1.06 1.061l-1.061-1.06a.75.75 0 010-1.061zM16 8a.75.75 0 01-.75.75h-1.5a.75.75 0 010-1.5h1.5A.75.75 0 0116 8zM3 8a.75.75 0 01-.75.75H.75a.75.75 0 010-1.5h1.5A.75.75 0 013 8zm10.657-5.657a.75.75 0 010 1.061l-1.061 1.06a.75.75 0 11-1.06-1.06l1.06-1.06a.75.75 0 011.06 0zm-9.193 9.193a.75.75 0 010 1.06l-1.06 1.061a.75.75 0 11-1.061-1.06l1.06-1.061a.75.75 0 011.061 0z",
    "moon":"M9.598 1.591a.75.75 0 01.785-.175 7 7 0 11-8.967 8.967.75.75 0 01.961-.96 5.5 5.5 0 007.046-7.046.75.75 0 01.175-.786zm1.616 1.945a7 7 0 01-7.678 7.678 5.5 5.5 0 107.678-7.678z",
    "search":"M15.7 13.3l-3.81-3.83A5.93 5.93 0 0 0 13 6c0-3.31-2.69-6-6-6S1 2.69 1 6s2.69 6 6 6c1.3 0 2.48-.41 3.47-1.11l3.83 3.81c.19.2.45.3.7.3.25 0 .52-.09.7-.3a.996.996 0 0 0 0-1.41v.01zM7 10.7c-2.59 0-4.7-2.11-4.7-4.7 0-2.59 2.11-4.7 4.7-4.7 2.59 0 4.7 2.11 4.7 4.7 0 2.59-2.11 4.7-4.7 4.7z",
    "rss":"M2.002 2.725a.75.75 0 0 1 .797-.699C8.79 2.42 13.58 7.21 13.974 13.201a.75.75 0 0 1-1.497.098 10.502 10.502 0 0 0-9.776-9.776.747.747 0 0 1-.7-.798ZM2.84 7.05h-.002a7.002 7.002 0 0 1 6.113 6.111.75.75 0 0 1-1.49.178 5.503 5.503 0 0 0-4.8-4.8.75.75 0 0 1 .179-1.489ZM2 13a1 1 0 1 1 2 0 1 1 0 0 1-2 0Z",
    "upload":"M2.75 14A1.75 1.75 0 0 1 1 12.25v-2.5a.75.75 0 0 1 1.5 0v2.5c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25v-2.5a.75.75 0 0 1 1.5 0v2.5A1.75 1.75 0 0 1 13.25 14Z M11.78 4.72a.749.749 0 1 1-1.06 1.06L8.75 3.811V9.5a.75.75 0 0 1-1.5 0V3.811L5.28 5.78a.749.749 0 1 1-1.06-1.06l3.25-3.25a.749.749 0 0 1 1.06 0l3.25 3.25Z",
    "github":"M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z",
    "home":"M6.906.664a1.749 1.749 0 0 1 2.187 0l5.25 4.2c.415.332.657.835.657 1.367v7.019A1.75 1.75 0 0 1 13.25 15h-3.5a.75.75 0 0 1-.75-.75V9H7v5.25a.75.75 0 0 1-.75.75h-3.5A1.75 1.75 0 0 1 1 13.25V6.23c0-.531.242-1.034.657-1.366l5.25-4.2Zm1.25 1.171a.25.25 0 0 0-.312 0l-5.25 4.2a.25.25 0 0 0-.094.196v7.019c0 .138.112.25.25.25H5.5V8.25a.75.75 0 0 1 .75-.75h3.5a.75.75 0 0 1 .75.75v5.25h2.75a.25.25 0 0 0 .25-.25V6.23a.25.25 0 0 0-.094-.195Z",
    "sync":"M1.705 8.005a.75.75 0 0 1 .834.656 5.5 5.5 0 0 0 9.592 2.97l-1.204-1.204a.25.25 0 0 1 .177-.427h3.646a.25.25 0 0 1 .25.25v3.646a.25.25 0 0 1-.427.177l-1.38-1.38A7.002 7.002 0 0 1 1.05 8.84a.75.75 0 0 1 .656-.834ZM8 2.5a5.487 5.487 0 0 0-4.131 1.869l1.204 1.204A.25.25 0 0 1 4.896 6H1.25A.25.25 0 0 1 1 5.75V2.104a.25.25 0 0 1 .427-.177l1.38 1.38A7.002 7.002 0 0 1 14.95 7.16a.75.75 0 0 1-1.49.178A5.5 5.5 0 0 0 8 2.5Z",
    "copy":"M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 0 1 0 1.5h-1.5a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-1.5a.75.75 0 0 1 1.5 0v1.5A1.75 1.75 0 0 1 9.25 16h-7.5A1.75 1.75 0 0 1 0 14.25Z M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0 1 14.25 11h-7.5A1.75 1.75 0 0 1 5 9.25Zm1.75-.25a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-7.5a.25.25 0 0 0-.25-.25Z",
    "check":"M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"
}
######################################################################################
class GMEEK():
    def __init__(self,options):
        self.options=options
        
        self.root_dir='docs/'
        self.static_dir='static/'
        self.post_folder='post/'
        self.backup_dir='backup/'
        self.post_dir=self.root_dir+self.post_folder
        
        # 初始化默认值
        self.github_available = False
        self.repo = None
        self.feed = None
        self.oldFeedString = ''
        self.labelColorDict = json.loads('{}')
        
        # 检查是否为本地开发模式
        self.local_mode = self.options.github_token == "local_development"
        
        # 尝试连接GitHub API，除非是本地开发模式
        if not self.local_mode:
            try:
                if not self.options.github_token:
                    print("⚠️ 未提供GitHub Token，尝试使用公共访问权限")
                    user = Github()  # 无token的公共访问
                else:
                    user = Github(self.options.github_token)
                    print(f"✅ 成功连接到GitHub API")
                
                self.repo = self.get_repo(user, options.repo_name)
                print(f"✅ 成功获取仓库: {options.repo_name}")
                self.feed = FeedGenerator()
                self.github_available = True
                
                # 获取标签颜色
                try:
                    for label in self.repo.get_labels():
                        self.labelColorDict[label.name] = '#' + label.color
                    print(f"✅ 获取到 {len(self.labelColorDict)} 个标签颜色")
                except Exception as e:
                    print(f"⚠️ 获取标签颜色失败: {e}")
                    # 如果无法获取标签颜色，使用默认颜色
                    if not self.labelColorDict:
                        self.labelColorDict = {
                            "默认": "#0075ca",
                            "技术": "#107c10",
                            "生活": "#d13438",
                            "笔记": "#8a2be2",
                            "其他": "#6c757d"
                        }
                        print(f"✅ 使用默认标签颜色: {self.labelColorDict}")
            except Exception as e:
                print(f"❌ GitHub API连接失败: {e}")
                # 检查是否有现有配置可以使用
                if os.path.exists("blogBase.json"):
                    try:
                        with open("blogBase.json", "r", encoding="utf-8") as f:
                            old_config = json.load(f)
                            if "labelColorDict" in old_config:
                                self.labelColorDict = old_config["labelColorDict"]
                                print(f"✅ 从现有配置加载标签颜色")
                    except Exception as e:
                        print(f"❌ 读取现有配置失败: {e}")
                
                # 设置默认标签颜色
                if not self.labelColorDict:
                    self.labelColorDict = {
                        "默认": "#0075ca",
                        "技术": "#107c10",
                        "生活": "#d13438",
                        "笔记": "#8a2be2",
                        "其他": "#6c757d"
                    }
                    print(f"✅ 使用默认标签颜色")
        else:
            print("📝 本地开发模式：跳过GitHub API连接")
            # 在本地开发模式下，从现有配置加载标签颜色
            if os.path.exists("blogBase.json"):
                try:
                    with open("blogBase.json", "r", encoding="utf-8") as f:
                        old_config = json.load(f)
                        if "labelColorDict" in old_config:
                            self.labelColorDict = old_config["labelColorDict"]
                            print(f"✅ 从blogBase.json加载标签颜色")
                except Exception as e:
                    print(f"❌ 读取blogBase.json失败: {e}")
            
            # 如果加载失败，使用默认标签颜色
            if not self.labelColorDict:
                self.labelColorDict = {
                    "默认": "#0075ca",
                    "技术": "#107c10",
                    "生活": "#d13438",
                    "笔记": "#8a2be2",
                    "其他": "#6c757d"
                }
                print(f"✅ 使用默认标签颜色")
        
        # 加载默认配置
        self.defaultConfig()
        
    def cleanFile(self):
        print("🔄 开始清理和准备工作目录...")
        workspace_path = os.environ.get('GITHUB_WORKSPACE', '.')
        
        # 清理backup目录
        for backup_path in [
            os.path.join(workspace_path, self.backup_dir),
            self.backup_dir
        ]:
            if os.path.exists(backup_path):
                try:
                    shutil.rmtree(backup_path)
                    print(f"✅ 已清理目录: {backup_path}")
                except Exception as e:
                    print(f"❌ 清理目录失败 {backup_path}: {e}")
        
        # 特殊处理root_dir，保留plugins目录
        root_paths = [
            os.path.join(workspace_path, self.root_dir),
            self.root_dir
        ]
        
        for root_path in root_paths:
            if os.path.exists(root_path):
                try:
                    # 检查是否在GitHub Actions环境中运行
                    is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
                    
                    if is_github_actions:
                        # 在GitHub Actions中运行时，保留plugins目录
                        plugins_dir = os.path.join(root_path, 'plugins')
                        plugins_content = {}
                        
                        # 如果plugins目录存在，先保存其内容
                        if os.path.exists(plugins_dir):
                            for item in os.listdir(plugins_dir):
                                item_path = os.path.join(plugins_dir, item)
                                if os.path.isfile(item_path):
                                    with open(item_path, 'rb') as f:
                                        plugins_content[item] = f.read()
                            print(f"📁 已保存plugins目录中的{len(plugins_content)}个文件")
                    
                    # 删除并重新创建root_dir
                    shutil.rmtree(root_path)
                    print(f"✅ 已清理目录: {root_path}")
                    
                    # 如果在GitHub Actions中且保存了plugins内容，恢复它们
                    if is_github_actions and plugins_content:
                        os.makedirs(plugins_dir, exist_ok=True)
                        for item_name, content in plugins_content.items():
                            with open(os.path.join(plugins_dir, item_name), 'wb') as f:
                                f.write(content)
                        print(f"✅ 已恢复plugins目录中的{len(plugins_content)}个文件")
                except Exception as e:
                    print(f"❌ 清理目录失败 {root_path}: {e}")
        
        # 创建必要的目录
        for path in [self.backup_dir, self.root_dir, self.post_dir]:
            try:
                os.makedirs(path, exist_ok=True)
                print(f"✅ 已创建目录: {path}")
            except Exception as e:
                print(f"❌ 创建目录失败 {path}: {e}")
                raise

        # 复制静态资源，添加进度和错误处理
        if os.path.exists(self.static_dir):
            items = os.listdir(self.static_dir)
            print(f"📁 开始复制 {len(items)} 个静态资源...")
            
            for i, item in enumerate(items, 1):
                src = os.path.join(self.static_dir, item)
                dst = os.path.join(self.root_dir, item)
                try:
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)  # 使用copy2保留元数据
                        print(f"✅ ({i}/{len(items)}) 已复制文件: {item}")
                    elif os.path.isdir(src):
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                        print(f"✅ ({i}/{len(items)}) 已复制目录: {item}")
                except Exception as e:
                    print(f"⚠️ ({i}/{len(items)}) 复制失败 {item}: {e}")
        else:
            print("⚠️ static目录不存在，跳过静态资源复制")
        
        # 检查配置中是否启用了plugins目录自动复制功能
        # 在config.json中添加"autoCopyPlugins": false可以禁用自动复制
        auto_copy_plugins = self.blogBase.get("autoCopyPlugins", True)
        
        if auto_copy_plugins:
            print("🔄 启用了plugins目录自动复制功能")
            # 复制plugins目录到docs目录，确保CSS和JS资源可用
            plugins_dir = 'plugins'
            dst_plugins_dir = os.path.join(self.root_dir, plugins_dir)
            
            # 确保目标目录存在
            os.makedirs(dst_plugins_dir, exist_ok=True)
            
            if os.path.exists(plugins_dir):
                items = os.listdir(plugins_dir)
                print(f"📁 发现plugins目录，包含 {len(items)} 个文件")
                
                # 记录复制的文件数
                copied_count = 0
                failed_count = 0
                
                for i, item in enumerate(items, 1):
                    src = os.path.join(plugins_dir, item)
                    dst = os.path.join(dst_plugins_dir, item)
                    try:
                        if os.path.isfile(src):
                            shutil.copy2(src, dst)  # 使用copy2保留元数据
                            copied_count += 1
                            print(f"✅ ({i}/{len(items)}) 已复制插件文件: {item}")
                    except Exception as e:
                        failed_count += 1
                        print(f"⚠️ ({i}/{len(items)}) 复制插件文件失败 {item}: {e}")
                
                print(f"📊 插件复制完成 - 成功: {copied_count}, 失败: {failed_count}")
            else:
                print(f"ℹ️ plugins目录不存在，跳过复制")
                print(f"ℹ️ 使用现有的docs/plugins目录中的资源")
        else:
            print("ℹ️ 已禁用plugins目录自动复制功能")
            print("ℹ️ 使用手动维护的docs/plugins目录中的资源")

    def defaultConfig(self):
        dconfig={"singlePage":[],"startSite":"","filingNum":"","onePageListNum":15,"commentLabelColor":"#006b75","yearColorList":["#bc4c00", "#0969da", "#1f883d", "#A333D0"],"i18n":"CN","themeMode":"manual","dayTheme":"light","nightTheme":"dark","urlMode":"pinyin","script":"","style":"","head":"","indexScript":"","indexStyle":"","bottomText":"","showPostSource":1,"iconList":{},"UTC":+8,"rssSplit":"sentence","exlink":{},"needComment":1,"allHead":""}
        config=json.loads(open('config.json', 'r', encoding='utf-8').read())
        self.blogBase={**dconfig,**config}.copy()
        self.blogBase["postListJson"]=json.loads('{}')
        self.blogBase["singeListJson"]=json.loads('{}')
        self.blogBase["labelColorDict"]=self.labelColorDict
        if "displayTitle" not in self.blogBase:
            self.blogBase["displayTitle"]=self.blogBase["title"]

        if "faviconUrl" not in self.blogBase:
            self.blogBase["faviconUrl"]=self.blogBase["avatarUrl"]

        if "ogImage" not in self.blogBase:
            self.blogBase["ogImage"]=self.blogBase["avatarUrl"]

        if "primerCSS" not in self.blogBase:
            self.blogBase["primerCSS"]="<link href='/plugins/primer.css' rel='stylesheet' />"

        if "homeUrl" not in self.blogBase:
            if str(self.repo.name).lower() == (str(self.repo.owner.login) + ".github.io").lower():
                self.blogBase["homeUrl"] = f"https://{self.repo.name}"
            else:
                self.blogBase["homeUrl"] = f"https://{self.repo.owner.login}.github.io/{self.repo.name}"
        print("GitHub Pages URL: ", self.blogBase["homeUrl"])

        if self.blogBase["i18n"]=="CN":
            self.i18n=i18nCN
        elif self.blogBase["i18n"]=="RU":
            self.i18n=i18nRU
        else:
            self.i18n=i18n
        
        self.TZ=datetime.timezone(datetime.timedelta(hours=self.blogBase["UTC"]))

    def get_repo(self,user:Github, repo:str):
        return user.get_repo(repo)

    def markdown2html(self, mdstr):
        # 本地模式或GitHub API不可用时，使用python-markdown库
        if self.local_mode or not self.github_available:
            try:
                # 尝试导入python-markdown库
                import markdown
                # 启用扩展以获得更好的Markdown支持
                html = markdown.markdown(
                    mdstr, 
                    extensions=[
                        'fenced_code',      # 支持代码块
                        'codehilite',       # 代码高亮
                        'tables',           # 表格支持
                        'toc',              # 目录生成
                        'nl2br',            # 换行转<br>
                        'footnotes'         # 脚注支持
                    ]
                )
                print("📝 使用python-markdown进行本地转换")
                return html
            except ImportError:
                print("⚠️ python-markdown库未安装，使用基本转换")
                # 如果没有安装python-markdown，使用备用方案
                return self._basic_markdown_convert(mdstr)
            except Exception as e:
                print(f"⚠️ Markdown转换出错: {e}，使用基本转换")
                return self._basic_markdown_convert(mdstr)
        
        # 正常模式：使用GitHub API转换Markdown为HTML
        payload = {"text": mdstr, "mode": "gfm"}
        headers = {}
        
        # 仅在有token时添加认证头
        if self.options.github_token:
            headers["Authorization"] = "token {}".format(self.options.github_token)
            
        try:
            response = requests.post("https://api.github.com/markdown", json=payload, headers=headers)
            response.raise_for_status()  # Raises an exception if status code is not 200
            return response.text
        except requests.RequestException as e:
            print(f"⚠️ GitHub API Markdown转换失败: {e}，尝试无认证请求...")
            try:
                # 尝试无认证请求
                response = requests.post("https://api.github.com/markdown", json=payload)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e2:
                print(f"⚠️ 无认证请求也失败: {e2}，使用备用转换")
                return self._basic_markdown_convert(mdstr)
    
    def _basic_markdown_convert(self, mdstr):
        """基本的Markdown转换作为最后备用方案"""
        import html
        # 先进行HTML转义
        text = html.escape(mdstr)
        
        # 处理标题
        for i in range(6, 0, -1):
            level = '#' * i
            text = text.replace(f"\n{level} ", f"\n<h{i}>")
        
        # 处理列表项
        text = re.sub(r'^\s*\*\s', '<li>', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s', '<li>', text, flags=re.MULTILINE)
        
        # 处理加粗和斜体（简单实现）
        text = re.sub(r'\*\*(.+?)\*\*', '<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', '<em>\1</em>', text)
        
        # 处理代码块（简单实现）
        text = re.sub(r'```([\s\S]*?)```', '<pre><code>\1</code></pre>', text)
        text = re.sub(r'`([^`]+)`', '<code>\1</code>', text)
        
        # 处理链接（简单实现）
        text = re.sub(r'\[(.*?)\]\((.*?)\)', '<a href="\2">\1</a>', text)
        
        # 处理段落
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        for p in paragraphs:
            # 跳过已经有HTML标签的行
            if not re.match(r'^\s*<[h1-6li]>|<pre>|<code>', p):
                p = f'<p>{p}</p>'
            formatted_paragraphs.append(p)
        
        return '\n\n'.join(formatted_paragraphs)

    def renderHtml(self,template,blogBase,postListJson,htmlDir,icon):
        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        template = env.get_template(template)
        output = template.render(blogBase=blogBase,postListJson=postListJson,i18n=self.i18n,IconList=icon)
        f = open(htmlDir, 'w', encoding='UTF-8')
        f.write(output)
        f.close()
        
    def addCacheControlHeaders(self):
        """
        为静态资源文件添加缓存控制配置
        注意：这个方法主要是为了提供配置指导，实际的缓存控制头会在base.html中通过meta标签设置
        对于部署到GitHub Pages的站点，还可以通过创建.nojekyll文件和自定义404页面来优化
        """
        # 检查是否存在.nojekyll文件，如果不存在则创建
        nojekyll_path = os.path.join(self.root_dir, '.nojekyll')
        if not os.path.exists(nojekyll_path):
            with open(nojekyll_path, 'w') as f:
                f.write('')
            print(f"已创建 .nojekyll 文件在 {nojekyll_path}")
        
        # 这里可以添加其他缓存相关的配置文件生成
        # 例如创建 _headers 文件用于GitHub Pages的HTTP头配置
        headers_content = '''/*
  Cache-Control: max-age=31536000, public, must-revalidate
  Expires: Thu, 31 Dec 2025 23:59:59 GMT
  Content-Type: text/html; charset=utf-8
*/

/*.js
  Cache-Control: max-age=31536000, public, must-revalidate
  Expires: Thu, 31 Dec 2025 23:59:59 GMT
*/

/*.css
  Cache-Control: max-age=31536000, public, must-revalidate
  Expires: Thu, 31 Dec 2025 23:59:59 GMT
*/

/*.png,/*.jpg,/*.jpeg,/*.gif,/*.webp,/*.svg
  Cache-Control: max-age=31536000, public, must-revalidate
  Expires: Thu, 31 Dec 2025 23:59:59 GMT
*/
'''
        
        headers_path = os.path.join(self.root_dir, '_headers')
        with open(headers_path, 'w', encoding='utf-8') as f:
            f.write(headers_content)
        print(f"已创建 _headers 文件在 {headers_path}，配置了缓存控制头")
        
        return True

    def createPostHtml(self,issue):
        mdFileName=re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', issue["postTitle"])
        f = open(self.backup_dir+mdFileName+".md", 'r', encoding='UTF-8')
        post_body=self.markdown2html(f.read())
        f.close()
        
        # 图片懒加载优化：将普通img标签转换为懒加载格式
        # 保留原始src作为lazy-src，并设置占位符
        post_body = re.sub(r'<img src="([^"]*)"([^>]*)>', '<img lazy-src="\1"\2 loading="lazy" alt="图片加载中...">', post_body)

        postBase=self.blogBase.copy()

        if '<math-renderer' in post_body:
            post_body=re.sub(r'<math-renderer.*?>','',post_body)
            post_body=re.sub(r'</math-renderer>','',post_body)
            issue["script"]=issue["script"]+'<script>MathJax = {tex: {inlineMath: [["$", "$"]]}};</script><script async src="/plugins/mathjax/tex-mml-chtml.js"></script>'
        
        if '<p class="markdown-alert-title">' in post_body:
            issue["style"]=issue["style"]+'<style>.markdown-alert{padding:0.5rem 1rem;margin-bottom:1rem;border-left:.25em solid var(--borderColor-default,var(--color-border-default));}.markdown-alert .markdown-alert-title {display:flex;font-weight:var(--base-text-weight-medium,500);align-items:center;line-height:1;}.markdown-alert>:first-child {margin-top:0;}.markdown-alert>:last-child {margin-bottom:0;}</style>'
            alerts = {
                'note': 'accent',
                'tip': 'success',
                'important': 'done',
                'warning': 'attention',
                'caution': 'danger'
            }

            for alert, style in alerts.items():
                if f'markdown-alert-{alert}' in post_body:
                    issue["style"] += (
                        f'<style>.markdown-alert.markdown-alert-{alert} {{'
                        f'border-left-color:var(--borderColor-{style}-emphasis, var(--color-{style}-emphasis));'
                        f'background-color:var(--color-{style}-subtle);}}'
                        f'.markdown-alert.markdown-alert-{alert} .markdown-alert-title {{'
                        f'color: var(--fgColor-{style},var(--color-{style}-fg));}}</style>'
                    )

        if '<code class="notranslate">Gmeek-html' in post_body:
            post_body = re.sub(r'<code class="notranslate">Gmeek-html(.*?)</code>', lambda match: html.unescape(match.group(1)), post_body, flags=re.DOTALL)

        postBase["postTitle"]=issue["postTitle"]
        postBase["postUrl"]=self.blogBase["homeUrl"]+"/"+issue["postUrl"]
        postBase["description"]=issue["description"]
        postBase["ogImage"]=issue["ogImage"]
        postBase["postBody"]=post_body
        postBase["commentNum"]=issue["commentNum"]
        postBase["style"]=issue["style"]
        postBase["script"]=issue["script"]
        postBase["head"]=issue["head"]
        postBase["top"]=issue["top"]
        postBase["postSourceUrl"]=issue["postSourceUrl"]
        postBase["repoName"]=options.repo_name
        
        if issue["labels"][0] in self.blogBase["singlePage"]:
            postBase["bottomText"]=''

        if '<pre class="notranslate">' in post_body:
            keys=['sun','moon','sync','home','github','copy','check']
            if '<div class="highlight' in post_body:
                postBase["highlight"]=1
            else:
                postBase["highlight"]=2
        else:
            keys=['sun','moon','sync','home','github']
            postBase["highlight"]=0

        postIcon=dict(zip(keys, map(IconBase.get, keys)))
        self.renderHtml('post.html',postBase,{},issue["htmlDir"],postIcon)
        print("create postPage title=%s file=%s " % (issue["postTitle"],issue["htmlDir"]))

    def createPlistHtml(self):
        self.blogBase["postListJson"]=dict(sorted(self.blogBase["postListJson"].items(),key=lambda x:(x[1]["top"],x[1]["createdAt"]),reverse=True))#使列表由时间排序
        keys=list(OrderedDict.fromkeys(['sun', 'moon','sync', 'search', 'rss', 'upload', 'post'] + self.blogBase["singlePage"]))
        plistIcon={**dict(zip(keys, map(IconBase.get, keys))),**self.blogBase["iconList"]}
        keys=['sun','moon','sync','home','search','post']
        tagIcon=dict(zip(keys, map(IconBase.get, keys)))

        postNum=len(self.blogBase["postListJson"])
        pageFlag=0
        while True:
            topNum=pageFlag*self.blogBase["onePageListNum"]
            print("topNum=%d postNum=%d"%(topNum,postNum))
            if postNum<=self.blogBase["onePageListNum"]:
                if pageFlag==0:
                    onePageList=dict(list(self.blogBase["postListJson"].items())[:postNum])
                    htmlDir=self.root_dir+"index.html"
                    self.blogBase["prevUrl"]="disabled"
                    self.blogBase["nextUrl"]="disabled"
                else:
                    onePageList=dict(list(self.blogBase["postListJson"].items())[topNum:topNum+postNum])
                    htmlDir=self.root_dir+("page%d.html" % (pageFlag+1))
                    if pageFlag==1:
                        self.blogBase["prevUrl"]="/index.html"
                    else:
                        self.blogBase["prevUrl"]="/page%d.html" % pageFlag
                    self.blogBase["nextUrl"]="disabled"

                self.renderHtml('plist.html',self.blogBase,onePageList,htmlDir,plistIcon)
                print("create "+htmlDir)
                break
            else:
                onePageList=dict(list(self.blogBase["postListJson"].items())[topNum:topNum+self.blogBase["onePageListNum"]])
                postNum=postNum-self.blogBase["onePageListNum"]
                if pageFlag==0:
                    htmlDir=self.root_dir+"index.html"
                    self.blogBase["prevUrl"]="disabled"
                    self.blogBase["nextUrl"]="/page2.html"
                else:
                    htmlDir=self.root_dir+("page%d.html" % (pageFlag+1))
                    if pageFlag==1:
                        self.blogBase["prevUrl"]="/index.html"
                    else:
                        self.blogBase["prevUrl"]="/page%d.html" % pageFlag
                    self.blogBase["nextUrl"]="/page%d.html" % (pageFlag+2)

                self.renderHtml('plist.html',self.blogBase,onePageList,htmlDir,plistIcon)
                print("create "+htmlDir)

            pageFlag=pageFlag+1

        self.renderHtml('tag.html',self.blogBase,onePageList,self.root_dir+"tag.html",tagIcon)
        print("create tag.html")

    def createFeedXml(self):
        self.blogBase["postListJson"]=dict(sorted(self.blogBase["postListJson"].items(),key=lambda x:x[1]["createdAt"],reverse=False))#使列表由时间排序
        feed = FeedGenerator()
        feed.title(self.blogBase["title"])
        feed.description(self.blogBase["subTitle"])
        feed.link(href=self.blogBase["homeUrl"])
        feed.image(url=self.blogBase["avatarUrl"],title="avatar", link=self.blogBase["homeUrl"])
        feed.copyright(self.blogBase["title"])
        feed.managingEditor(self.blogBase["title"])
        feed.webMaster(self.blogBase["title"])
        feed.ttl("60")

        for num in self.blogBase["singeListJson"]:
            item=feed.add_item()
            item.guid(self.blogBase["homeUrl"]+"/"+self.blogBase["singeListJson"][num]["postUrl"],permalink=True)
            item.title(self.blogBase["singeListJson"][num]["postTitle"])
            item.description(self.blogBase["singeListJson"][num]["description"])
            item.link(href=self.blogBase["homeUrl"]+"/"+self.blogBase["singeListJson"][num]["postUrl"])
            item.pubDate(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(self.blogBase["singeListJson"][num]["createdAt"])))

        for num in self.blogBase["postListJson"]:
            item=feed.add_item()
            item.guid(self.blogBase["homeUrl"]+"/"+self.blogBase["postListJson"][num]["postUrl"],permalink=True)
            item.title(self.blogBase["postListJson"][num]["postTitle"])
            item.description(self.blogBase["postListJson"][num]["description"])
            item.link(href=self.blogBase["homeUrl"]+"/"+self.blogBase["postListJson"][num]["postUrl"])
            item.pubDate(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(self.blogBase["postListJson"][num]["createdAt"])))

        if self.oldFeedString!='':
            feed.rss_file(self.root_dir+'new.xml')
            newFeed=open(self.root_dir+'new.xml','r',encoding='utf-8')
            new=newFeed.read()
            newFeed.close()

            new=re.sub(r'<lastBuildDate>.*?</lastBuildDate>','',new)
            old=re.sub(r'<lastBuildDate>.*?</lastBuildDate>','',self.oldFeedString)
            os.remove(self.root_dir+'new.xml')
            
            if new==old:
                print("====== rss xml no update ======")
                feedFile=open(self.root_dir+'rss.xml',"w")
                feedFile.write(self.oldFeedString)
                feedFile.close()
                return

        print("====== create rss xml ======")
        feed.rss_file(self.root_dir+'rss.xml')

    def addOnePostJson(self,issue):
        if len(issue.labels)>=1:
            if issue.labels[0].name in self.blogBase["singlePage"]:
                listJsonName='singeListJson'
                htmlFile='{}.html'.format(self.createFileName(issue,useLabel=True))
                gen_Html = self.root_dir+htmlFile
            else:
                listJsonName='postListJson'
                htmlFile='{}.html'.format(self.createFileName(issue))
                gen_Html = self.post_dir+htmlFile

            postNum="P"+str(issue.number)
            self.blogBase[listJsonName][postNum]=json.loads('{}')
            self.blogBase[listJsonName][postNum]["htmlDir"]=gen_Html
            self.blogBase[listJsonName][postNum]["labels"]=[label.name for label in issue.labels]
            self.blogBase[listJsonName][postNum]["postTitle"]=issue.title
            self.blogBase[listJsonName][postNum]["postUrl"]=urllib.parse.quote(gen_Html[len(self.root_dir):])

            self.blogBase[listJsonName][postNum]["postSourceUrl"]="https://github.com/"+options.repo_name+"/issues/"+str(issue.number)
            self.blogBase[listJsonName][postNum]["commentNum"]=issue.get_comments().totalCount

            if issue.body==None:
                self.blogBase[listJsonName][postNum]["description"]=''
                self.blogBase[listJsonName][postNum]["wordCount"]=0
            else:
                self.blogBase[listJsonName][postNum]["wordCount"]=len(issue.body)
                if self.blogBase["rssSplit"]=="sentence":
                    if self.blogBase["i18n"]=="CN":
                        period="。"
                    else:
                        period="."
                else:
                    period=self.blogBase["rssSplit"]
                self.blogBase[listJsonName][postNum]["description"]=issue.body.split(period)[0].replace("\"", "\'")+period
                
            self.blogBase[listJsonName][postNum]["top"]=0
            for event in issue.get_events():
                if event.event=="pinned":
                    self.blogBase[listJsonName][postNum]["top"]=1
                elif event.event=="unpinned":
                    self.blogBase[listJsonName][postNum]["top"]=0

            try:
                postConfig=json.loads(issue.body.split("\r\n")[-1:][0].split("##")[1])
                print("Has Custom JSON parameters")
                print(postConfig)
            except:
                postConfig={}

            if "timestamp" in postConfig:
                self.blogBase[listJsonName][postNum]["createdAt"]=postConfig["timestamp"]
            else:
                self.blogBase[listJsonName][postNum]["createdAt"]=int(time.mktime(issue.created_at.timetuple()))
            
            if "style" in postConfig:
                self.blogBase[listJsonName][postNum]["style"]=self.blogBase["style"]+str(postConfig["style"])
            else:
                self.blogBase[listJsonName][postNum]["style"]=self.blogBase["style"]

            if "script" in postConfig:
                self.blogBase[listJsonName][postNum]["script"]=self.blogBase["script"]+str(postConfig["script"])
            else:
                self.blogBase[listJsonName][postNum]["script"]=self.blogBase["script"]

            if "head" in postConfig:
                self.blogBase[listJsonName][postNum]["head"]=self.blogBase["head"]+str(postConfig["head"])
            else:
                self.blogBase[listJsonName][postNum]["head"]=self.blogBase["head"]

            if "ogImage" in postConfig:
                self.blogBase[listJsonName][postNum]["ogImage"]=postConfig["ogImage"]
            else:
                self.blogBase[listJsonName][postNum]["ogImage"]=self.blogBase["ogImage"]

            thisTime=datetime.datetime.fromtimestamp(self.blogBase[listJsonName][postNum]["createdAt"])
            thisTime=thisTime.astimezone(self.TZ)
            thisYear=thisTime.year
            self.blogBase[listJsonName][postNum]["createdDate"]=thisTime.strftime("%Y-%m-%d")
            self.blogBase[listJsonName][postNum]["dateLabelColor"]=self.blogBase["yearColorList"][int(thisYear)%len(self.blogBase["yearColorList"])]

            mdFileName=re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', issue.title)
            f = open(self.backup_dir+mdFileName+".md", 'w', encoding='UTF-8')
            
            if issue.body==None:
                f.write('')
            else:
                f.write(issue.body)
            f.close()
            return listJsonName

    def runAll(self):
        print("====== start create static html ======")
        self.cleanFile()

        # 如果是本地开发模式，从blogBase.json加载数据
        if self.local_mode:
            print("📁 本地开发模式：从blogBase.json加载文章数据")
            try:
                with open("blogBase.json", "r", encoding="utf-8") as f:
                    old_config = json.load(f)
                    # 复制必要的数据结构
                    if "postListJson" in old_config:
                        self.blogBase["postListJson"] = old_config["postListJson"]
                        print(f"✅ 加载了 {len(self.blogBase['postListJson'])} 篇文章")
                    if "singeListJson" in old_config:
                        self.blogBase["singeListJson"] = old_config["singeListJson"]
            except Exception as e:
                print(f"❌ 从blogBase.json加载数据失败: {e}")
                return
        else:
            # 正常模式：从GitHub获取数据
            if not self.github_available or not self.repo:
                print("❌ GitHub API不可用，无法获取文章数据")
                return
            
            print("📡 从GitHub获取文章数据...")
            try:
                issues = self.repo.get_issues()
                issue_count = 0
                for issue in issues:
                    self.addOnePostJson(issue)
                    issue_count += 1
                print(f"✅ 处理了 {issue_count} 篇文章")
            except Exception as e:
                print(f"❌ 获取文章数据失败: {e}")
                return

        # 生成HTML文件
        try:
            # 处理普通文章
            for post_id, issue in list(self.blogBase["postListJson"].items()):
                if post_id != "labelColorDict":  # 跳过特殊键
                    try:
                        self.createPostHtml(issue)
                    except Exception as e:
                        print(f"⚠️ 生成文章HTML失败 {issue.get('postTitle', '未知标题')}: {e}")
            
            # 处理单页文章
            for post_id, issue in list(self.blogBase["singeListJson"].items()):
                try:
                    self.createPostHtml(issue)
                except Exception as e:
                    print(f"⚠️ 生成单页HTML失败 {issue.get('postTitle', '未知标题')}: {e}")
        except Exception as e:
            print(f"❌ 生成HTML文件时出错: {e}")

        # 生成列表页面
        try:
            self.createPlistHtml()
            print("✅ 生成了列表页面")
        except Exception as e:
            print(f"❌ 生成列表页面失败: {e}")

        # 仅在非本地模式下创建Feed
        if not self.local_mode and self.github_available:
            try:
                self.createFeedXml()
                print("✅ 生成了RSS Feed")
            except Exception as e:
                print(f"⚠️ 生成RSS Feed失败: {e}")

        # 添加缓存控制配置
        try:
            self.addCacheControlHeaders()
            print("✅ 添加了缓存控制配置")
        except Exception as e:
            print(f"⚠️ 添加缓存控制配置失败: {e}")

        print("====== create static html end ======")

    def runOne(self, number_str):
        print("====== start create static html ======")
        
        # 如果是本地开发模式，从blogBase.json加载单篇文章数据
        if self.local_mode:
            print(f"📁 本地开发模式：从blogBase.json加载文章 #{number_str} 数据")
            try:
                with open("blogBase.json", "r", encoding="utf-8") as f:
                    old_config = json.load(f)
                    
                    # 尝试从postListJson或singeListJson中找到文章
                    post_key = "P" + number_str
                    issue = None
                    listJsonName = None
                    
                    if "postListJson" in old_config and post_key in old_config["postListJson"]:
                        issue = old_config["postListJson"][post_key]
                        listJsonName = "postListJson"
                    elif "singeListJson" in old_config and post_key in old_config["singeListJson"]:
                        issue = old_config["singeListJson"][post_key]
                        listJsonName = "singeListJson"
                    
                    if issue and listJsonName:
                        # 确保相应的数据结构存在
                        if listJsonName not in self.blogBase:
                            self.blogBase[listJsonName] = {}
                        self.blogBase[listJsonName][post_key] = issue
                        print(f"✅ 找到文章: {issue.get('postTitle', '未知标题')}")
                        
                        # 生成HTML
                        self.createPostHtml(issue)
                        self.createPlistHtml()
                        print("====== create static html end ======")
                    else:
                        print(f"❌ 未找到文章 #{number_str}")
            except Exception as e:
                print(f"❌ 从blogBase.json加载数据失败: {e}")
        else:
            # 正常模式：从GitHub获取单篇文章
            if not self.github_available or not self.repo:
                print("❌ GitHub API不可用，无法获取文章数据")
                return
            
            try:
                issue = self.repo.get_issue(int(number_str))
                if issue.state == "open":
                    listJsonName = self.addOnePostJson(issue)
                    self.createPostHtml(self.blogBase[listJsonName]["P" + number_str])
                    self.createPlistHtml()
                    self.createFeedXml()
                    print("====== create static html end ======")
                else:
                    print("====== issue is closed ======")
            except Exception as e:
                print(f"❌ 处理单篇文章时出错: {e}")

    def createFileName(self,issue,useLabel=False):
        if useLabel==True:
            fileName=issue.labels[0].name
        else:
            if self.blogBase["urlMode"]=="issue":
                fileName=str(issue.number)
            elif self.blogBase["urlMode"]=="ru_translit": 
                fileName=str(translit(issue.title, language_code='ru', reversed=True)).replace(' ', '-')
            else:
                fileName=Pinyin().get_pinyin(issue.title)
        
        fileName=re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', fileName)
        return fileName

######################################################################################
parser = argparse.ArgumentParser()
parser.add_argument("github_token", help="github_token", nargs='?', default=None)
parser.add_argument("repo_name", help="repo_name", nargs='?', default=None)
parser.add_argument("--issue_number", help="issue_number", default=0, required=False)
parser.add_argument("--local", help="Run in local development mode without GitHub API", action="store_true")
options = parser.parse_args()

# 检查是否启用本地开发模式
if options.local:
    print("🔧 启用本地开发模式")
    # 创建一个模拟的options对象，避免GitHub API调用
    class LocalOptions:
        def __init__(self):
            self.github_token = "local_development"
            self.repo_name = "local_repo"
            self.issue_number = options.issue_number
    
    options = LocalOptions()
    
    # 如果没有blogBase.json文件，提示用户需要先运行完整构建
    if not os.path.exists("blogBase.json"):
        print("❌ 本地开发模式需要先运行完整构建以生成blogBase.json")
        print("请先使用GitHub token运行一次: python Gmeek.py <token> <repo_name>")
        exit(1)
    
    print("✅ 将使用现有的blogBase.json进行本地开发")

blog=GMEEK(options)

if not os.path.exists("blogBase.json"):
    print("blogBase is not exists, runAll")
    blog.runAll()
else:
    if os.path.exists(blog.root_dir+'rss.xml'):
        oldFeedFile=open(blog.root_dir+'rss.xml','r',encoding='utf-8')
        blog.oldFeedString=oldFeedFile.read()
        oldFeedFile.close()
    if options.issue_number=="0" or options.issue_number=="":
        print("issue_number=='0', runAll")
        blog.runAll()
    else:
        f=open("blogBase.json","r")
        print("blogBase is exists and issue_number!=0, runOne")
        oldBlogBase=json.loads(f.read())
        for key, value in oldBlogBase.items():
            blog.blogBase[key] = value
        f.close()
        blog.blogBase["labelColorDict"]=blog.labelColorDict
        blog.runOne(options.issue_number)

listFile=open("blogBase.json","w")
listFile.write(json.dumps(blog.blogBase))
listFile.close()

commentNumSum=0
wordCount=0
print("====== create postList.json file ======")
blog.blogBase["postListJson"]=dict(sorted(blog.blogBase["postListJson"].items(),key=lambda x:x[1]["createdAt"],reverse=True))#使列表由时间排序
for i in blog.blogBase["postListJson"]:
    del blog.blogBase["postListJson"][i]["description"]
    del blog.blogBase["postListJson"][i]["postSourceUrl"]
    del blog.blogBase["postListJson"][i]["htmlDir"]
    del blog.blogBase["postListJson"][i]["createdAt"]
    del blog.blogBase["postListJson"][i]["script"]
    del blog.blogBase["postListJson"][i]["style"]
    del blog.blogBase["postListJson"][i]["top"]
    del blog.blogBase["postListJson"][i]["ogImage"]

    if 'head' in blog.blogBase["postListJson"][i]:
        del blog.blogBase["postListJson"][i]["head"]

    if 'commentNum' in blog.blogBase["postListJson"][i]:
        commentNumSum=commentNumSum+blog.blogBase["postListJson"][i]["commentNum"]
        del blog.blogBase["postListJson"][i]["commentNum"]
    
    # 添加文章内容到postListJson以便全文搜索
    if i != "labelColorDict":
        post_title = blog.blogBase["postListJson"][i]["postTitle"]
        mdFileName = re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', post_title)
        mdFilePath = os.path.join(blog.backup_dir, mdFileName + ".md")
        try:
            with open(mdFilePath, 'r', encoding='UTF-8') as f:
                # 读取文件内容并优化存储
                content = f.read()
                # 对于大型博客，考虑只存储内容摘要以减少JSON大小
                if len(content) > 10000:
                    content = content[:10000] + "..."
                blog.blogBase["postListJson"][i]["content"] = content
        except FileNotFoundError:
            print(f"⚠️ 找不到文章的markdown文件: {post_title}")
            blog.blogBase["postListJson"][i]["content"] = ""
        except Exception as e:
            print(f"❌ 读取文章内容时出错 {post_title}: {e}")
            blog.blogBase["postListJson"][i]["content"] = ""

    if 'wordCount' in blog.blogBase["postListJson"][i]:
        wordCount=wordCount+blog.blogBase["postListJson"][i]["wordCount"]
        del blog.blogBase["postListJson"][i]["wordCount"]

# 添加标签颜色字典
blog.blogBase["postListJson"]["labelColorDict"] = blog.labelColorDict

# 保存postList.json，添加错误处理
post_list_path = os.path.join(blog.root_dir, "postList.json")
try:
    # 使用更高效的JSON序列化选项
    with open(post_list_path, 'w', encoding='utf-8') as docListFile:
        json.dump(blog.blogBase["postListJson"], docListFile, ensure_ascii=False, separators=(',', ':'))
    print(f"✅ 成功保存文章列表到 {post_list_path}")
except Exception as e:
    print(f"❌ 保存文章列表失败: {e}")

# 仅在非计划任务时更新README
if os.environ.get('GITHUB_EVENT_NAME') != 'schedule':
    print("📝 开始更新README文件...")
    try:
        workspace_path = os.environ.get('GITHUB_WORKSPACE', '.')
        
        # 计算统计数据，添加异常处理
        try:
            post_count = len([k for k in blog.blogBase["postListJson"] if k != "labelColorDict"])
        except Exception as e:
            print(f"⚠️ 计算文章数量时出错: {e}")
            post_count = 0
        
        # 提取最近发布的文章，添加进度和错误处理
        recent_posts = []
        try:
            sorted_posts = dict(sorted(
                [(k, v) for k, v in blog.blogBase["postListJson"].items() if k != "labelColorDict"],
                key=lambda x: x[1].get("createdDate", "1970-01-01"), 
                reverse=True
            ))
            
            for i, (key, post) in enumerate(sorted_posts.items()):
                if i < 5:
                    # 确保所有必需字段存在
                    post_url = post.get("postUrl", "")
                    if post_url.startswith('/'):
                        post_url = post_url[1:]  # 移除开头的斜杠
                    
                    recent_posts.append({
                        "title": post.get("postTitle", "无标题"),
                        "date": post.get("createdDate", ""),
                        "url": f"{blog.blogBase.get('homeUrl', '')}/{post_url}"
                    })
            print(f"✅ 成功提取 {len(recent_posts)} 篇最近文章")
        except Exception as e:
            print(f"⚠️ 提取最近文章时出错: {e}")
        
        # 构建README内容
        try:
            readme = f"""# 📝 {blog.blogBase.get('title', '博客')}

## 🌐 项目介绍
**{blog.blogBase.get('title', '博客')}** 是一个基于 GitHub Issues 的静态博客系统，使用 Gmeek 框架自动生成和部署。

## 📊 博客统计
| 统计项 | 数据 | 说明 |
|-------|------|------|
| 📚 文章总数 | [{post_count}]({blog.blogBase.get('homeUrl', '')}/tag.html) | 包含所有公开文章 |
| 💬 评论总数 | {commentNumSum} | 所有文章的评论统计 |
| 📝 总字数 | {wordCount:,} | 所有文章内容字数 |
| 🌍 网站地址 | [{blog.blogBase.get('homeUrl', '')}]({blog.blogBase.get('homeUrl', '')}) | GitHub Pages 部署地址 |
| 🕒 最后更新 | {datetime.datetime.now(blog.TZ).strftime('%Y-%m-%d %H:%M:%S')} | 服务器时区：UTC{blog.blogBase.get('UTC', 0):+d} |

## 🚀 核心特性
- ✅ 基于 GitHub Issues 的内容管理
- ✅ 自动化构建与部署（GitHub Actions）
- ✅ 响应式设计，支持多设备浏览
- ✅ 支持标签分类和文章搜索
- ✅ 提供 RSS 订阅功能
- ✅ 代码高亮与 Markdown 增强

## 📑 最近文章

"""
            
            # 添加最近文章列表
            if recent_posts:
                for i, post in enumerate(recent_posts, 1):
                    readme += f"### {i}. [{post['title']}]({post['url']})\n**发布日期**: {post['date']}\n\n"
            else:
                readme += "暂无文章发布\n\n"
            
            # 添加结尾部分
            readme += """
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

*本 README 由 Gmeek 自动生成和更新*"""
        except Exception as e:
            print(f"❌ 构建README内容时出错: {e}")
            readme = "# 博客\n\nREADME文件生成失败。"
        
        # 写入README文件，添加错误处理
        readme_path = os.path.join(workspace_path, "README.md")
        try:
            with open(readme_path, 'w', encoding='utf-8') as readmeFile:
                readmeFile.write(readme)
            print(f"✅ 成功更新README.md文件: {readme_path}")
        except Exception as e:
            print(f"❌ 写入README文件失败: {e}")
    except Exception as e:
        print(f"❌ README更新过程中出错: {e}")

######################################################################################
