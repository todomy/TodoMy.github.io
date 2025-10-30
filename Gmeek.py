# -*- coding: utf-8 -*-
import os
import re
import json
import time
import datetime
import shutil
import urllib
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import argparse
import html
import logging
from github import Github, GithubException
from xpinyin import Pinyin
from feedgen.feed import FeedGenerator
from jinja2 import Environment, FileSystemLoader
from transliterate import translit
from collections import OrderedDict
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
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
        # 创建static目录（如果不存在）
        if not os.path.exists(self.static_dir):
            os.makedirs(self.static_dir)
            logging.info(f"已创建static目录: {self.static_dir}")
        self.post_folder='post/'
        self.backup_dir='backup/'
        self.post_dir=self.root_dir+self.post_folder
        self.max_retries = 3
        self.retry_delay = 2  # 秒
        
        # 设置带重试机制的requests会话
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        try:
            # 添加超时和重试机制初始化GitHub连接
            # 使用新版auth参数避免弃用警告
            from github import Auth
            auth = Auth.Token(self.options.github_token)
            user = Github(
                auth=auth,
                timeout=30,
                per_page=100
            )
            self.repo = self.get_repo(user, options.repo_name)
            self.feed = FeedGenerator()
            self.oldFeedString=''

            self.labelColorDict=json.loads('{}')
            for label in self.repo.get_labels():
                self.labelColorDict[label.name]='#'+label.color
            logging.info(f"标签颜色字典: {self.labelColorDict}")
            self.defaultConfig()
        except Exception as e:
            logging.error(f"初始化失败: {str(e)}")
            raise
        
    def cleanFile(self):
        try:
            workspace_path = os.environ.get('GITHUB_WORKSPACE')
            
            # 清理目录
            dirs_to_clean = []
            if workspace_path:
                dirs_to_clean.append(os.path.join(workspace_path, self.backup_dir))
                dirs_to_clean.append(os.path.join(workspace_path, self.root_dir))
            dirs_to_clean.append(self.backup_dir)
            dirs_to_clean.append(self.root_dir)
            
            for dir_path in dirs_to_clean:
                if os.path.exists(dir_path):
                    logging.info(f"删除目录: {dir_path}")
                    shutil.rmtree(dir_path)

            # 创建必要的目录
            for directory in [self.backup_dir, self.root_dir, self.post_dir]:
                if not os.path.exists(directory):
                    logging.info(f"创建目录: {directory}")
                    os.mkdir(directory)

            # 复制静态文件
            if os.path.exists(self.static_dir):
                for item in os.listdir(self.static_dir):
                    src = os.path.join(self.static_dir, item)
                    dst = os.path.join(self.root_dir, item)
                    try:
                        if os.path.isfile(src):
                            shutil.copy(src, dst)
                            logging.info(f"复制文件: {item} 到 docs")
                        elif os.path.isdir(src):
                            shutil.copytree(src, dst)
                            logging.info(f"复制目录: {item} 到 docs")
                    except Exception as e:
                        logging.warning(f"复制 {item} 失败: {str(e)}")
            else:
                logging.warning("static 目录不存在")
        except Exception as e:
            logging.error(f"清理文件失败: {str(e)}")
            raise

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
            self.blogBase["primerCSS"]="<link href='https://cdn.jsdelivr.net/gh/todomy/TodoMy.github.io@main/plugins/primer.css' rel='stylesheet' />"

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
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                repo_instance = user.get_repo(repo)
                logging.info(f"成功连接到仓库: {repo}")
                return repo_instance
            except GithubException as e:
                retry_count += 1
                logging.warning(f"GitHub API错误 (尝试 {retry_count}/{self.max_retries}): {str(e)}")
                if retry_count >= self.max_retries:
                    logging.error(f"连接仓库失败，已达最大重试次数")
                    raise
                time.sleep(self.retry_delay * (retry_count + random.uniform(0.5, 1.5)))  # 指数退避加随机延迟
            except Exception as e:
                logging.error(f"获取仓库失败: {str(e)}")
                raise

    def __init__(self,options):
        self.options=options
        
        self.root_dir='docs/'
        self.static_dir='static/'
        # 创建static目录（如果不存在）
        if not os.path.exists(self.static_dir):
            os.makedirs(self.static_dir)
            logging.info(f"已创建static目录: {self.static_dir}")
        self.post_folder='post/'
        self.backup_dir='backup/'
        self.post_dir=self.root_dir+self.post_folder
        self.max_retries = 3
        self.retry_delay = 2  # 秒
        
        # 设置带重试机制的requests会话
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        # 设置GitHub API请求头
        self.github_headers = {"Authorization": "token {}".format(self.options.github_token)}
        # 初始化Jinja2环境（只创建一次）
        self.jinja_env = None
        
        try:
            # 添加超时和重试机制初始化GitHub连接
            # 使用新版auth参数避免弃用警告
            from github import Auth
            auth = Auth.Token(self.options.github_token)
            user = Github(
                auth=auth,
                timeout=30,
                per_page=100
            )
            self.repo = self.get_repo(user, options.repo_name)
            self.feed = FeedGenerator()
            self.oldFeedString=''

            self.labelColorDict=json.loads('{}')
            for label in self.repo.get_labels():
                self.labelColorDict[label.name]='#'+label.color
            logging.info(f"标签颜色字典: {self.labelColorDict}")
            self.defaultConfig()
        except Exception as e:
            logging.error(f"初始化失败: {str(e)}")
            raise
    
    def markdown2html(self, mdstr):
        try:
            if mdstr is None:
                return ""
            
            payload = {"text": mdstr, "mode": "gfm"}
            # 使用已配置的会话而不是新请求
            response = self.session.post("https://api.github.com/markdown", json=payload, headers=self.github_headers)
            response.raise_for_status()  # Raises an exception if status code is not 200
            return response.text
        except requests.RequestException as e:
            logging.error(f"markdown2html API调用失败: {str(e)}")
            # 返回原始字符串，确保即使转换失败也能显示内容
            return mdstr or ""
        except Exception as e:
            logging.error(f"markdown2html处理失败: {str(e)}")
            return mdstr or ""

    def renderHtml(self,template,blogBase,postListJson,htmlDir,icon):
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(htmlDir), exist_ok=True)
            
            # 复用Jinja2环境，避免重复创建
            if self.jinja_env is None:
                file_loader = FileSystemLoader('templates')
                self.jinja_env = Environment(loader=file_loader)
            
            template_obj = self.jinja_env.get_template(template)
            
            # 准备渲染数据，确保所有必需字段存在
            render_data = {
                "blogBase": blogBase or {},
                "postListJson": postListJson or {},
                "i18n": self.i18n or {},
                "IconList": icon or {}
            }
            
            output = template_obj.render(**render_data)
            
            # 使用with语句安全地写入文件，增加缓冲区大小
            with open(htmlDir, 'w', encoding='UTF-8', buffering=8192) as f:
                f.write(output)
                
            logging.info(f"成功生成HTML文件: {htmlDir}")
        except Exception as e:
            logging.error(f"渲染HTML文件 {htmlDir} 失败: {str(e)}")
            # 尝试创建一个简单的错误页面
            try:
                error_content = f"<html><body><h1>页面生成错误</h1><p>{str(e)}</p></body></html>"
                with open(htmlDir, 'w', encoding='UTF-8') as f:
                    f.write(error_content)
                logging.warning(f"已创建错误页面: {htmlDir}")
            except:
                logging.critical(f"无法创建错误页面: {htmlDir}")

    def createPostHtml(self,issue):
        mdFileName=re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', issue["postTitle"])
        f = open(self.backup_dir+mdFileName+".md", 'r', encoding='UTF-8')
        post_body=self.markdown2html(f.read())
        f.close()

        postBase=self.blogBase.copy()

        if '<math-renderer' in post_body:
            post_body=re.sub(r'<math-renderer.*?>','',post_body)
            post_body=re.sub(r'</math-renderer>','',post_body)
            issue["script"]=issue["script"]+'<script>MathJax = {tex: {inlineMath: [["$", "$"]]}};</script><script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'
        
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
        # 优化排序逻辑，只排序一次
        sorted_posts = sorted(
            self.blogBase["postListJson"].items(),
            key=lambda x: (x[1]["top"], x[1]["createdAt"]),
            reverse=True
        )
        self.blogBase["postListJson"] = dict(sorted_posts)
        
        # 缓存图标，避免重复查找
        icon_cache = {}
        for key in IconBase:
            icon_cache[key] = IconBase[key]
        
        # 优化图标生成
        keys = list(OrderedDict.fromkeys(['sun', 'moon', 'sync', 'search', 'rss', 'upload', 'post'] + self.blogBase["singlePage"]))
        plistIcon = {**{key: icon_cache.get(key, '') for key in keys}, **self.blogBase["iconList"]}
        
        tag_keys = ['sun', 'moon', 'sync', 'home', 'search', 'post']
        tagIcon = {key: icon_cache.get(key, '') for key in tag_keys}

        postNum = len(self.blogBase["postListJson"])
        page_count = (postNum + self.blogBase["onePageListNum"] - 1) // self.blogBase["onePageListNum"]  # 计算总页数
        logging.info(f"总文章数: {postNum}, 每页显示: {self.blogBase['onePageListNum']}, 总页数: {page_count}")
        
        # 优化分页生成逻辑
        for page in range(page_count):
            start = page * self.blogBase["onePageListNum"]
            end = start + self.blogBase["onePageListNum"]
            onePageList = dict(sorted_posts[start:end])
            
            # 设置分页链接
            if page == 0:
                htmlDir = self.root_dir + "index.html"
                self.blogBase["prevUrl"] = "disabled"
            else:
                htmlDir = self.root_dir + ("page%d.html" % (page + 1))
                self.blogBase["prevUrl"] = "/index.html" if page == 1 else "/page%d.html" % page
            
            self.blogBase["nextUrl"] = "disabled" if page == page_count - 1 else "/page%d.html" % (page + 2)
            
            self.renderHtml('plist.html', self.blogBase, onePageList, htmlDir, plistIcon)
            logging.info(f"已生成分页页面: {htmlDir}")
        
        # 生成标签页，使用第一页的数据
        first_page_list = dict(sorted_posts[:self.blogBase["onePageListNum"]])
        self.renderHtml('tag.html', self.blogBase, first_page_list, self.root_dir + "tag.html", tagIcon)
        logging.info("已生成标签页面: tag.html")

    def createFeedXml(self):
        try:
            logging.info("====== 开始生成RSS XML ======")
            
            # 确保数据结构存在
            if "postListJson" not in self.blogBase:
                self.blogBase["postListJson"] = {}
            if "singeListJson" not in self.blogBase:
                self.blogBase["singeListJson"] = {}
            
            # 排序文章列表
            self.blogBase["postListJson"] = dict(sorted(
                self.blogBase["postListJson"].items(),
                key=lambda x: x[1].get("createdAt", 0),
                reverse=False
            ))
            
            # 初始化FeedGenerator
            feed = FeedGenerator()
            
            # 安全地设置Feed属性，提供默认值
            feed.title(self.blogBase.get("title", "Blog Title"))
            feed.description(self.blogBase.get("subTitle", "Blog Description"))
            feed.link(href=self.blogBase.get("homeUrl", "https://example.com"))
            
            # 尝试设置图片，出错时记录警告但继续
            try:
                if self.blogBase.get("avatarUrl"):
                    feed.image(
                        url=self.blogBase["avatarUrl"],
                        title="avatar",
                        link=self.blogBase.get("homeUrl", "https://example.com")
                    )
            except Exception as e:
                logging.warning(f"设置RSS图片失败: {str(e)}")
            
            feed.copyright(self.blogBase.get("title", "Blog"))
            feed.managingEditor(self.blogBase.get("title", "Blog"))
            feed.webMaster(self.blogBase.get("title", "Blog"))
            feed.ttl("60")
            
            # 添加单页内容到RSS
            rss_item_count = 0
            for list_type in ["singeListJson", "postListJson"]:
                if list_type in self.blogBase:
                    for num, post_data in self.blogBase[list_type].items():
                        try:
                            item = feed.add_item()
                            
                            # 安全地获取并设置属性
                            post_url = post_data.get("postUrl", "")
                            home_url = self.blogBase.get("homeUrl", "")
                            full_url = f"{home_url}/{post_url}" if post_url else home_url
                            
                            item.guid(full_url, permalink=True)
                            item.title(post_data.get("postTitle", f"Post {num}"))
                            item.description(post_data.get("description", "No description available"))
                            item.link(href=full_url)
                            
                            # 安全地设置发布日期
                            try:
                                if "createdAt" in post_data:
                                    pub_date = time.strftime(
                                        "%a, %d %b %Y %H:%M:%S +0000",
                                        time.gmtime(post_data["createdAt"])
                                    )
                                    item.pubDate(pub_date)
                            except Exception as e:
                                logging.warning(f"设置发布日期失败 for {num}: {str(e)}")
                                # 使用当前时间作为备选
                                current_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
                                item.pubDate(current_time)
                            
                            rss_item_count += 1
                        except Exception as e:
                            logging.error(f"添加RSS项目 {num} 失败: {str(e)}")
                            # 继续处理下一个项目
                            continue
            
            # 检查是否需要更新RSS文件
            need_update = True
            if self.oldFeedString and rss_item_count > 0:
                try:
                    temp_rss_path = os.path.join(self.root_dir, 'new.xml')
                    feed.rss_file(temp_rss_path)
                    
                    with open(temp_rss_path, 'r', encoding='utf-8') as newFeed:
                        new = newFeed.read()
                    
                    # 移除lastBuildDate标签以便比较
                    new = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', '', new, flags=re.DOTALL)
                    old = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', '', self.oldFeedString, flags=re.DOTALL)
                    
                    # 清理临时文件
                    os.remove(temp_rss_path)
                    
                    if new == old:
                        logging.info("RSS内容无变化，跳过更新")
                        need_update = False
                        # 使用旧的RSS内容
                        rss_output_path = os.path.join(self.root_dir, 'rss.xml')
                        with open(rss_output_path, "w", encoding='utf-8') as feedFile:
                            feedFile.write(self.oldFeedString)
                except Exception as e:
                    logging.error(f"比较RSS内容时出错: {str(e)}")
                    # 出错时仍然更新RSS
                    need_update = True
            
            # 如果需要更新，则生成新的RSS文件
            if need_update and rss_item_count > 0:
                rss_output_path = os.path.join(self.root_dir, 'rss.xml')
                feed.rss_file(rss_output_path)
                logging.info(f"成功生成RSS XML，共包含 {rss_item_count} 个项目")
            elif rss_item_count == 0:
                logging.warning("没有内容可添加到RSS")
                
        except Exception as e:
            logging.error(f"创建RSS XML失败: {str(e)}")
            # 尝试创建一个基本的RSS文件作为后备
            try:
                basic_rss = f'''
                <?xml version="1.0" encoding="UTF-8"?>
                <rss version="2.0">
                    <channel>
                        <title>{self.blogBase.get("title", "Blog")}</title>
                        <link>{self.blogBase.get("homeUrl", "")}</link>
                        <description>RSS generation failed: {str(e)}</description>
                        <lastBuildDate>{time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())}</lastBuildDate>
                    </channel>
                </rss>
                '''
                rss_output_path = os.path.join(self.root_dir, 'rss.xml')
                with open(rss_output_path, "w", encoding='utf-8') as f:
                    f.write(basic_rss)
                logging.warning(f"已创建基本RSS文件作为后备")
            except:
                logging.critical("无法创建后备RSS文件")

    def addOnePostJson(self,issue):
        if len(issue.labels)>=1:
            # 优化标签判断逻辑
            first_label = issue.labels[0].name
            if first_label in self.blogBase["singlePage"]:
                listJsonName='singeListJson'
                htmlFile='{}.html'.format(self.createFileName(issue,useLabel=True))
                gen_Html = self.root_dir+htmlFile
            else:
                listJsonName='postListJson'
                htmlFile='{}.html'.format(self.createFileName(issue))
                gen_Html = self.post_dir+htmlFile

            postNum="P"+str(issue.number)
            # 使用字典字面量而非json.loads，提高性能
            self.blogBase[listJsonName][postNum] = {}
            post_data = self.blogBase[listJsonName][postNum]
            
            # 批量赋值，减少重复键查找
            post_data["htmlDir"] = gen_Html
            post_data["labels"] = [label.name for label in issue.labels]
            post_data["postTitle"] = issue.title
            post_data["postUrl"] = urllib.parse.quote(gen_Html[len(self.root_dir):])
            post_data["postSourceUrl"] = "https://github.com/"+options.repo_name+"/issues/"+str(issue.number)
            
            # 缓存评论数，避免重复API调用
            comment_count = issue.get_comments().totalCount
            post_data["commentNum"] = comment_count

            # 优化文章内容处理
            issue_body = issue.body or ''
            post_data["content"] = issue_body  # 保存文章内容
            
            if not issue_body:
                post_data["description"] = ''
                post_data["wordCount"] = 0
            else:
                post_data["wordCount"] = len(issue_body)
                # 优化分隔符逻辑
                if self.blogBase["rssSplit"] == "sentence":
                    period = "。" if self.blogBase["i18n"] == "CN" else "."
                else:
                    period = self.blogBase["rssSplit"]
                
                # 安全地获取第一段
                description_parts = issue_body.split(period)
                if description_parts:
                    post_data["description"] = description_parts[0].replace('"', "'") + period
                else:
                    post_data["description"] = ""
                
            # 优化置顶状态检查
            post_data["top"] = 0
            # 减少不必要的API调用，仅在需要时获取事件
            if hasattr(issue, '_rawData') and 'events_url' in issue._rawData:
                for event in issue.get_events():
                    if event.event == "pinned":
                        post_data["top"] = 1
                        break  # 找到置顶事件后立即退出循环
                    elif event.event == "unpinned":
                        post_data["top"] = 0

            # 尝试解析自定义配置
            postConfig = {}
            if issue_body and "##" in issue_body:
                try:
                    last_line = issue_body.split("\r\n")[-1]
                    if "##" in last_line:
                        postConfig = json.loads(last_line.split("##")[1])
                        print("Has Custom JSON parameters")
                        print(postConfig)
                except Exception as e:
                    # 静默处理错误，使用默认配置
                    pass

            # 处理时间戳
            if "timestamp" in postConfig:
                post_data["createdAt"] = postConfig["timestamp"]
            else:
                post_data["createdAt"] = int(time.mktime(issue.created_at.timetuple()))
            
            # 处理自定义样式和脚本
            post_data["style"] = self.blogBase["style"] + (str(postConfig.get("style", "")) if "style" in postConfig else "")
            post_data["script"] = self.blogBase["script"] + (str(postConfig.get("script", "")) if "script" in postConfig else "")
            post_data["head"] = self.blogBase["head"] + (str(postConfig.get("head", "")) if "head" in postConfig else "")
            post_data["ogImage"] = postConfig.get("ogImage", self.blogBase["ogImage"])

            # 处理日期相关信息
            thisTime = datetime.datetime.fromtimestamp(post_data["createdAt"])
            thisTime = thisTime.astimezone(self.TZ)
            thisYear = thisTime.year
            post_data["createdDate"] = thisTime.strftime("%Y-%m-%d")
            post_data["dateLabelColor"] = self.blogBase["yearColorList"][int(thisYear) % len(self.blogBase["yearColorList"])]

            # 写入备份文件
            mdFileName = re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', issue.title)
            with open(self.backup_dir + mdFileName + ".md", 'w', encoding='UTF-8') as f:
                f.write(issue_body)
                
            return listJsonName

    def runAll(self):
        logging.info("====== 开始创建静态HTML ======")
        try:
            # 安全处理：先备份现有备份文件到临时目录，防止API失败导致备份丢失
            temp_backup_dir = self.backup_dir + "temp_backup_" + str(int(time.time())) + "/"
            if os.path.exists(self.backup_dir) and os.listdir(self.backup_dir):
                os.makedirs(temp_backup_dir)
                logging.info(f"临时备份现有文件到: {temp_backup_dir}")
                for file in os.listdir(self.backup_dir):
                    if file.endswith(".md"):
                        shutil.copy(self.backup_dir + file, temp_backup_dir + file)
            
            # 清理文件和目录
            self.cleanFile()
            
            # 获取所有issues，添加分页支持以处理大量issues
            issue_count = 0
            max_issues = 1000  # 设置一个合理的上限，防止处理过多issues
            
            # 预加载所有open状态的issues，减少API调用次数
            open_issues = list(self.repo.get_issues(state="open"))
            issue_count = len(open_issues)
            
            logging.info(f"准备处理 {issue_count} 个issues")
            
            # 限制处理数量
            if issue_count > max_issues:
                logging.warning(f"已达到最大处理数量 {max_issues}，跳过剩余issues")
                open_issues = open_issues[:max_issues]
                issue_count = max_issues
            
            # 批量处理issues
            for i, issue in enumerate(open_issues):
                try:
                    self.addOnePostJson(issue)
                    # 每处理10个issue打印一次进度，减少日志输出
                    if (i + 1) % 10 == 0 or i + 1 == issue_count:
                        logging.info(f"已处理 {i + 1}/{issue_count} 个issues")
                except Exception as e:
                    logging.error(f"处理issue #{issue.number} 失败: {str(e)}")
                    # 继续处理下一个issue
                    continue
            
            # 优化HTML生成顺序，先生成文章，再生成列表页
            total_posts = 0
            for issue_type in ["postListJson", "singeListJson"]:
                if issue_type in self.blogBase:
                    posts = list(self.blogBase[issue_type].items())
                    post_count = len(posts)
                    total_posts += post_count
                    
                    if post_count > 0:
                        logging.info(f"开始生成 {issue_type} 的 {post_count} 个HTML页面")
                        
                        for i, (issue_id, issue) in enumerate(posts):
                            try:
                                self.createPostHtml(issue)
                                # 每处理10个post打印一次进度
                                if (i + 1) % 10 == 0 or i + 1 == post_count:
                                    logging.info(f"已生成 {i + 1}/{post_count} 个HTML页面")
                            except Exception as e:
                                logging.error(f"生成文章 {issue_id} HTML 失败: {str(e)}")
                                # 继续处理下一篇文章
                                continue
            
            logging.info(f"总共生成了 {total_posts} 个文章HTML页面")
            
            # 生成列表页面和RSS
            logging.info("开始生成列表页面")
            self.createPlistHtml()
            
            logging.info("开始生成RSS文件")
            self.createFeedXml()
            
            # 如果临时备份存在，删除它
            if os.path.exists(temp_backup_dir):
                shutil.rmtree(temp_backup_dir)
                
            logging.info("====== 创建静态HTML完成 ======")
            logging.info(f"总共处理了 {issue_count} 个issues")
        except Exception as e:
            logging.error(f"runAll 执行失败: {str(e)}")
            # 尝试恢复临时备份
            if os.path.exists(temp_backup_dir) and os.listdir(temp_backup_dir):
                logging.info("尝试恢复之前的备份文件...")
                # 确保备份目录存在
                if not os.path.exists(self.backup_dir):
                    os.makedirs(self.backup_dir)
                # 恢复备份文件
                for file in os.listdir(temp_backup_dir):
                    if file.endswith(".md"):
                        shutil.copy(temp_backup_dir + file, self.backup_dir + file)
                shutil.rmtree(temp_backup_dir)
                logging.info("备份文件已恢复")
            raise

    def runOne(self,number_str):
        print("====== start create static html ======")
        issue=self.repo.get_issue(int(number_str))
        if issue.state == "open":
            listJsonName=self.addOnePostJson(issue)
            self.createPostHtml(self.blogBase[listJsonName]["P"+number_str])
            self.createPlistHtml()
            self.createFeedXml()
            print("====== create static html end ======")
        else:
            print("====== issue is closed ======")

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
parser.add_argument("github_token", help="github_token")
parser.add_argument("repo_name", help="repo_name")
parser.add_argument("--issue_number", help="issue_number", default=0, required=False)
options = parser.parse_args()

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

    if 'wordCount' in blog.blogBase["postListJson"][i]:
        wordCount=wordCount+blog.blogBase["postListJson"][i]["wordCount"]
        del blog.blogBase["postListJson"][i]["wordCount"]

