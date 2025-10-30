(()=>{// 添加资源提示以优化连接
const addResourceHints = () => {
  // 添加preconnect以优化与utteranc.es的连接
  const preconnectLink = document.createElement('link');
  preconnectLink.rel = 'preconnect';
  preconnectLink.href = 'https://utteranc.es';
  document.head.appendChild(preconnectLink);
  
  // 添加dns-prefetch作为后备
  const dnsPrefetchLink = document.createElement('link');
  dnsPrefetchLink.rel = 'dns-prefetch';
  dnsPrefetchLink.href = 'https://utteranc.es';
  document.head.appendChild(dnsPrefetchLink);
  
  // 预加载暗色主题CSS
  const darkThemeLink = document.createElement('link');
  darkThemeLink.rel = 'preload';
  darkThemeLink.href = 'https://utteranc.es/stylesheets/themes/github-dark/utterances.css';
  darkThemeLink.as = 'style';
  darkThemeLink.media = 'print';
  darkThemeLink.onload = () => {
    darkThemeLink.media = 'all';
  };
  document.head.appendChild(darkThemeLink);
};

// 执行资源提示添加
addResourceHints();

// 原有功能代码开始
const e = window.matchMedia("(prefers-color-scheme: dark)").matches ? "github-dark" : "github-light";
const t = new URL(location.href);
const n = t.searchParams.get("utterances");

if (n) {
  localStorage.setItem("utterances-session", n);
  t.searchParams.delete("utterances");
  history.replaceState(void 0, document.title, t.href);
}

let r = document.currentScript;
if (void 0 === r) {
  r = document.querySelector('script[src^="https://utteranc.es/client.js"],script[src^="http://localhost:4000/client.js"],script[src^="/plugins/utterances.client.js"]');
}

const i = {};
for (let e = 0; e < r.attributes.length; e++) {
  const t = r.attributes.item(e);
  i[t.name.replace(/^data-/, '')] = t.value;
}

if ("preferred-color-scheme" === i.theme) {
  i.theme = e;
}

const a = document.querySelector("link[rel='canonical']");
i.url = a ? a.href : t.origin + t.pathname + t.search;
i.origin = t.origin;
i.pathname = t.pathname.length < 2 ? "index" : t.pathname.substr(1).replace(/\.\w+$/, '');
i.title = document.title;

const s = document.querySelector("meta[name='description']");
i.description = s ? s.content : "";

const o = encodeURIComponent(i.description).length;
if (o > 1e3) {
  i.description = i.description.substr(0, Math.floor(1e3 * i.description.length / o));
}

const c = document.querySelector("meta[property='og:title'],meta[name='og:title']");
i["og:title"] = c ? c.content : "";
i.session = n || localStorage.getItem("utterances-session") || "";

// 优化样式：添加加载状态和骨架屏
const styles = `
  <style>
    .utterances {
      position: relative;
      box-sizing: border-box;
      width: 100%;
      max-width: 760px;
      margin-left: auto;
      margin-right: auto;
      min-height: 200px; /* 确保有足够空间显示加载状态 */
    }
    .utterances-frame {
      color-scheme: light;
      position: absolute;
      left: 0;
      right: 0;
      width: 1px;
      min-width: 100%;
      max-width: 100%;
      height: 100%;
      border: 0;
    }
    .utterances-skeleton {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(90deg, var(--skeleton-start, #f0f0f0) 25%, var(--skeleton-middle, #e0e0e0) 50%, var(--skeleton-end, #f0f0f0) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
      z-index: 1;
      border-radius: 4px;
      border: 1px solid var(--color-border-default, #e1e4e8);
    }
    @keyframes shimmer {
      0% { background-position: -200% 0; }
      100% { background-position: 200% 0; }
    }
    .utterances-loading {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      z-index: 2;
      font-size: 14px;
      color: var(--color-text-secondary, #666);
      background: var(--color-bg-primary, #ffffff);
      padding: 10px 20px;
      border-radius: 6px;
      border: 1px solid var(--color-border-default, #e1e4e8);
    }
    .utterances-loaded .utterances-skeleton,
    .utterances-loaded .utterances-loading {
      display: none;
    }
  </style>`;

document.head.insertAdjacentHTML("afterbegin", styles);

const l = r.src.match(/^https:\/\/utteranc\.es|http:\/\/localhost:\d+|\/plugins\/utterances\.client\.js$/)[0];
const h = l.includes('plugins') ? 'https://utteranc.es' : l;
const u = `${h}/utterances.html`;

// 添加带骨架屏和加载状态的容器
r.insertAdjacentHTML("afterend", `
  <div class="utterances">
    <div class="utterances-skeleton"></div>
    <div class="utterances-loading">加载评论中...</div>
    <iframe 
      class="utterances-frame" 
      title="Comments" 
      scrolling="no" 
      src="${u}?${new URLSearchParams(i)}" 
      loading="lazy"
      onload="this.parentElement.classList.add('utterances-loaded')"
    ></iframe>
  </div>
`);

const m = r.nextElementSibling;
r.parentElement.removeChild(r);

// 添加超时处理
let timeoutId = setTimeout(() => {
  const container = document.querySelector('.utterances');
  if (container && !container.classList.contains('utterances-loaded')) {
    console.warn('Utterances加载超时，尝试重新加载...');
    // 重新加载iframe
    const iframe = container.querySelector('.utterances-frame');
    if (iframe) {
      iframe.src = iframe.src;
    }
  }
}, 10000); // 10秒超时

// 消息处理函数
function handleMessage(e) {
  if (e.origin !== h) return;
  
  const t = e.data;
  if (t && "resize" === t.type && t.height) {
    // 清除超时定时器
    clearTimeout(timeoutId);
    // 设置高度并标记为已加载
    m.style.height = `${t.height}px`;
    m.classList.add('utterances-loaded');
  }
}

// 添加消息监听器
addEventListener("message", handleMessage);
})();