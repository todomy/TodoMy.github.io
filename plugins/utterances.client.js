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
// 添加基本样式，避免重复添加
if (!document.getElementById('utterances-styles')) {
  const styleElement = document.createElement('style');
  styleElement.id = 'utterances-styles';
  styleElement.textContent = `
    .utterances {
      position: relative;
      box-sizing: border-box;
      width: 100%;
      max-width: 760px;
      margin-left: auto;
      margin-right: auto;
      min-height: 100px; /* 确保有足够空间显示加载状态 */
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
    .utterances-loading {
      text-align: center;
      padding: 20px;
      font-size: 14px;
      color: var(--color-text-secondary, #666);
    }
    .utterances-loaded .utterances-loading {
      display: none;
    }
  `;
  document.head.appendChild(styleElement);
}

const l = r.src.match(/^https:\/\/utteranc\.es|http:\/\/localhost:\d+|\/plugins\/utterances\.client\.js$/)[0];
const h = l.includes('plugins') ? 'https://utteranc.es' : l;
const u = `${h}/utterances.html`;

// 创建评论容器
const container = document.createElement('div');
container.className = 'utterances';

// 创建加载状态元素
const loadingDiv = document.createElement('div');
loadingDiv.className = 'utterances-loading';
loadingDiv.textContent = '正在加载评论...';
container.appendChild(loadingDiv);

// 创建iframe元素
const iframe = document.createElement('iframe');
iframe.className = 'utterances-frame';
iframe.title = 'Comments';
iframe.scrolling = 'no';
iframe.src = `${u}?${new URLSearchParams(i)}`;
iframe.loading = 'lazy';

// 使用事件监听器而不是内联事件
iframe.addEventListener('load', function() {
  container.classList.add('utterances-loaded');
  // 清除超时定时器
  if (timeoutId) clearTimeout(timeoutId);
});

container.appendChild(iframe);

// 插入容器到DOM
r.parentNode.insertBefore(container, r.nextSibling);

// 移除原始脚本元素
r.parentNode.removeChild(r);

// 添加超时处理
let timeoutId = setTimeout(() => {
  if (!container.classList.contains('utterances-loaded')) {
    console.warn('Utterances加载超时，尝试重新加载...');
    // 重新加载iframe
    if (iframe) {
      iframe.src = iframe.src;
      // 重置超时
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        if (!container.classList.contains('utterances-loaded')) {
          console.warn('Utterances加载再次超时');
          // 标记为加载完成，避免加载提示一直显示
          container.classList.add('utterances-loaded');
        }
      }, 10000); // 再次尝试10秒
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
    container.style.height = `${t.height}px`;
    container.classList.add('utterances-loaded');
  }
}

// 添加消息监听器
addEventListener("message", handleMessage);
})();