blog.blogBase["postListJson"]["labelColorDict"]=blog.labelColorDict

docListFile=open(blog.root_dir+"postList.json","w")
docListFile.write(json.dumps(blog.blogBase["postListJson"]))
docListFile.close()

if os.environ.get('GITHUB_EVENT_NAME')!='schedule':
    print("====== update readme file ======")
    workspace_path = os.environ.get('GITHUB_WORKSPACE')
    readme="# %s :link: %s \r\n" % (blog.blogBase["title"],blog.blogBase["homeUrl"])
    readme=readme+"\r\n## 关于这个博客\r\n"
    readme=readme+"这是一个基于 GitHub Issues 的个人知识库和思考记录平台。\r\n"
    readme=readme+"主要分享读书笔记、生活思考、技术探索和投资见解等内容。\r\n"
    readme=readme+"通过 Gmeek 工具自动将 GitHub Issues 转换为静态博客页面。\r\n\r\n"
    readme=readme+"### :page_facing_up: [%d](%s/tag.html) \r\n" % (len(blog.blogBase["postListJson"])-1,blog.blogBase["homeUrl"])
    readme=readme+"### :speech_balloon: %d \r\n" % commentNumSum
    readme=readme+"### :hibiscus: %d \r\n" % wordCount
    readme=readme+"### :alarm_clock: %s \r\n" % datetime.datetime.now(blog.TZ).strftime('%Y-%m-%d %H:%M:%S')
    readmeFile=open(workspace_path+"/README.md","w")
    readmeFile.write(readme)
    readmeFile.close()
######################################################################################
