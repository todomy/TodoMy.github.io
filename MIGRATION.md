# 从旧独立版 Gmeek 迁移到 TodoMy-Next

好消息：**你的文章不用动**。内容都在 GitHub Issues 里，TodoMy-Next 直接从 Issues 读取，换的是「生成方式」不是「数据」。

## 原地替换现有仓库（以 todomy/TodoMy.github.io 为例）

如果只是想把自己原来的仓库「原地换引擎」，按这一节走。**config.json 已经按你原仓库的配置迁好，不用再改。**

### 第 1 步：本地先留两份备份

- 把原仓库的 `backup/` 目录（历史文章 Markdown）整个复制一份到仓库外。新构建会删掉并重建它；虽然文章都在 Issues 里，但如果有已删除 Issue 的残留备份，只有这份留档还在。
- 原 `docs/` 会被全量构建清空重建，无需备份（只是产物）。

### 第 2 步：上传新项目文件，同时处理旧文件

把 TodoMy-Next 的全部文件覆盖上传到仓库 **main 分支**，然后**删掉这些旧文件/目录**（它们是旧引擎专用，留下会互相干扰或造成误解）：

```
Gmeek.py
requirements.txt
blogBase.json              ← 必须删！否则首次单篇构建会拿旧状态覆盖新配置
.github/workflows/Gmeek.yml ← 必须删！否则旧 workflow 每天仍会跑并失败
plugins/                   ← 已全部本地化到 assets/
static/                    ← 已由 assets/ 取代
templates/                 ← 同名覆盖即可，确认没有多余旧模板残留
```

**务必保留 `附件/` 目录**，有文章链接到 `github.com/todomy/TodoMy.github.io/tree/main/附件/H3C NX30Pro`，删了那个链接就 404。文章里的图片都是 `user-attachments` 绝对地址，不受 `docs/` 重建影响。

### 第 3 步：GitHub 后台设置（一次性）

1. **Settings → Actions → General → Workflow permissions**：选 **Read and write permissions**。构建要把生成的 `docs/` 提交回仓库；只读权限会导致提交失败。
2. **Settings → Pages → Build and deployment**：Source 选 **Deploy from a branch**，Branch 选 **main**，目录选 **/docs**。原来就指向 `/docs` 的话不用动。
3. 旧仓库没有自定义域名文件（无 `CNAME`），站点地址仍是 `https://todomy.github.io`。

### 第 4 步：手动触发一次全量构建

在 **Actions → Build Blog → Run workflow** 手动跑一次，`issue_number` 传空（全量）。这一步会：

- 从你的 Issues 重新拉全部文章（约 160 篇）
- 重建 `docs/`、文章页、标签页、搜索索引、RSS
- 写回新的 `blogBase.json`

**不要跳过这步直接用「新建 Issue」触发**：那样会走单篇构建路径，若旧 `blogBase.json` 没删干净会污染站点。

### 第 5 步：验收

- 首页文章数与原站一致
- 打开那篇带 H3C 附件的文章，下载链接能跳到仓库 `附件/` 目录
- 标签页、搜索、明暗主题、RSS 正常
- 「link」「about」两个单页在（旧配置里的 label 名是 `link`，不是 `links`）
- 写一篇带 ` ```mermaid ` 的测试 Issue，构建后能看到 SVG 图，然后关掉该 Issue

> 访问量：原 vercount.one 的历史数据无法迁出。本站 `config.json` 的 `allHead` 已留空，所以暂时不显示访问量，页面其余功能正常。以后想启用，按 README 3.3 部署自己的 Worker 再填回去。

---

## 迁移清单

### 1. 配置字段对应关系

把旧仓库 `config.json` 的字段搬过来，大部分字段名一致。新增/变化的有：

| 旧字段 | 新字段 | 说明 |
|---|---|---|
| `GMEEK_VERSION` | — | 删除。新项目完全独立，没有上游版本 |
| `script` 里的 jsDelivr 插件地址 | 留空或改本地路径 | 插件已全部本地化到 `assets/`，TOC/灯箱/访问量自动加载 |
| `allHead` 里的 vercount 脚本 | counter.js 地址 | 换成自托管计数（见 README 3.3） |
| `primerCSS`（若配过） | — | 生成器自动指向 `/assets/primer.css`，不用手填 |
| — | `enableDiagrams` | 新增，设 1 启用 Mermaid 图形 |

其余字段（`title / subTitle / displayTitle / avatarUrl / singlePage / i18n / themeMode / urlMode / exlink / filingNum / startSite` 等）**原样照搬**。

### 2. URL 会变吗？

- `urlMode: pinyin`（默认）：新项目用内置拼音表生成的文件名，和 xpinyin 的结果**基本一致**，绝大多数文章 URL 不变。少数多音字可能不同——如果介意，把 `urlMode` 改成 `issue`，URL 变成 `/post/P123.html` 这种永久稳定的编号形式（更推荐，彻底无歧义）。
- 建议迁移后检查 `docs/postList.json` 里的 `postUrl`，对个别 URL 变化的老文章加 301 或接受搜索引擎重新收录。

### 3. 评论迁移

- 旧评论在 utteranc.es，数据存在你仓库的 Issues 里（issue-term=title）。
- TodoMy-Next 直接读这些 Issues 的评论，**评论内容全在**。
- 区别：新项目评论框直读 GitHub API，发表评论跳转到对应 Issue（静态站无后端，这是零依赖下的最稳做法）。

### 4. 访问量迁移

- vercount.one 的历史数据无法迁出（它在第三方）。
- 从迁移这天起，用你自己的 Worker + KV 重新计数，数据归你。

### 5. 静态资源

- 新项目 `assets/` 已经带了全套本地资源（Primer CSS、代码高亮、MathJax、TOC、灯箱等），不用从旧仓库拷。
- 如果你自定义过 `plugins/` 里的脚本，把它们放进新项目的 `assets/`，并在 config.json 的 `script/head` 里用 `/assets/你的文件.js` 引用。

### 6. 部署切换

1. 新仓库按 README 第 3 节配好 Pages 和 Actions 权限。
2. 第一次触发构建（点一次 Run workflow），生成 `docs/`。
3. 确认 `https://你的域名` 正常后，再把旧仓库的 Pages 关闭或改指向新仓库。
4. GitHub Pages 自定义域名的话，记得在新仓库重新绑定并配置 DNS。

## 迁移后验证清单

- [ ] 首页正常显示文章列表
- [ ] 点开任意文章，正文/代码高亮/数学公式正常
- [ ] 标签页和全文搜索可用
- [ ] 写一篇带 ```mermaid 代码块的文章，构建后能看到 SVG 图
- [ ] 主题切换（明/暗/自动）正常
- [ ] 评论能显示（直读 Issues）
- [ ] 访问量（若启用）能显示

## 回滚

TodoMy-Next 不修改你的 Issues，只生成 `docs/`。任何问题都可以随时切回旧仓库的 Pages 配置，数据零丢失。
