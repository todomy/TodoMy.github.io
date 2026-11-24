# -*- coding: utf-8 -*-
import os
import re
import json
import time
import zlib
import datetime
import shutil
import urllib
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import argparse
import html
from github import Github
from github.GithubException import GithubException
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

# 标签配色：精调表优先，新分类用稳定 hash 从色池确定性取色（浅底深字）
# 同一分类名在任何时候/任何设备都得到同一组颜色；新增分类零维护，撞色时往 preset 加一行即可。
def buildLabelColors(labelNames, theme):
    preset = theme.get('preset', {})
    pool = theme.get('pool', [])
    meta = theme.get('meta', {})
    colorDict = {}
    bgDict = {}
    for name in labelNames:
        if name in preset:
            colorDict[name] = preset[name]['color']
            bgDict[name] = preset[name]['bg']
        elif pool:
            # zlib.crc32 是跨平台、跨进程稳定的 hash，不用 Python 内置 hash()
            idx = zlib.crc32(name.encode('utf-8')) % len(pool)
            colorDict[name] = pool[idx]['color']
            bgDict[name] = pool[idx]['bg']
        else:
            colorDict[name] = meta.get('color', '#6B7280')
            bgDict[name] = meta.get('bg', '#F1F3F5')
    return colorDict, bgDict

