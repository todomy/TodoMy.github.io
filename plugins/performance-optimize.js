// 性能优化脚本 - 虚拟列表和延迟DOM创建
(function() {
    console.log('性能优化脚本已加载');
    
    // 保存原始的XMLHttpRequest.open方法
    const originalOpen = XMLHttpRequest.prototype.open;
    let postListData = null;
    let currentPage = 1;
    const itemsPerPage = 500;
    
    // 拦截XMLHttpRequest请求
    XMLHttpRequest.prototype.open = function(method, url, ...args) {
        // 只拦截postList.json的请求
        if (url === 'postList.json') {
            this.addEventListener('load', function() {
                if (this.status === 200) {
                    try {
                        // 缓存完整数据
                        postListData = JSON.parse(this.responseText);
                        console.log('已缓存文章数据，共', postListData.length, '篇文章');
                        
                        // 替换响应为第一页数据
                        const firstPageData = postListData.slice(0, itemsPerPage);
                        Object.defineProperty(this, 'responseText', {
                            value: JSON.stringify(firstPageData)
                        });
                    } catch (e) {
                        console.error('处理文章数据时出错:', e);
                    }
                }
            });
        }
        return originalOpen.apply(this, [method, url, ...args]);
    };
    
    // 等待页面加载完成
    window.addEventListener('load', function() {
        // 保存原始的showList函数
        const originalShowList = window.showList;
        
        // 重写showList函数
        window.showList = function(data) {
            // 如果是我们拦截的请求，显示加载状态
            if (data.length === itemsPerPage && postListData && postListData.length > itemsPerPage) {
                // 先调用原始函数显示第一页
                originalShowList(data);
                
                // 添加加载更多按钮
                addLoadMoreButton();
            } else {
                // 正常调用原始函数
                originalShowList(data);
            }
        };
        
        // 保存原始的searchShow函数
        const originalSearchShow = window.searchShow;
        
        // 重写searchShow函数
        window.searchShow = function() {
            const searchInput = document.getElementsByClassName('subnav-search-input')[0].value.toLowerCase();
            
            if (postListData && searchInput) {
                console.log('执行增量搜索...');
                
                // 使用缓存的完整数据进行搜索
                const filteredItems = postListData.filter(item => {
                    const titleMatch = item.title.toLowerCase().includes(searchInput);
                    const contentMatch = item.content && item.content.toLowerCase().includes(searchInput);
                    return titleMatch || contentMatch;
                });
                
                console.log('找到', filteredItems.length, '个匹配结果');
                
                // 显示前500个结果
                const displayItems = filteredItems.slice(0, 500);
                
                // 清空现有列表
                const contentDiv = document.getElementById('content');
                const listContainer = contentDiv.querySelector('div[style*="display:grid"]') || contentDiv.querySelector('nav + div');
                if (listContainer) {
                    listContainer.innerHTML = '';
                }
                
                // 显示结果
                originalShowList(displayItems);
                
                // 显示搜索结果数量提示
                showSearchResultCount(filteredItems.length);
                
                // 如果有更多结果，添加查看更多按钮
                if (filteredItems.length > 500) {
                    addViewMoreResultsButton(filteredItems);
                }
                
                return; // 阻止执行原始函数
            }
            
            // 无搜索词时调用原始函数
            originalSearchShow();
        };
    });
    
    // 添加加载更多按钮
    function addLoadMoreButton() {
        const contentDiv = document.getElementById('content');
        let loadMoreButton = document.getElementById('loadMoreBtn');
        
        if (!loadMoreButton) {
            loadMoreButton = document.createElement('div');
            loadMoreButton.id = 'loadMoreBtn';
            loadMoreButton.className = 'text-center mt-4 mb-4';
            loadMoreButton.innerHTML = '<button class="btn">加载更多文章</button>';
            contentDiv.appendChild(loadMoreButton);
            
            loadMoreButton.addEventListener('click', function() {
                loadMoreArticles();
            });
        }
    }
    
    // 加载更多文章
    function loadMoreArticles() {
        const nextPageStart = currentPage * itemsPerPage;
        const nextPageEnd = nextPageStart + itemsPerPage;
        
        if (postListData && nextPageStart < postListData.length) {
            currentPage++;
            const nextPageData = postListData.slice(nextPageStart, nextPageEnd);
            
            // 显示加载状态
            const loadMoreButton = document.getElementById('loadMoreBtn');
            loadMoreButton.innerHTML = '<button class="btn">加载中...</button>';
            
            // 使用setTimeout模拟异步加载
            setTimeout(() => {
                // 调用原始showList函数，但只添加不替换
                const originalInnerHTML = document.querySelector('.d-flex')?.parentElement?.innerHTML || '';
                window.showList(nextPageData);
                
                // 如果没有更多数据，隐藏按钮
                if (nextPageEnd >= postListData.length) {
                    loadMoreButton.style.display = 'none';
                } else {
                    loadMoreButton.innerHTML = '<button class="btn">加载更多文章</button>';
                }
            }, 100);
        }
    }
    
    // 显示搜索结果数量
    function showSearchResultCount(count) {
        let countElement = document.getElementById('searchResultCount');
        
        if (!countElement) {
            countElement = document.createElement('div');
            countElement.id = 'searchResultCount';
            countElement.className = 'text-center mb-4';
            countElement.style.fontSize = '14px';
            countElement.style.color = '#666';
            
            const contentDiv = document.getElementById('content');
            const firstChild = contentDiv.firstChild;
            contentDiv.insertBefore(countElement, firstChild);
        }
        
        countElement.textContent = `找到 ${count} 个搜索结果`;
    }
    
    // 添加查看更多搜索结果按钮
    function addViewMoreResultsButton(allResults) {
        let viewMoreButton = document.getElementById('viewMoreResultsBtn');
        
        if (!viewMoreButton) {
            viewMoreButton = document.createElement('div');
            viewMoreButton.id = 'viewMoreResultsBtn';
            viewMoreButton.className = 'text-center mt-4 mb-4';
            viewMoreButton.innerHTML = '<button class="btn">查看更多结果</button>';
            
            const contentDiv = document.getElementById('content');
            contentDiv.appendChild(viewMoreButton);
            
            viewMoreButton.addEventListener('click', function() {
                // 显示所有结果（分批加载）
                const contentDiv = document.getElementById('content');
                const listContainer = contentDiv.querySelector('div[style*="display:grid"]') || contentDiv.querySelector('nav + div');
                
                // 清空现有列表
                listContainer.innerHTML = '';
                
                // 分批显示结果，避免一次性创建太多DOM
                let currentIndex = 0;
                const batchSize = 500;
                
                function showNextBatch() {
                    if (currentIndex < allResults.length) {
                        const batch = allResults.slice(currentIndex, currentIndex + batchSize);
                        window.showList(batch);
                        currentIndex += batchSize;
                        
                        // 继续显示下一批
                        setTimeout(showNextBatch, 100);
                    } else {
                        // 所有结果显示完毕，隐藏按钮
                        viewMoreButton.style.display = 'none';
                    }
                }
                
                showNextBatch();
            });
        }
    }
    
    // 优化渲染性能
    function optimizeRendering() {
        // 使用requestAnimationFrame优化DOM操作
        const originalAppendChild = Element.prototype.appendChild;
        Element.prototype.appendChild = function(child) {
            if (child.nodeType === 1) { // 元素节点
                return requestAnimationFrame(() => {
                    return originalAppendChild.call(this, child);
                });
            }
            return originalAppendChild.call(this, child);
        };
    }
    
    // 启动优化
    optimizeRendering();
})();