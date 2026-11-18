#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TodoMy-Next 博客生成器 —— 纯 Python 标准库实现，零 pip 依赖。

设计目标：
  1. 长期稳定：只用标准库，不因第三方包升级/EOL 而失效。
  2. 独立自持：所有静态资源本地化；评论/访问量自托管；不依赖任何 CDN。
  3. 能力完整：继承原 Gmeek 独立版的全部能力，并新增 Markdown 图形构建时渲染。

数据流：
  GitHub Issues(内容后端) -> 本生成器 -> docs/(静态站点) -> GitHub Pages

构建路径：
  runAll  : 全量重建（首次、手动 Run workflow、每周体检触发）
  runOne  : 单篇增量（发布/编辑 Issue 触发）

用法：
  python generator/build.py <github_token> <owner/repo> [--issue_number N] [--workspace DIR]
"""

import os
import re
import sys
import json
import html
import time
import shutil
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# 配置默认值（对应原版 dconfig，全部能力键保留）
# ---------------------------------------------------------------------------
DCONFIG = {
    "title": "TodoMy",
    "subTitle": "",
    "displayTitle": "",
    "avatarUrl": "",
    "faviconUrl": "",
    "ogImage": "",
    "homeUrl": "",
    "startSite": "",
    "filingNum": "",
    "onePageListNum": 15,
    "commentLabelColor": "#006b75",
    "yearColorList": ["#bc4c00", "#0969da", "#1f883d", "#A333D0"],
    "i18n": "CN",
    "themeMode": "manual",          # manual | fix | auto
    "dayTheme": "light",
    "nightTheme": "dark",
    "urlMode": "pinyin",            # pinyin | issue | slug
    "script": "",
    "style": "",
    "head": "",
    "indexScript": "",
    "indexStyle": "",
    "bottomText": "",
    "showPostSource": 1,
    "iconList": {},
    "UTC": 8,
    "rssSplit": "sentence",
    "exlink": {},
    "needComment": 1,
    "allHead": "",
    "singlePage": [],               # 作为单页的 label 名，如 ["about","links"]
    "enableDiagrams": 1,            # 新增：是否启用 Mermaid 构建时渲染
    "diagramTheme": "default",      # 新增：mermaid 主题
}

# ---------------------------------------------------------------------------
# i18n 三语（对应原版 i18n / i18nCN / i18nRU）
# ---------------------------------------------------------------------------
I18N = {
    "EN": {"Search": "Search", "switchTheme": "Switch theme", "home": "Home",
           "comments": "Comments", "run": "Site running ", "days": " days",
           "Previous": "Previous", "Next": "Next", "toc": "Contents",
           "notFind": "Not Find", "loadMore": "Load more articles", "viewMore": "View more results"},
    "CN": {"Search": "搜索", "switchTheme": "切换主题", "home": "首页",
           "comments": "评论", "run": "网站运行", "days": "天",
           "Previous": "上一页", "Next": "下一页", "toc": "文章目录",
           "notFind": "未找到", "loadMore": "加载更多文章", "viewMore": "查看更多结果"},
    "RU": {"Search": "Поиск", "switchTheme": "Сменить тему", "home": "Главная",
           "comments": "Комментарии", "run": "Сайт работает ", "days": " дней",
           "Previous": "Назад", "Next": "Вперёд", "toc": "Оглавление",
           "notFind": "Не найдено", "loadMore": "Загрузить ещё", "viewMore": "Показать ещё"},
}

# ---------------------------------------------------------------------------
# Octicon SVG path（本地内联，替代原版 IconBase）
# ---------------------------------------------------------------------------
ICON_PATHS = {
    "post": "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z",
    "link": "M7.775 3.275a.75.75 0 0 0 1.06 1.06l1.25-1.25a2 2 0 1 1 2.83 2.83l-2.5 2.5a2 2 0 0 1-2.83 0 .75.75 0 0 0-1.06 1.06 3.5 3.5 0 0 0 4.95 0l2.5-2.5a3.5 3.5 0 0 0-4.95-4.95l-1.25 1.25Zm-4.69 9.64a2 2 0 0 1 0-2.83l2.5-2.5a2 2 0 0 1 2.83 0 .75.75 0 0 0 1.06-1.06 3.5 3.5 0 0 0-4.95 0l-2.5 2.5a3.5 3.5 0 0 0 4.95 4.95l1.25-1.25a.75.75 0 0 0-1.06-1.06l-1.25 1.25a2 2 0 0 1-2.83 0Z",
    "about": "M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8Zm8-6.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13ZM6.5 7.75A.75.75 0 0 1 7.25 7h1a.75.75 0 0 1 .75.75v2.75h.25a.75.75 0 0 1 0 1.5h-2a.75.75 0 0 1 0-1.5h.25v-2h-.25a.75.75 0 0 1-.75-.75ZM8 6a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z",
    "sun": "M8 12a4 4 0 1 1 0-8 4 4 0 0 1 0 8Zm0-1.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Zm5.657-8.157a.75.75 0 0 1 0 1.061l-1.061 1.06a.75.75 0 1 1-1.06-1.06l1.06-1.06a.75.75 0 0 1 1.06 0Zm-9.097 0a.75.75 0 0 1 1.06 0l1.06 1.06a.75.75 0 1 1-1.06 1.061l-1.06-1.06a.75.75 0 0 1 0-1.061ZM8 0a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0V.75A.75.75 0 0 1 8 0Zm0 13.5a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0v-1.5A.75.75 0 0 1 8 13.5ZM.75 7.25h1.5a.75.75 0 0 1 0 1.5H.75a.75.75 0 0 1 0-1.5Zm13.5 0h1.5a.75.75 0 0 1 0 1.5h-1.5a.75.75 0 0 1 0-1.5Z",
    "moon": "M9.598 1.591a.749.749 0 0 1 .785-.175 7.001 7.001 0 1 1-8.967 8.967.75.75 0 0 1 .961-.96 5.5 5.5 0 0 0 7.046-7.046.75.75 0 0 1 .175-.786Z",
    "search": "M10.68 11.74a6 6 0 0 1-7.922-8.982 6 6 0 0 1 8.982 7.922l3.04 3.04a.749.749 0 0 1-.326 1.275.749.749 0 0 1-.734-.215ZM11.5 7a4.499 4.499 0 1 0-8.997 0A4.499 4.499 0 0 0 11.5 7Z",
    "rss": "M2.002 2.725a.75.75 0 0 1 .797-.699C8.79 2.42 13.58 7.21 13.974 13.201a.75.75 0 0 1-1.497.098 10.502 10.502 0 0 0-9.776-9.776.75.75 0 0 1-.699-.798ZM2 11.5a2.5 2.5 0 1 1 5 0 2.5 2.5 0 0 1-5 0Z",
    "upload": "M7.25 1.75a.75.75 0 0 1 1.5 0v6.19l2.72-2.72a.749.749 0 0 1 1.275.326.749.749 0 0 1-.215.734l-4 4a.75.75 0 0 1-1.06 0l-4-4a.749.749 0 0 1 .326-1.275.749.749 0 0 1 .734.215l2.72 2.72V1.75ZM2.75 12.5a.75.75 0 0 1 .75.75v.75h9v-.75a.75.75 0 0 1 1.5 0v1.5a.75.75 0 0 1-.75.75h-10.5a.75.75 0 0 1-.75-.75v-1.5a.75.75 0 0 1 .75-.75Z",
    "github": "M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8Z",
    "home": "M6.906.664a1.749 1.749 0 0 1 2.187 0l5.25 4.2c.415.332.657.835.657 1.367v7.019A1.75 1.75 0 0 1 13.25 15h-3.5a.75.75 0 0 1-.75-.75V9H7v5.25a.75.75 0 0 1-.75.75h-3.5A1.75 1.75 0 0 1 1 13.25V6.23c0-.531.242-1.034.657-1.366l5.25-4.2Z",
    "sync": "M8 2.5a5.5 5.5 0 0 1 4.72 2.732.75.75 0 0 1-1.298.75 4 4 0 1 0 .078 4.018.75.75 0 0 1 1.31.724A5.5 5.5 0 1 1 8 2.5ZM13.25 8a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 0 1.5H14a.75.75 0 0 1-.75-.75ZM1 8a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 0 1.5H1.75A.75.75 0 0 1 1 8Z",
    "copy": "M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 0 1 0 1.5h-1.5a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-1.5a.75.75 0 0 1 1.5 0v1.5A1.75 1.75 0 0 1 9.25 16h-7.5A1.75 1.75 0 0 1 0 14.25Z",
    "check": "M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L1.72 8.78a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z",
}


class Pinyin:
    """内置拼音表，纯标准库实现汉字转拼音（URL 用，无声调）。"""
    def __init__(self, data_path):
        self.table = {}
        try:
            with open(data_path, encoding="utf-8") as f:
                self.table = json.load(f)
        except Exception:
            pass

    def convert(self, text, sep=""):
        out = []
        for ch in text:
            if ch in self.table:
                out.append(self.table[ch])
            elif ch.isalnum():
                out.append(ch.lower())
            elif out and out[-1] != sep:
                out.append(sep)
        s = sep.join(x for x in out if x)
        return re.sub(r"-{2,}", "-", s).strip("-")


class GitHubAPI:
    """极简 GitHub REST 客户端（标准库 urllib），替代 PyGithub + requests。"""
    def __init__(self, token, repo):
        self.token = token
        self.repo = repo            # owner/name
        self.base = "https://api.github.com"

    def _request(self, method, path, body=None, raw=False):
        url = path if path.startswith("http") else self.base + path
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "TodoMy-Next-Builder",
        }
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        if data:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                content = resp.read()
                return content.decode("utf-8") if raw else json.loads(content or b"null")
        except urllib.error.HTTPError as e:
            raise RuntimeError("GitHub API %s %s -> HTTP %s: %s" %
                               (method, path, e.code, e.read().decode("utf-8", "replace")[:200]))

    def get(self, path, raw=False):
        return self._request("GET", path, raw=raw)

    def get_all(self, path):
        """自动翻页拉取列表。"""
        items = []
        page = 1
        while True:
            batch = self.get("%s?per_page=100&page=%d" % (path, page))
            if not isinstance(batch, list) or not batch:
                break
            items.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return items

    def markdown(self, text):
        """GitHub 官方 Markdown 渲染（gfm），保持与原版一致。"""
        return self._request("POST", "/markdown",
                             {"text": text, "mode": "gfm"}, raw=True)

    def get_labels(self):
        return self.get_all("/repos/%s/labels" % self.repo)

    def get_issues(self):
        # state=all + 过滤 PR，比原版更严谨（原版 get_issues() 会混入 PR）
        issues = self.get_all("/repos/%s/issues?state=all" % self.repo)
        return [i for i in issues if "pull_request" not in i]

    def get_issue(self, number):
        return self.get("/repos/%s/issues/%s" % (self.repo, number))

    def get_comments_count(self, number):
        issue = self.get("/repos/%s/issues/%s" % (self.repo, number))
        return issue.get("comments", 0)

    def get_events(self, number):
        return self.get_all("/repos/%s/issues/%s/events" % (self.repo, number))


# ---------------------------------------------------------------------------
# 图形渲染：构建时把 mermaid 代码块替换为内联 SVG（前端零依赖）
# ---------------------------------------------------------------------------
class DiagramRenderer:
    """
    在 Markdown 渲染成 HTML 之后，把 mermaid 代码块替换为内联 SVG。
    依赖构建环境的 mmdc（Node + runner 自带 Chrome），产物是自包含 SVG。
    每次构建渲染所有图（约 N 篇 × 图数），结果写回 HTML，前端不再运行 JS。

    生成失败时优雅降级：保留原始代码块，不让整篇构建失败。
    """
    FENCE_RE = re.compile(
        r'<(?:div|pre)[^>]*>.*?</(?:div|pre)>', re.S
    )

    def __init__(self, enabled=True, mmdc_bin="mmdc", theme="default", tmp_dir=None):
        self.enabled = enabled
        self.mmdc_bin = mmdc_bin
        self.theme = theme
        self.tmp_dir = tmp_dir or os.path.join(os.path.dirname(__file__), ".diagram-tmp")
        self._cache = {}
        if self.enabled:
            os.makedirs(self.tmp_dir, exist_ok=True)

    def _extract_blocks(self, rendered_html):
        """
        GitHub Markdown API 对 ```mermaid 的输出形如：
          <div class="highlight highlight-source-mermaid"><pre>...代码(含span标签)...</pre></div>
        需要去掉内部 span 标签还原源码，并定位每个块的起止位置。
        返回 [(start, end, mermaid_source), ...]
        """
        blocks = []
        for m in re.finditer(r'<div class="highlight highlight-source-mermaid"><pre>(.*?)</pre></div>',
                             rendered_html, re.S):
            inner = m.group(1)
            # 还原被语法高亮拆分的 HTML 实体与 span
            source = re.sub(r'<[^>]+>', '', inner)
            source = html.unescape(source).strip()
            if source:
                blocks.append((m.start(), m.end(), source))
        return blocks

    def render_one(self, source):
        """调用 mmdc 把一段 mermaid 源码渲染为内联 SVG 字符串。带缓存。"""
        key = hash(source)
        if key in self._cache:
            return self._cache[key]
        import subprocess
        import tempfile
        mmd = os.path.join(self.tmp_dir, "d_%s.mmd" % key)
        svg = os.path.join(self.tmp_dir, "d_%s.svg" % key)
        with open(mmd, "w", encoding="utf-8") as f:
            f.write(source)
        cmd = [self.mmdc_bin, "-i", mmd, "-o", svg, "-b", "transparent",
               "-p", os.path.join(self.tmp_dir, "puppeteer.json")]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            if proc.returncode != 0 or not os.path.exists(svg):
                raise RuntimeError((proc.stderr or proc.stdout)[:300])
            with open(svg, encoding="utf-8") as f:
                svg_text = f.read()
            # 内联 SVG：去掉 XML 声明，加 class 便于样式控制
            svg_text = re.sub(r'^<\?xml[^>]*\?>', '', svg_text).strip()
            svg_text = svg_text.replace('<svg ', '<svg class="mermaid-svg" ', 1)
            self._cache[key] = svg_text
            return svg_text
        except Exception as e:
            print("  [diagram] 渲染失败，保留原代码块: %s" % str(e)[:120])
            return None
        finally:
            for p in (mmd, svg):
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

    def process(self, rendered_html):
        """把 HTML 里所有 mermaid 块替换为 SVG 图。"""
        if not self.enabled:
            return rendered_html
        blocks = self._extract_blocks(rendered_html)
        if not blocks:
            return rendered_html
        print("  [diagram] 检测到 %d 个 Mermaid 图，开始构建时渲染..." % len(blocks))
        out = []
        last = 0
        rendered = 0
        for start, end, source in blocks:
            svg = self.render_one(source)
            if not svg:
                continue
            out.append(rendered_html[last:start])
            out.append('<div class="mermaid-figure">%s</div>' % svg)
            last = end
            rendered += 1
        out.append(rendered_html[last:])
        print("  [diagram] 成功内联 %d 个 SVG" % rendered)
        return "".join(out)

    def ensure_puppeteer_config(self):
        """写好 mmdc 的 puppeteer 配置：优先用 runner 自带 chrome，零下载。"""
        cfg = os.path.join(self.tmp_dir, "puppeteer.json")
        chrome = os.environ.get("CHROME_PATH") or "/usr/bin/google-chrome"
        if not os.path.exists(chrome):
            for c in ("/usr/bin/chromium", "/usr/bin/chromium-browser"):
                if os.path.exists(c):
                    chrome = c
                    break
        data = {"args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]}
        if os.path.exists(chrome):
            data["executablePath"] = chrome
        with open(cfg, "w") as f:
            json.dump(data, f)
        return cfg


# ---------------------------------------------------------------------------
# 极简模板渲染器：只依赖 Jinja2 风格的子集，用纯 Python 实现
#   支持 {{ var }} / {{ var['k'] }} / {{ x|e }} / {% if %} / {% for %} / {% include %}
# ---------------------------------------------------------------------------
class MiniTemplate:
    def __init__(self, template_dir):
        self.dir = template_dir

    def _eval(self, expr, ctx):
        expr = expr.strip()
        # 过滤器
        filt = None
        if "|" in expr:
            expr, filt = expr.split("|", 1)
            filt = filt.strip()
        # 变量/字典访问，如 blogBase['title'] 或 postListJson[num]['postUrl']
        def resolve(e):
            e = e.strip()
            # 字符串字面量
            if (e.startswith("'") and e.endswith("'")) or (e.startswith('"') and e.endswith('"')):
                return e[1:-1]
            # 变量[键] 链
            m = re.match(r'^([A-Za-z_]\w*)(.*)$', e)
            if not m:
                return ""
            val = ctx.get(m.group(1), "")
            rest = m.group(2)
            for keyexpr in re.findall(r"\[([^\]]+)\]", rest):
                key = resolve(keyexpr)
                try:
                    val = val[key]
                except Exception:
                    try:
                        val = val[int(key)]
                    except Exception:
                        return ""
            return val
        val = resolve(expr)
        if val is None:
            val = ""
        s = str(val)
        if filt == "e":
            s = html.escape(s, quote=True)
        return s

    BLOCK_RE = re.compile(r'\{%\s*block\s+(\w+)\s*%\}(.*?)\{%\s*endblock\s*%\}', re.S)

    def render_file(self, name, ctx):
        """渲染模板文件，支持 extends + block 继承、include。"""
        with open(os.path.join(self.dir, name), encoding="utf-8") as f:
            text = f.read()
        # extends：子模板的 block 覆盖父模板同名 block
        ext = re.match(r'\s*\{%\s*extends\s+\'([^\']+)\'\s*%\}', text)
        if ext:
            parent_name = ext.group(1)
            child = text[ext.end():]
            overrides = {m.group(1): m.group(2) for m in self.BLOCK_RE.finditer(child)}
            with open(os.path.join(self.dir, parent_name), encoding="utf-8") as f:
                parent = f.read()
            def repl(m):
                return overrides.get(m.group(1), m.group(2))
            text = self.BLOCK_RE.sub(repl, parent)
        return self.render(text, ctx)

    def render(self, text, ctx):
        # include
        def do_include(m):
            name = m.group(1).strip().strip("'\"")
            try:
                with open(os.path.join(self.dir, name), encoding="utf-8") as f:
                    return self.render(f.read(), ctx)
            except Exception:
                return ""
        text = re.sub(r'\{%\s*include\s+\'([^\']+)\'\s*%\}', do_include, text)

        # 递归处理 for / if 块
        text = self._blocks(text, ctx)
        # 变量插值
        text = re.sub(r'\{\{\s*(.*?)\s*\}\}', lambda m: self._eval(m.group(1), ctx), text, flags=re.S)
        return text

    def _find_block(self, text, start, tag):
        """从 start（块开标签之后）找到与之匹配的 endtag 位置，支持同类标签嵌套。"""
        depth = 1
        pos = start
        pattern = re.compile(r'\{%\s*(' + tag + r'|end' + tag + r')\b[^%]*%\}', re.S)
        while depth > 0:
            m = pattern.search(text, pos)
            if not m:
                return -1
            if m.group(1) == tag:
                depth += 1
            else:
                depth -= 1
            pos = m.end()
            if depth == 0:
                return (m.start(), m.end())
        return -1

    def _blocks(self, text, ctx):
        # 处理 for（支持 {% for k, v in dict %} 与嵌套 for）
        for_re = re.compile(r'\{%\s*for\s+([\w,\s]+?)\s+in\s+([\w\[\]\'"\.]+)\s*%\}', re.S)
        while True:
            m = for_re.search(text)
            if not m:
                break
            bounds = self._find_block(text, m.end(), "for")
            if bounds == -1:
                break
            body = text[m.end():bounds[0]]
            vars_ = [v.strip() for v in m.group(1).split(",")]
            iterable = m.group(2)
            seq = self._eval(iterable, ctx)
            if not isinstance(seq, (list, tuple, dict)):
                seq = []
            parts = []
            if isinstance(seq, dict):
                for k, v in seq.items():
                    c = dict(ctx)
                    if len(vars_) == 1:
                        c[vars_[0]] = v
                    else:
                        c[vars_[0]] = k
                        c[vars_[1]] = v
                    parts.append(self._blocks(body, c))
            else:
                for idx, v in enumerate(seq):
                    c = dict(ctx)
                    if len(vars_) == 1:
                        c[vars_[0]] = v
                    else:
                        c[vars_[0]] = idx
                        c[vars_[1]] = v
                    parts.append(self._blocks(body, c))
            text = text[:m.start()] + "".join(parts) + text[bounds[1]:]

        # if / else（支持嵌套 if 与简单比较 not in / ==）
        if_re = re.compile(r'\{%\s*if\s+(.*?)\s*%\}', re.S)
        while True:
            m = if_re.search(text)
            if not m:
                break
            bounds = self._find_block(text, m.end(), "if")
            if bounds == -1:
                break
            body = text[m.end():bounds[0]]
            cond = m.group(1).strip()
            # 拆分最外层的 else（注意嵌套 if 的 else 不能误拆）
            depth = 0
            else_pos = -1
            for em in re.finditer(r'\{%\s*(if|else|endif)\b[^%]*%\}', body, re.S):
                t = em.group(1)
                if t == "if":
                    depth += 1
                elif t == "endif":
                    depth -= 1
                elif t == "else" and depth == 0:
                    else_pos = em.start()
                    else_end = em.end()
                    break
            if else_pos >= 0:
                a, b = body[:else_pos], body[else_end:]
            else:
                a, b = body, ""
            chosen = a if self._eval_cond(cond, ctx) else b
            text = text[:m.start()] + self._blocks(chosen, ctx) + text[bounds[1]:]
        return text

    def _eval_cond(self, cond, ctx):
        cond = cond.strip()
        # not in
        m = re.match(r"(.+?)\s+not in\s+(.+)", cond)
        if m:
            return str(self._eval(m.group(1), ctx)) not in str(self._eval(m.group(2), ctx))
        # in
        m = re.match(r"(.+?)\s+in\s+(.+)", cond)
        if m:
            return str(self._eval(m.group(1), ctx)) in str(self._eval(m.group(2), ctx))
        # == / !=
        m = re.match(r"(.+?)\s*(==|!=)\s*(.+)", cond)
        if m:
            l = self._eval(m.group(1), ctx)
            r = self._eval(m.group(3), ctx)
            return (str(l) == str(r)) if m.group(2) == "==" else (str(l) != str(r))
        # truthy
        v = self._eval(cond, ctx)
        return bool(v) and str(v).lower() not in ("0", "none", "false", "")


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def clean_filename(title):
    """清洗标题为安全文件名。"""
    return re.sub(r'[<>:/\\|?*"]|[\x00-\x1f]', "-", title).strip()


def split_post_config(body):
    """
    解析文章末尾的 ##{...} 自定义配置。
    兼容 CRLF 与 LF（原版只支持 CRLF，这里修复）。
    """
    cfg = {}
    lines = [l for l in body.replace("\r\n", "\n").split("\n") if l.strip()]
    for line in reversed(lines[-3:]):
        line = line.strip()
        if line.startswith("##") and "{" in line:
            js = line.split("##", 1)[1].strip()
            try:
                cfg = json.loads(js)
            except Exception:
                pass
            break
    return cfg


def build_icon_subset(keys):
    """构建页面图标子集。键名大小写不敏感（兼容用户 exlink 里写 Github/github）。"""
    out = {}
    for k in keys:
        if k in ICON_PATHS:
            out[k] = ICON_PATHS[k]
        elif k.lower() in ICON_PATHS:
            out[k] = ICON_PATHS[k.lower()]
    return out


# ---------------------------------------------------------------------------
# 主体：BlogBuilder
# ---------------------------------------------------------------------------
class BlogBuilder:
    def __init__(self, token, repo, workspace, issue_number="0"):
        self.api = GitHubAPI(token, repo)
        self.repo = repo
        self.owner = repo.split("/")[0]
        self.repo_name = repo.split("/")[-1]
        self.ws = workspace
        self.issue_number = str(issue_number)
        self.root_dir = os.path.join(workspace, "docs")
        self.post_dir = os.path.join(self.root_dir, "post")
        self.backup_dir = os.path.join(workspace, "backup")
        self.static_dir = os.path.join(workspace, "assets")
        self.tpl = MiniTemplate(os.path.join(workspace, "templates"))
        self.pinyin = Pinyin(os.path.join(workspace, "data", "pinyin.json"))
        data_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.diagrams = DiagramRenderer(
            enabled=True,
            mmdc_bin=os.environ.get("MMDC_BIN", "mmdc"),
            tmp_dir=os.path.join(workspace, ".diagram-tmp"),
        )
        self.diagrams.ensure_puppeteer_config()
        self.old_feed = ""
        self.label_colors = {}
        self.blog = {}
        self.i18n = {}
        self._load_config()

    def _load_config(self):
        cfg = json.loads(json.dumps(DCONFIG))  # deep copy
        cfg_path = os.path.join(self.ws, "config.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, encoding="utf-8") as f:
                cfg.update(json.load(f))
        # 派生字段
        cfg["singlePage"] = cfg.get("singlePage") or []
        if not cfg.get("displayTitle"):
            cfg["displayTitle"] = cfg.get("title", "")
        if not cfg.get("faviconUrl"):
            cfg["faviconUrl"] = cfg.get("avatarUrl", "")
        if not cfg.get("ogImage"):
            cfg["ogImage"] = cfg.get("avatarUrl", "")
        if not cfg.get("homeUrl"):
            if self.repo_name.endswith(".github.io"):
                cfg["homeUrl"] = "https://" + self.repo_name
            else:
                cfg["homeUrl"] = "https://%s.github.io/%s" % (self.owner, self.repo_name)
        cfg["primerCSS"] = "<link href='/assets/primer.css' rel='stylesheet' />"
        cfg["diagramCSS"] = "<link href='/assets/diagram.css' rel='stylesheet' />"
        cfg["starryNightCSS"] = "/assets/vendor/starry-night.css"
        cfg["mathjaxJS"] = "/assets/vendor/tex-mml-chtml.js"
        # 用户自定义 script/head 指向本地资源时无需改动；保留原样
        cfg["postListJson"] = {}
        cfg["singeListJson"] = {}
        cfg["labelColorDict"] = {}
        self.blog = cfg
        lang = cfg.get("i18n", "CN").upper()
        self.i18n = I18N.get(lang, I18N["EN"])

    def clean_file(self):
        """先删后建再复制：docs/ 每次重建，assets/ 内容复制进 docs/assets/。"""
        for d in (os.path.join(self.ws, "backup"), self.root_dir):
            if os.path.isdir(d):
                shutil.rmtree(d)
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.root_dir, exist_ok=True)
        os.makedirs(self.post_dir, exist_ok=True)
        # 把 assets/ 整体复制进 docs/assets/
        if os.path.isdir(self.static_dir):
            dst = os.path.join(self.root_dir, "assets")
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            shutil.copytree(self.static_dir, dst)
            print("  [assets] 已复制本地静态资源到 docs/assets/")
        # 读旧 feed 用于增量检测
        feed_path = os.path.join(self.root_dir, "rss.xml")
        if os.path.exists(feed_path):
            with open(feed_path, encoding="utf-8") as f:
                self.old_feed = f.read()

    def make_filename(self, issue, use_label=False):
        if use_label and issue.get("labels"):
            name = issue["labels"][0]["name"]
        else:
            mode = self.blog.get("urlMode", "pinyin")
            title = issue.get("title", "")
            if mode == "issue":
                name = "P" + str(issue["number"])
            elif mode == "slug":
                name = re.sub(r"[^a-z0-9\-]", "", title.lower().replace(" ", "-"))
            else:  # pinyin（默认，内置数据表实现，无第三方依赖）
                name = self.pinyin.convert(title, sep="-")
            if not name:
                name = "P" + str(issue["number"])
        return clean_filename(name)

    def issue_to_entry(self, issue):
        """把一个 Issue 转成索引条目，并保存 markdown 原文到 backup/。"""
        labels = [l["name"] for l in issue.get("labels", [])]
        if not labels:
            return None
        number = issue["number"]
        is_single = labels[0] in self.blog["singlePage"]
        key = "P" + str(number)
        body = issue.get("body") or ""

        # 置顶：从 events 里找 pinned/unpinned
        top = 0
        try:
            events = self.api.get_events(number)
            for ev in events:
                if ev.get("event") == "pinned":
                    top = 1
                elif ev.get("event") == "unpinned":
                    top = 0
        except Exception:
            pass

        comments = issue.get("comments", 0)
        created_raw = issue.get("created_at", "")
        created_ts = int(time.mktime(time.strptime(created_raw[:19], "%Y-%m-%dT%H:%M:%S"))) if created_raw else int(time.time())
        created_date = time.strftime("%Y-%m-%d", time.gmtime(created_ts))
        year_color = self.blog["yearColorList"][int(time.strftime("%Y", time.gmtime(created_ts))) % len(self.blog["yearColorList"])]

        # 保存原文
        fname = self.make_filename(issue)
        if is_single:
            html_dir = os.path.join(self.root_dir, fname + ".html")
            backup_path = os.path.join(self.backup_dir, fname + ".md")
        else:
            html_dir = os.path.join(self.post_dir, fname + ".html")
            backup_path = os.path.join(self.backup_dir, fname + ".md")
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(body)

        # description
        description = ""
        if body:
            if self.blog.get("rssSplit") == "sentence":
                m = re.split(r"[。.]", body.replace("\n", " "), 1)
                description = (m[0] + ("。" if "。" in body[:len(m[0])+1] else "."))[:120]
            else:
                description = body[:120]

        entry = {
            "htmlDir": html_dir,
            "backupFile": os.path.basename(backup_path),
            "labels": labels,
            "postTitle": issue.get("title", ""),
            "postUrl": "/%s.html" % fname if is_single else "/post/%s.html" % fname,
            "postSourceUrl": "https://github.com/%s/issues/%s" % (self.repo, number),
            "commentNum": comments,
            "description": description,
            "wordCount": len(body),
            "content": body,
            "top": top,
            "createdAt": created_ts,
            "createdDate": created_date,
            "dateLabelColor": year_color,
        }
        # 文章级自定义配置（##{...}）
        cfg = split_post_config(body)
        for k in ("timestamp", "style", "script", "head", "ogImage"):
            if k in cfg:
                entry[k] = cfg[k]
        if "timestamp" in cfg:
            try:
                ts = int(cfg["timestamp"])
                entry["createdAt"] = ts
                entry["createdDate"] = time.strftime("%Y-%m-%d", time.gmtime(ts))
            except Exception:
                pass
        return "singeListJson" if is_single else "postListJson", entry

    def markdown_to_html(self, md_text):
        try:
            rendered = self.api.markdown(md_text)
        except Exception as e:
            # 健壮性：GitHub API 限流/网络异常时，用内置极简渲染兜底，
            # 保证构建不会因为临时故障整体失败。
            print("  [warn] Markdown API 不可用(%s)，使用内置渲染兜底" % str(e)[:80])
            rendered = self._fallback_markdown(md_text)
        # 图形构建时渲染
        rendered = self.diagrams.process(rendered)
        return rendered

    def _fallback_markdown(self, md_text):
        """仅覆盖常用语法的兜底渲染（正常情况走 GitHub API）。"""
        import html as _h
        s = md_text
        # mermaid 代码块先标记，供 diagrams 识别（用 GitHub 相同的 class 结构）
        def code_block(m):
            lang = m.group(1) or ""
            code = _h.escape(m.group(2))
            if lang == "mermaid":
                return '<div class="highlight highlight-source-mermaid"><pre>%s</pre></div>' % code
            return '<pre><code class="notranslate">%s</code></pre>' % code
        s = re.sub(r'```(\w*)\n(.*?)```', code_block, s, flags=re.S)
        s = _h.escape(s)
        # 还原代码块里已被二次转义的内容
        s = s.replace('&lt;div class=&quot;highlight', '<div class="highlight')
        s = re.sub(r'^### (.*)$', r'<h3>\1</h3>', s, flags=re.M)
        s = re.sub(r'^## (.*)$', r'<h2>\1</h2>', s, flags=re.M)
        s = re.sub(r'^# (.*)$', r'<h1>\1</h1>', s, flags=re.M)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img alt="\1" src="\2">', s)
        s = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', s)
        s = re.sub(r'^> (.*)$', r'<blockquote>\1</blockquote>', s, flags=re.M)
        s = re.sub(r'\n\n+', '</p><p>', s)
        return '<p>' + s + '</p>'

    def create_post_html(self, entry):
        """渲染文章页。"""
        post = dict(entry)
        # 读回原文做 markdown 渲染（用生成时的精确文件名，兼容旧数据兜底）
        backup = os.path.join(self.backup_dir, entry.get("backupFile") or (clean_filename(entry["postTitle"]) + ".md"))
        if not os.path.exists(backup):
            cand = [f for f in os.listdir(self.backup_dir) if f.endswith(".md")] if os.path.isdir(self.backup_dir) else []
            backup = os.path.join(self.backup_dir, self._find_backup(entry, cand)) if cand else backup
        md = ""
        if os.path.exists(backup):
            with open(backup, encoding="utf-8") as f:
                md = f.read()
        # 去掉末尾的 ##{...} 配置行再渲染
        md = re.sub(r"\n##\s*\{.*?\}\s*$", "", md, flags=re.S)
        body_html = self.markdown_to_html(md) if md else ""

        script = post.get("script", "") or self.blog.get("script", "")
        style = post.get("style", "") or self.blog.get("style", "")
        head = post.get("head", "") or self.blog.get("head", "")

        # 数学公式：GitHub gfm 输出 <math-renderer> 或含 $...$，注入本地 MathJax
        has_math = ("<math" in body_html or "math-renderer" in body_html or
                    re.search(r'\$[^$]+\$', md) is not None)
        if has_math:
            head += ('<script>window.MathJax={tex:{inlineMath:[["$","$"],["\\(","\\)"]],'
                     'displayMath:[["$$","$$"]]}};</script>'
                     '<script defer src="%s"></script>' % self.blog["mathjaxJS"])

        # GitHub Alerts 着色（gfm 原生输出 markdown-alert）
        if "markdown-alert" in body_html:
            style += self._alert_css()

        # 代码高亮：探测 pre + highlight 结构
        highlight = 0
        if "<pre" in body_html:
            highlight = 1 if "highlight" in body_html else 2
        if highlight == 1:
            head += '<link href="%s" rel="stylesheet" />' % self.blog["starryNightCSS"]

        icon_keys = ["sun", "moon", "sync", "home", "github"]
        if "<pre" in body_html:
            icon_keys += ["copy", "check"]
        icons = build_icon_subset(icon_keys)
        for k, v in (self.blog.get("iconList") or {}).items():
            icons[k] = v

        ctx = dict(self.blog)
        ctx.update({
            "postTitle": post["postTitle"],
            "postUrl": self.blog["homeUrl"] + post["postUrl"],
            "description": post["description"],
            "ogImage": post.get("ogImage", self.blog["ogImage"]),
            "postBody": body_html,
            "commentNum": post["commentNum"],
            "style": style,
            "script": script,
            "head": head,
            "highlight": highlight,
            "bottomText": self.blog["bottomText"],
            "postSourceUrl": post["postSourceUrl"],
            "repoName": self.repo,
            "repo": self.repo,
            "i18n": self.i18n,
            "IconList": icons,
        })
        # 单页清空底部文字
        if post["labels"] and post["labels"][0] in self.blog["singlePage"]:
            ctx["bottomText"] = ""
        out = self.tpl.render_file("post.html", ctx)
        os.makedirs(os.path.dirname(post["htmlDir"]), exist_ok=True)
        with open(post["htmlDir"], "w", encoding="utf-8") as f:
            f.write(out)

    def _find_backup(self, entry, candidates):
        """按 postUrl 的文件名找到对应 backup。"""
        want = os.path.basename(entry["postUrl"])
        for c in candidates:
            if c[:-3] == want[:-5]:
                return c
        return candidates[0]

    def _alert_css(self):
        return """
<style>
.markdown-alert{border-left:.25em solid var(--color-border-default);padding:8px 16px;margin:16px 0;border-radius:6px}
.markdown-alert-note{border-left-color:var(--borderColor-accent-emphasis,#0969da)}
.markdown-alert-tip{border-left-color:var(--borderColor-success-emphasis,#1a7f37)}
.markdown-alert-important{border-left-color:var(--borderColor-done-emphasis,#8250df)}
.markdown-alert-warning{border-left-color:var(--borderColor-attention-emphasis,#9a6700)}
.markdown-alert-caution{border-left-color:var(--borderColor-danger-emphasis,#cf222e)}
.markdown-alert-title{font-weight:600;margin-bottom:4px}
</style>"""

    def create_list_html(self):
        """首页 / 分页 / 标签搜索页。"""
        posts = self.blog["postListJson"]
        singles = self.blog["singeListJson"]
        ordered = sorted(posts.values(), key=lambda p: (p.get("top", 0), p.get("createdAt", 0)), reverse=True)
        per = int(self.blog.get("onePageListNum", 15))
        total = len(ordered)
        pages = max(1, (total + per - 1) // per)

        icon_keys = ["sun", "moon", "sync", "search", "rss", "upload", "post", "home", "github"] + \
                    list(self.blog.get("singlePage", [])) + list(self.blog.get("exlink", {}).keys())
        icons = build_icon_subset(icon_keys)
        # 用户自定义图标覆盖（旧版 iconList 字段）
        custom_icons = self.blog.get("iconList") or {}
        for k, v in custom_icons.items():
            icons[k] = v
        base_ctx = dict(self.blog)
        base_ctx.update({
            "i18n": self.i18n,
            "IconList": icons,
            "labelColorDict": self.blog["labelColorDict"],
            "singeListJson": singles,
        })
        for p in range(pages):
            start = p * per
            page_posts = ordered[start:start + per]
            prev_url = "disabled" if p == 0 else ("/index.html" if p == 1 else "/page%d.html" % p)
            next_url = "disabled" if p >= pages - 1 else "/page%d.html" % (p + 2)
            ctx = dict(base_ctx)
            ctx.update({
                "postListJson": {i: post for i, post in enumerate(page_posts)},
                "prevUrl": prev_url,
                "nextUrl": next_url,
            })
            out = self.tpl.render_file("plist.html", ctx)
            path = os.path.join(self.root_dir, "index.html" if p == 0 else "page%d.html" % (p + 1))
            with open(path, "w", encoding="utf-8") as f:
                f.write(out)

        # 标签 + 全文搜索页
        tag_ctx = dict(base_ctx)
        tag_ctx["postListJson"] = {k: v for k, v in posts.items()}
        tag_out = self.tpl.render_file("tag.html", tag_ctx)
        with open(os.path.join(self.root_dir, "tag.html"), "w", encoding="utf-8") as f:
            f.write(tag_out)

    def create_feed(self):
        """手写 RSS 2.0 XML（标准库，无 feedgen）。"""
        entries = list(self.blog["postListJson"].values()) + list(self.blog["singeListJson"].values())
        entries = sorted(entries, key=lambda p: p.get("createdAt", 0))
        items = []
        for p in entries:
            item = ET.Element("item")
            ET.SubElement(item, "guid", isPermaLink="true").text = self.blog["homeUrl"] + p["postUrl"]
            ET.SubElement(item, "title").text = p["postTitle"]
            ET.SubElement(item, "description").text = p.get("description", "")
            ET.SubElement(item, "link").text = self.blog["homeUrl"] + p["postUrl"]
            pub = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(p.get("createdAt", 0)))
            ET.SubElement(item, "pubDate").text = pub
            items.append(item)

        def build(last_build):
            rss = ET.Element("rss", version="2.0")
            ch = ET.SubElement(rss, "channel")
            ET.SubElement(ch, "title").text = self.blog.get("title", "")
            ET.SubElement(ch, "description").text = self.blog.get("subTitle", "")
            ET.SubElement(ch, "link").text = self.blog["homeUrl"]
            ET.SubElement(ch, "ttl").text = "60"
            ET.SubElement(ch, "lastBuildDate").text = last_build
            for it in items:
                ch.append(it)
            ET.indent(rss, space="  ")
            return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(rss, encoding="unicode")

        now_str = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        new_xml = build(now_str)
        # 增量：去掉 lastBuildDate 后相同则沿用旧文件
        if self.old_feed:
            strip = lambda s: re.sub(r"<lastBuildDate>.*?</lastBuildDate>", "", s)
            if strip(new_xml) == strip(self.old_feed):
                with open(os.path.join(self.root_dir, "rss.xml"), "w", encoding="utf-8") as f:
                    f.write(self.old_feed)
                return
        with open(os.path.join(self.root_dir, "rss.xml"), "w", encoding="utf-8") as f:
            f.write(new_xml)

    def write_index_data(self):
        """写 blogBase.json（调试/增量用）。"""
        with open(os.path.join(self.ws, "blogBase.json"), "w", encoding="utf-8") as f:
            json.dump(self.blog, f, ensure_ascii=False, separators=(",", ":"))

    def write_post_list(self):
        """裁剪后的搜索索引 docs/postList.json（含 content 全文）。"""
        data = {}
        posts = dict(self.blog["postListJson"])
        for k, p in posts.items():
            data[k] = {
                "labels": p["labels"],
                "postTitle": p["postTitle"],
                "postUrl": p["postUrl"],
                "content": p.get("content", ""),
                "createdDate": p["createdDate"],
                "dateLabelColor": p["dateLabelColor"],
            }
        data["labelColorDict"] = self.blog["labelColorDict"]
        with open(os.path.join(self.root_dir, "postList.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    def run_all(self):
        print("[runAll] 全量构建开始")
        self.clean_file()
        labels = self.api.get_labels()
        self.label_colors = {l["name"]: "#" + l["color"] for l in labels}
        self.blog["labelColorDict"] = self.label_colors
        issues = self.api.get_issues()
        print("  拉取到 %d 篇 Issue" % len(issues))
        for issue in issues:
            try:
                result = self.issue_to_entry(issue)
                if result:
                    key, entry = result
                    self.blog[key]["P" + str(issue["number"])] = entry
            except Exception as e:
                print("  [skip] Issue #%s: %s" % (issue.get("number"), str(e)[:100]))
        self._render_all_outputs()

    def run_one(self, number):
        print("[runOne] 单篇构建 #%s" % number)
        # 增量：复用已有 blogBase
        bb_path = os.path.join(self.ws, "blogBase.json")
        if os.path.exists(bb_path):
            with open(bb_path, encoding="utf-8") as f:
                old = json.load(f)
            self.blog.update(old)
        issue = self.api.get_issue(number)
        if issue.get("state") != "open":
            print("  Issue 已关闭，跳过")
            return
        result = self.issue_to_entry(issue)
        if not result:
            print("  Issue 无 label，跳过")
            return
        key, entry = result
        # 重新拉 labels 补齐颜色
        try:
            self.label_colors = {l["name"]: "#" + l["color"] for l in self.api.get_labels()}
            self.blog["labelColorDict"] = self.label_colors
        except Exception:
            pass
        self.blog[key]["P" + str(number)] = entry
        # 只渲染这一篇，再重建列表/RSS/索引
        self.create_post_html(entry)
        self._render_all_outputs(skip_posts=True)

    def _render_all_outputs(self, skip_posts=False):
        if not skip_posts:
            print("  生成文章 HTML...")
            for key in ("postListJson", "singeListJson"):
                for entry in self.blog[key].values():
                    try:
                        self.create_post_html(entry)
                    except Exception as e:
                        print("  [skip html] %s: %s" % (entry.get("postTitle"), str(e)[:100]))
        print("  生成列表 / 标签 / 搜索页...")
        self.create_list_html()
        print("  生成 RSS...")
        self.create_feed()
        self.write_index_data()
        self.write_post_list()
        print("  完成。")

    def _read_tpl(self, name):
        with open(os.path.join(self.ws, "templates", name), encoding="utf-8") as f:
            return f.read()


def main():
    args = sys.argv[1:]
    if len(args) < 3:
        print("用法: python build.py <token> <owner/repo> [--issue_number N] [--workspace DIR]")
        sys.exit(1)
    token, repo = args[0], args[1]
    issue_number = "0"
    workspace = os.environ.get("GITHUB_WORKSPACE") or os.getcwd()
    i = 2
    while i < len(args):
        if args[i] == "--issue_number" and i + 1 < len(args):
            issue_number = args[i + 1]
            i += 2
        elif args[i] == "--workspace" and i + 1 < len(args):
            workspace = args[i + 1]
            i += 2
        else:
            i += 1

    # 保证从健壮的 issue_number 判定（原版有 int/str 比较 bug，这里统一字符串）
    builder = BlogBuilder(token, repo, workspace, issue_number)
    if issue_number in ("", "0", "None"):
        builder.run_all()
    else:
        builder.run_one(issue_number)


if __name__ == "__main__":
    main()