class GMEEK():
    def __init__(self,options):
        self.options=options
        
        self.root_dir='docs/'
        self.static_dir='static/'
        self.post_folder='post/'
        self.backup_dir='backup/'
        self.post_dir=self.root_dir+self.post_folder

        # Jinja 环境只建一次，模板带缓存，避免每篇文章重复加载
        self.jinja_env=Environment(loader=FileSystemLoader('templates'))

        # 共享 Session + 重试：全量构建约 500 次 API 调用，遇 429/5xx/网络抖动自动退避
        self.http = requests.Session()
        retry = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
                      allowed_methods=frozenset(['GET', 'POST']), respect_retry_after_header=True)
        self.http.mount('https://', HTTPAdapter(max_retries=retry))

        # per_page=100：GitHub 默认每页 30 条，165 篇要翻 6 页；设为上限后只需 2 页
        user = Github(self.options.github_token, per_page=100)
        self.repo = self.get_repo(user, options.repo_name)
        self.feed = FeedGenerator()
        self.oldFeedString=''

        self.labelColorDict=json.loads('{}')
        for label in self.repo.get_labels():
            self.labelColorDict[label.name]='#'+label.color
        print(self.labelColorDict)
        self.defaultConfig()
        
    def cleanFile(self):
        workspace_path = os.environ.get('GITHUB_WORKSPACE') or os.getcwd()
        if os.path.exists(workspace_path+"/"+self.backup_dir):
            shutil.rmtree(workspace_path+"/"+self.backup_dir)

        if os.path.exists(workspace_path+"/"+self.root_dir):
            shutil.rmtree(workspace_path+"/"+self.root_dir)

        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)
            
        if os.path.exists(self.root_dir):
            shutil.rmtree(self.root_dir)

        os.mkdir(self.backup_dir)
        os.mkdir(self.root_dir)
        os.mkdir(self.post_dir)

        if os.path.exists(self.static_dir):
            for item in os.listdir(self.static_dir):
                src = os.path.join(self.static_dir, item)
                dst = os.path.join(self.root_dir, item)
                if os.path.isfile(src):
                    shutil.copy(src, dst)
                    print(f"Copied {item} to docs")
                elif os.path.isdir(src):
                    shutil.copytree(src, dst)
                    print(f"Copied directory {item} to docs")
        else:
            print("static does not exist")

        self.syncPlugins()

    def syncPlugins(self):
        """把 plugins/ 同步到 docs/plugins/。全量与增量构建均调用，避免增量构建时本地插件缺失或滞后。"""
        os.makedirs(self.root_dir, exist_ok=True)
        plugins_src = 'plugins/'
        plugins_dst = os.path.join(self.root_dir, 'plugins')
        if os.path.exists(plugins_src):
            if os.path.exists(plugins_dst):
                shutil.rmtree(plugins_dst)
            shutil.copytree(plugins_src, plugins_dst)
            print("Copied plugins/ to docs/plugins/")
        else:
            print("plugins does not exist")

    def defaultConfig(self):
        dconfig={"singlePage":[],"startSite":"","filingNum":"","onePageListNum":15,"commentLabelColor":"#006b75","yearColorList":["#bc4c00", "#0969da", "#1f883d", "#A333D0"],"i18n":"CN","themeMode":"manual","dayTheme":"light","nightTheme":"dark","urlMode":"pinyin","script":"","style":"","head":"","indexScript":"","indexStyle":"","bottomText":"","showPostSource":1,"iconList":{},"UTC":+8,"rssSplit":"sentence","rssFullText":0,"exlink":{},"needComment":1,"allHead":""}
        config=json.loads(open('config.json', 'r', encoding='utf-8').read())
        self.blogBase={**dconfig,**config}.copy()
        self.blogBase["postListJson"]=json.loads('{}')
        self.blogBase["singeListJson"]=json.loads('{}')
        # 标签配色：精调表优先 + 新分类稳定 hash 取色，生成深字色/浅底色
        self.labelColorDict, self.labelBgDict = buildLabelColors(
            list(self.labelColorDict.keys()), self.blogBase.get('labelTheme', {}))
        self.blogBase["labelColorDict"]=self.labelColorDict
        self.blogBase["labelBgDict"]=self.labelBgDict
        self.blogBase["metaLabelColor"]=self.blogBase.get('labelTheme', {}).get('meta', {})
        if "displayTitle" not in self.blogBase:
            self.blogBase["displayTitle"]=self.blogBase["title"]

        if "faviconUrl" not in self.blogBase:
            self.blogBase["faviconUrl"]=self.blogBase["avatarUrl"]

        if "ogImage" not in self.blogBase:
            self.blogBase["ogImage"]=self.blogBase["avatarUrl"]

        if "primerCSS" not in self.blogBase:
            self.blogBase["primerCSS"]="<link href='%s/plugins/primer.css' rel='stylesheet' />" % self.blogBase["homeUrl"]

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
        payload = {"text": mdstr, "mode": "gfm"}
        headers = {"Authorization": "token {}".format(self.options.github_token)}
        try:
            response = self.http.post("https://api.github.com/markdown", json=payload, headers=headers, timeout=30)
            response.raise_for_status()  # Raises an exception if status code is not 200
            return response.text
        except requests.RequestException as e:
            raise Exception("markdown2html error: {}".format(e))

    @staticmethod
    def cleanDescription(body, period, max_len=160):
        """从 Markdown 正文生成纯文本摘要：去标记、压空白、限长度，避免污染 meta 属性。"""
        if not body:
            return ''
        text = body
        # 去掉自定义 JSON 配置尾行 ##{...}
        text = re.sub(r'##\{.*?\}\s*$', '', text, flags=re.S)
        # 去掉围栏代码块与行内代码
        text = re.sub(r'```.*?```', '', text, flags=re.S)
        text = re.sub(r'`[^`]*`', '', text)
        # 图片去掉、链接保留可见文字
        text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', '', text)
        text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
        # 去掉 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 去掉 Markdown 标题/引用/列表/分隔线等行首标记
        text = re.sub(r'^\s*(#{1,6}|>|[-*+]\s|\d+\.\s|---|\*\*\*)\s*', '', text, flags=re.M)
        # 去掉强调符号
        text = re.sub(r'(\*\*|__|\*|_|~~)', '', text)
        # 去掉 GitHub alert 标记 [!NOTE] [!tip] 等
        text = re.sub(r'\[![A-Za-z]+\]', '', text)
        # 压平空白
        text = re.sub(r'\s+', ' ', text).strip()
        # 优先取首句，再按长度截断
        if period and period in text:
            first = text.split(period)[0].strip()
            if first:
                text = first + period
        if len(text) > max_len:
            text = text[:max_len].rstrip() + '…'
        return text.replace('"', "'")

    def renderHtml(self,template,blogBase,postListJson,htmlDir,icon):
        template = self.jinja_env.get_template(template)
        output = template.render(blogBase=blogBase,postListJson=postListJson,i18n=self.i18n,IconList=icon)
        f = open(htmlDir, 'w', encoding='UTF-8')
        f.write(output)
        f.close()

    def createPostHtml(self,issue):
        mdFileName=re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', issue["postTitle"])
        f = open(self.backup_dir+mdFileName+".md", 'r', encoding='UTF-8')
        post_body=self.markdown2html(f.read())
        f.close()

        # 图片懒加载：长文不再一次性下载全部图片
        post_body=re.sub(r'<img (?![^>]*loading=)', '<img loading="lazy" decoding="async" ', post_body)

        postBase=self.blogBase.copy()

        if '<math-renderer' in post_body:
            post_body=re.sub(r'<math-renderer.*?>','',post_body)
            post_body=re.sub(r'</math-renderer>','',post_body)
            # 本地化 MathJax：SVG 输出无需外部字体；关闭菜单以切断 SRE 的惰性 CDN 请求
            mathjax_src=self.blogBase["homeUrl"]+"/plugins/mathjax/tex-svg-full.js"
            issue["script"]=issue["script"]+'<script>MathJax = {tex: {inlineMath: [["$", "$"]]}, options: {enableMenu: false}, startup: {typeset: true}};</script><script defer src="'+mathjax_src+'"></script>'
        
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
        postBase["createdDate"]=issue.get("createdDate","")
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

    def getFeedDescription(self,post):
        description=post["description"]
        if self.blogBase.get("rssFullText",0)==1:
            full=self.getPostFullText(post)
            if full!='':
                description=full
        return description

    def getPostFullText(self,post):
        # 从已生成的文章 HTML 中提取正文，避免为 RSS 额外调用 Markdown API
        try:
            f=open(post["htmlDir"],'r',encoding='UTF-8')
            htmlText=f.read()
            f.close()
            marker='<div class="markdown-body" id="postBody">'
            start=htmlText.find(marker)
            if start<0:
                return ''
            start+=len(marker)
            end=htmlText.find('<div style="font-size:small;margin-top:8px;float:right;">',start)
            if end<0:
                return ''
            return htmlText[start:end].strip()
        except Exception:
            return ''

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
            item.description(self.getFeedDescription(self.blogBase["singeListJson"][num]))
            item.link(href=self.blogBase["homeUrl"]+"/"+self.blogBase["singeListJson"][num]["postUrl"])
            item.pubDate(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(self.blogBase["singeListJson"][num]["createdAt"])))

        for num in self.blogBase["postListJson"]:
            item=feed.add_item()
            item.guid(self.blogBase["homeUrl"]+"/"+self.blogBase["postListJson"][num]["postUrl"],permalink=True)
            item.title(self.blogBase["postListJson"][num]["postTitle"])
            item.description(self.getFeedDescription(self.blogBase["postListJson"][num]))
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

    def createSitemapXml(self):
        home=self.blogBase["homeUrl"]
        entries=[(home+"/",None),(home+"/tag.html",None)]
        for num in self.blogBase["singeListJson"]:
            p=self.blogBase["singeListJson"][num]
            entries.append((home+"/"+p["postUrl"],p.get("createdDate")))
        for num in self.blogBase["postListJson"]:
            p=self.blogBase["postListJson"][num]
            entries.append((home+"/"+p["postUrl"],p.get("createdDate")))

        dates=[d for _,d in entries if d]
        latest=max(dates) if dates else ""

        xml='<?xml version="1.0" encoding="UTF-8"?>\r\n'
        xml+='<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\r\n'
        for url,date in entries:
            lastmod=date or latest
            if lastmod:
                xml+='  <url><loc>%s</loc><lastmod>%s</lastmod></url>\r\n' % (url,lastmod)
            else:
                xml+='  <url><loc>%s</loc></url>\r\n' % url
        xml+='</urlset>\r\n'

        sitemapFile=open(self.root_dir+'sitemap.xml',"w",encoding='utf-8')
        sitemapFile.write(xml)
        sitemapFile.close()
        print("====== create sitemap xml ======")

    def uniqueHtmlPath(self, issue, postNum, useLabel=False):
        """生成 HTML 路径；仅当 slug 被其他文章占用时追加 -P编号，保证既有 URL 不变。"""
        base = self.createFileName(issue, useLabel=useLabel)
        prefix = self.root_dir if useLabel else self.post_dir
        candidate = base
        suffix = 0
        while True:
            html_path = prefix + candidate + '.html'
            taken = False
            for coll in ('postListJson', 'singeListJson'):
                for num, post in self.blogBase.get(coll, {}).items():
                    if num != postNum and post.get('htmlDir') == html_path:
                        taken = True
                        break
                if taken:
                    break
            if not taken:
                return html_path
            suffix += 1
            candidate = '{}-P{}-{}'.format(base, issue.number, suffix)

    def purgePrevious(self, postNum, keepHtml, keepList):
        """增量更新前清理旧产物：跨集合残留、改名/换标签后的旧 HTML 与旧备份 md。"""
        for coll in ('postListJson', 'singeListJson'):
            old = self.blogBase.get(coll, {}).get(postNum)
            if not old:
                continue
            old_html = old.get('htmlDir', '')
            # 旧集合或旧路径与新位置不同 -> 删除旧文件
            if old_html and old_html != keepHtml and os.path.exists(old_html):
                try:
                    os.remove(old_html)
                    print("removed stale html: " + old_html)
                except OSError as e:
                    print("warn: cannot remove stale html {}: {}".format(old_html, e))
            old_title = old.get('postTitle', '')
            if old_title:
                old_md = self.backup_dir + re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', old_title) + '.md'
                if os.path.exists(old_md):
                    try:
                        os.remove(old_md)
                        print("removed stale backup: " + old_md)
                    except OSError as e:
                        print("warn: cannot remove stale backup {}: {}".format(old_md, e))
            # 旧集合已不再是目标集合 -> 从旧集合中摘除
            if coll != keepList:
                del self.blogBase[coll][postNum]

    def addOnePostJson(self,issue):
        if len(issue.labels)>=1:
            postNum="P"+str(issue.number)
            is_single = issue.labels[0].name in self.blogBase["singlePage"]
            listJsonName='singeListJson' if is_single else 'postListJson'
            gen_Html = self.uniqueHtmlPath(issue, postNum, useLabel=is_single)
            # 覆盖前先清理该编号的旧产物（全量构建时两个集合为空，此步为空操作）
            self.purgePrevious(postNum, gen_Html, listJsonName)
            self.blogBase[listJsonName][postNum]=json.loads('{}')
            self.blogBase[listJsonName][postNum]["htmlDir"]=gen_Html
            self.blogBase[listJsonName][postNum]["labels"]=[label.name for label in issue.labels]
            self.blogBase[listJsonName][postNum]["postTitle"]=issue.title
            self.blogBase[listJsonName][postNum]["postUrl"]=urllib.parse.quote(gen_Html[len(self.root_dir):])

            self.blogBase[listJsonName][postNum]["postSourceUrl"]="https://github.com/"+options.repo_name+"/issues/"+str(issue.number)
            # 评论数已随 Issue 对象返回，直接读缓存属性，省去每篇一次 get_comments API
            self.blogBase[listJsonName][postNum]["commentNum"]=issue.comments

            if issue.body==None:
                self.blogBase[listJsonName][postNum]["description"]=''
                self.blogBase[listJsonName][postNum]["wordCount"]=0
                self.blogBase[listJsonName][postNum]["content"]=''  # 添加空内容
            else:
                self.blogBase[listJsonName][postNum]["wordCount"]=len(issue.body)
                if self.blogBase["rssSplit"]=="sentence":
                    if self.blogBase["i18n"]=="CN":
                        period="。"
                    else:
                        period="."
                else:
                    period=self.blogBase["rssSplit"]
                self.blogBase[listJsonName][postNum]["description"]=self.cleanDescription(issue.body, period)
                self.blogBase[listJsonName][postNum]["content"]=issue.body  # 保存完整内容
                
            # 置顶改用 label：GitHub 已弱化 Pin issue（无 API、上限 3 篇），
            # 而 labels 本就随 Issue 返回，零额外请求。给 Issue 加「置顶」标签即可置顶。
            self.blogBase[listJsonName][postNum]["top"]=(
                1 if '置顶' in [label.name for label in issue.labels] else 0
            )

            try:
                # 兼容 \n / \r\n 换行，并跳过正文末尾的空行（GitHub 编辑器常在末尾保留换行）
                body_lines=issue.body.replace("\r\n","\n").replace("\r","\n").split("\n")
                nonempty_lines=[line for line in body_lines if line.strip()]
                postConfig=json.loads(nonempty_lines[-1].split("##")[1]) if nonempty_lines else {}
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

        issues=self.repo.get_issues()
        for issue in issues:
            self.addOnePostJson(issue)

        for issue in self.blogBase["postListJson"].values():
            self.createPostHtml(issue)

        for issue in self.blogBase["singeListJson"].values():
            self.createPostHtml(issue)

        self.createPlistHtml()
        self.createFeedXml()
        self.createSitemapXml()
        print("====== create static html end ======")

    def removeOnePost(self,number_str):
        postNum="P"+number_str
        removed=False
        for listJsonName in ("postListJson","singeListJson"):
            if postNum in self.blogBase[listJsonName]:
                oldPost=self.blogBase[listJsonName][postNum]
                htmlDir=oldPost.get("htmlDir","")
                if htmlDir and os.path.exists(htmlDir):
                    os.remove(htmlDir)
                    print("removed html: "+htmlDir)
                mdFileName=re.sub(r'[<>:/\\|?*\"]|[\0-\31]', '-', oldPost["postTitle"])
                mdPath=self.backup_dir+mdFileName+".md"
                if os.path.exists(mdPath):
                    os.remove(mdPath)
                    print("removed backup: "+mdPath)
                del self.blogBase[listJsonName][postNum]
                removed=True
        if removed:
            self.createPlistHtml()
            self.createFeedXml()
            self.createSitemapXml()
        else:
            print("post not found in blogBase: "+postNum)

    def runOne(self,number_str):
        print("====== start create static html ======")
        self.syncPlugins()  # 增量构建也同步本地插件，避免只改 plugins 后不生效
        try:
            issue=self.repo.get_issue(int(number_str))
        except GithubException as e:
            if e.status in (404,410):
                print("====== issue is deleted (HTTP %d), remove post ======" % e.status)
                self.removeOnePost(number_str)
                return
            raise
        if issue.state == "open":
            listJsonName=self.addOnePostJson(issue)
            if listJsonName is None:
                # 无标签视为不发布；若此前发布过则下架，避免 KeyError 与残留
                print("====== issue has no label, unpublish if exists ======")
                self.removeOnePost(number_str)
                return
            self.createPostHtml(self.blogBase[listJsonName]["P"+number_str])
            self.createPlistHtml()
            self.createFeedXml()
            self.createSitemapXml()
            print("====== create static html end ======")
        else:
            print("====== issue is closed, remove post ======")
            self.removeOnePost(number_str)

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
        blog.blogBase["labelBgDict"]=blog.labelBgDict
        blog.blogBase["metaLabelColor"]=blog.blogBase.get('labelTheme', {}).get('meta', {})
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
    # 注意：这里保留content字段，不删除

    if 'head' in blog.blogBase["postListJson"][i]:
        del blog.blogBase["postListJson"][i]["head"]

    if 'commentNum' in blog.blogBase["postListJson"][i]:
        commentNumSum=commentNumSum+blog.blogBase["postListJson"][i]["commentNum"]
        del blog.blogBase["postListJson"][i]["commentNum"]

    if 'wordCount' in blog.blogBase["postListJson"][i]:
        wordCount=wordCount+blog.blogBase["postListJson"][i]["wordCount"]
        del blog.blogBase["postListJson"][i]["wordCount"]

