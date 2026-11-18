/*
 * 自托管访问量统计（替代 vercount.one）
 * 数据存在你自己的 Cloudflare Worker + KV 里，不依赖任何第三方。
 * 用法：在 config.json 的 allHead 里填
 *   <script src="/assets/counter.js" data-endpoint="https://你的worker.workers.dev" defer></script>
 * 未配置 data-endpoint 时不请求、不显示，页面其余部分不受影响（优雅降级）。
 */
(function () {
  var me = document.currentScript;
  var endpoint = (me && me.getAttribute('data-endpoint')) || '';
  if (!endpoint) return; // 未启用计数时静默退出

  function inject() {
    var path = location.pathname;
    fetch(endpoint + '/api/count?p=' + encodeURIComponent(path), { method: 'GET' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d) return;
        var postBody = document.getElementById('postBody');
        var runday = document.getElementById('runday');
        if (postBody && typeof d.page === 'number') {
          postBody.insertAdjacentHTML('afterend',
            '<div style="float:left;margin-top:8px;font-size:small;color:var(--color-fg-muted)">本文浏览量 ' + d.page + ' 次</div>');
        }
        if (runday && typeof d.site === 'number') {
          runday.insertAdjacentHTML('afterend',
            '<span style="color:var(--color-fg-muted)">总浏览量 ' + d.site + ' 次 • </span>');
        }
      })
      .catch(function () { /* 统计失败不影响页面 */ });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
