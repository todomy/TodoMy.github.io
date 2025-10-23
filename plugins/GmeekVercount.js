function createVercount() {
    // 移除外部统计服务依赖
    // 可选：实现简单的本地存储统计（有局限性，但无外部依赖）
    var postBody = document.getElementById('postBody');
    if (postBody){
        // 使用本地存储进行简单的页面访问计数
        const pageId = window.location.pathname;
        let count = localStorage.getItem(`page_visit_${pageId}`);
        count = count ? parseInt(count) + 1 : 1;
        localStorage.setItem(`page_visit_${pageId}`, count);
        
        postBody.insertAdjacentHTML('afterend',`<div id="local_container_page_pv" style="float:left;margin-top:8px;font-size:small;">本文浏览量${count}次</div>`);
    }
    
    var runday = document.getElementById('runday');
    if (runday) {
        // 计算总页面访问量（基于本地存储中记录的所有页面）
        let totalCount = 0;
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith('page_visit_')) {
                totalCount += parseInt(localStorage.getItem(key) || 0);
            }
        }
        
        runday.insertAdjacentHTML('afterend', `<span id="local_container_site_pv">总浏览量${totalCount}次 • </span>`);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    createVercount();
    // 移除外部脚本加载
});