blog.blogBase["postListJson"]["labelColorDict"]=blog.labelColorDict
blog.blogBase["postListJson"]["labelBgDict"]=blog.labelBgDict
blog.blogBase["postListJson"]["metaLabelColor"]=blog.blogBase.get('labelTheme', {}).get('meta', {})

docListFile=open(blog.root_dir+"postList.json","w")
docListFile.write(json.dumps(blog.blogBase["postListJson"]))
docListFile.close()

if os.environ.get('GITHUB_EVENT_NAME')!='schedule':
    print("====== update readme file ======")
    workspace_path = os.environ.get('GITHUB_WORKSPACE') or os.getcwd()
    
    # 计算额外统计信息
    total_pages = len(blog.blogBase["postListJson"]) - 1
    
    # 计算标签数量
    label_count = len(blog.labelColorDict)
    
    # 生成更专业的README
    readme="# %s :link: [%s](%s) \r\n\r\n" % (blog.blogBase["title"], blog.blogBase["title"], blog.blogBase["homeUrl"])
    readme += "🌍 **博客主页**：[%s](%s)\r\n\r\n" % (blog.blogBase["homeUrl"], blog.blogBase["homeUrl"])
    
    # 项目简介部分
    readme += "## 📝 项目简介\r\n"
    readme += "这是一个基于GitHub Issues的静态博客系统，通过Gmeek自动生成和部署。\r\n\r\n"
    
    # 统计信息卡片
    readme += "## 📊 博客统计\r\n"
    readme += "| 统计项目 | 数量 | | 统计项目 | 数据 |\r\n"
    readme += "|---------|------|---|---------|------|\r\n"
    readme += "| 📄 文章总数 | %d | | 🏷️ 标签数量 | %d |\r\n" % (len(blog.blogBase["postListJson"]) - 1, label_count)
    readme += "| 💬 评论总数 | %d | | 🔗 总页面数 | %d |\r\n" % (commentNumSum, total_pages)
    readme += "| 📚 总字数 | %d | | ⏰ 最后更新 | %s |\r\n\r\n" % (wordCount, datetime.datetime.now(blog.TZ).strftime('%Y-%m-%d %H:%M:%S'))
    
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
    
    readmeFile=open(workspace_path+"/README.md","w")
    readmeFile.write(readme)
    readmeFile.close()
######################################################################################
