/*
 * 评论主题同步辅助（评论主体逻辑在 post.html 内联，直读 GitHub Issues，零外部服务）。
 * 本文件仅负责把当前站点主题同步给评论区的 data-color-mode，供样式继承。
 */
(function () {
  function sync() {
    var mode = document.documentElement.getAttribute('data-color-mode') || 'light';
    var frame = document.getElementById('comments');
    if (frame) frame.setAttribute('data-color-mode', mode);
  }
  document.addEventListener('DOMContentLoaded', sync);
  window.applyCommentTheme = sync;
})();
