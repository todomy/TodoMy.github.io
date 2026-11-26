function createTOC() {
    var tocElement = document.createElement('div');
    tocElement.className = 'toc';
    var contentContainer = document.getElementById('content');
    
    const headings = contentContainer.querySelectorAll('h1, h2, h3, h4, h5, h6');
    
    if (headings.length === 0) {
        return false;  // 没有标题不创建 TOC，告知调用方无需注入样式与滚动监听
    }
    
    tocElement.insertAdjacentHTML('afterbegin', '<div class="toc-title">文章目录</div>');
    
    const usedIds = new Set();
    headings.forEach(heading => {
        if (!heading.id) {
            let base = heading.textContent.trim().replace(/\s+/g, '-').toLowerCase();
            let id = base, n = 1;
            while (usedIds.has(id)) { id = base + '-' + (n++); }
            usedIds.add(id);
            heading.id = id;
        }
        const link = document.createElement('a');
        link.href = '#' + heading.id;
        link.textContent = heading.textContent;
        link.className = 'toc-link';
        link.style.paddingLeft = `${(parseInt(heading.tagName.charAt(1)) - 1) * 10}px`;
        tocElement.appendChild(link);
    });
    
    // href 提供原生键盘可达（Tab 聚焦、Enter 触发），role/tabindex 让辅助技术识别为按钮；
    // preventDefault 阻止 # 跳到页首覆盖平滑滚动，keydown 补上空格键。
    tocElement.insertAdjacentHTML('beforeend', '<a class="toc-end" href="#" role="button" tabindex="0" onclick="event.preventDefault();window.scrollTo({top:0,behavior:\'smooth\'});" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();window.scrollTo({top:0,behavior:\'smooth\'});}">Top</a>');
    contentContainer.prepend(tocElement);
    return true;
}

document.addEventListener("DOMContentLoaded", function() {
    if (!createTOC()) return;  // 无标题页不注入样式、不注册滚动监听
    var css = `
    .toc {
        position:fixed;
        top:130px;
        left:50%;
        transform: translateX(50%) translateX(320px);
        width:200px;
        border: 1px solid #e1e4e8;
        border-radius: 6px;
        padding: 10px;
        overflow-y: auto;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        max-height: 70vh;
    }
    .toc-title{
        font-weight: bold;
        text-align: center;
        border-bottom: 1px solid #ddd;
        padding-bottom: 8px;
    }
    .toc-end{
        font-weight: bold;
        text-align: center;
        cursor: pointer;
        visibility: hidden;
    }  
    .toc a {
        display: block;
        color: var(--color-diff-blob-addition-num-text);
        text-decoration: none;
        padding: 5px 0;
        font-size: 14px;
        line-height: 1.5;
        border-bottom: 1px solid #e1e4e8;
    }
    .toc a:last-child {
        border-bottom: none;
    }
    .toc a:hover {
        background-color:var(--color-select-menu-tap-focus-bg);
    }

    @media (max-width: 1249px) 
    {
        .toc{
            position:static;
            top:auto;
            left:auto;
            transform:none;
            padding:10px;
            margin-bottom:20px;
        }
    }`;

    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);

    window.addEventListener('scroll', function() {
        const backToTopButton = document.querySelector('.toc-end');
        if (!backToTopButton) { return; }
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            backToTopButton.style="visibility: visible;"
        } else {
            backToTopButton.style="visibility: hidden;"
        }
    });

});
