(function(){
var css="#postBody{--coin:#f7b32b;--coin-dark:#d99a12;--down:var(--color-success-fg,#1a7f37);border-bottom:0;padding-bottom:8px}\n#postBody hr{height:2px;border:0;background:var(--color-border-default);margin:22px 0}\n#postBody .fl-hero-title{font-size:30px;font-weight:900;letter-spacing:6px;text-align:center;line-height:1.2;margin:10px 0 4px}\n.gm-coin{display:inline-block;color:var(--coin);font-size:38px;text-shadow:0 2px 0 var(--coin-dark);cursor:pointer;animation:gmSpin 3.2s linear infinite;transition:transform .15s;vertical-align:middle;margin-right:6px}\n.gm-coin:hover{filter:brightness(1.1)}\n.gm-coin.fly{animation:gmPop .35s ease-out}\n.gm-chart{width:min(420px,86vw);margin:6px auto 0}\n.gm-chart svg{width:100%;height:auto;display:block}\n.gm-chart polyline{fill:none;stroke:var(--down);stroke-width:3;stroke-linejoin:round;stroke-dasharray:600;stroke-dashoffset:600;animation:gmDraw 1.6s ease-out forwards}\n.gm-chart circle{fill:var(--down);opacity:0;animation:gmDrop .3s ease-out 1.5s forwards;transform:translateY(-14px)}\n#postBody .gm-status{text-align:center;font-size:19px;font-weight:600;margin:10px 0 4px}\n#postBody .fl-hero-title+p{font-size:16px;line-height:1.9;padding:14px 18px;margin:8px 0 26px;border-left:3px solid var(--coin);background:var(--color-canvas-subtle);border-radius:0 10px 10px 0}\n#postBody h2{font-size:19px;font-weight:600;margin:28px 0 14px;padding:10px 16px;border-left:4px solid var(--coin);background:var(--color-canvas-subtle);border-radius:0 8px 8px 0}\nmarkdown-accessiblity-table{display:block;width:100%;max-width:100%}\nmarkdown-accessiblity-table table{display:table !important;width:100% !important}\n#postBody table{border-collapse:collapse;width:100%;max-width:100%;margin:0 0 22px;border-radius:8px;overflow:hidden}\n#postBody th,#postBody td{border:1px solid var(--color-border-default);padding:12px 14px;line-height:1.7}\n#postBody th{background:var(--color-canvas-subtle);font-weight:600}\n#postBody.sp-about ul{list-style:none;padding:0;display:flex;gap:12px;flex-wrap:wrap;justify-content:center;margin-top:20px}\n#postBody.sp-about ul li{padding:0}\n#postBody.sp-about ul a{display:inline-block;padding:11px 26px;border-radius:8px;border:1px solid var(--color-border-default);background:var(--color-canvas-subtle);color:var(--color-accent-fg);font-size:15px;text-decoration:none;transition:all .15s}\n#postBody.sp-about ul a:hover{transform:translateY(-2px);border-color:var(--color-accent-fg)}\n.fl-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px;margin:6px 0 24px}\n.fl-card{position:relative;display:flex;align-items:center;gap:13px;padding:16px;border-radius:12px;border:1px solid var(--color-border-default);background:var(--color-canvas-subtle);text-decoration:none;color:inherit;transition:transform .15s,border-color .15s;overflow:hidden}\n.fl-card:hover{transform:translateY(-3px);border-color:var(--coin)}\n.fl-av{flex:0 0 46px;width:46px;height:46px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:19px;font-weight:600;color:#fff;user-select:none;transition:transform .15s}\n.fl-card:hover .fl-av{transform:rotate(-8deg) scale(1.06)}\n.fl-meta{min-width:0}\n.fl-name{font-size:15px;font-weight:600;line-height:1.3;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}\n.fl-desc{font-size:12px;color:var(--color-fg-muted);line-height:1.5;margin-top:3px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}\n.fl-idx{position:absolute;top:8px;right:11px;font-size:11px;color:var(--color-fg-muted);opacity:.55;font-variant-numeric:tabular-nums}\n.fl-bar{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:4px 0 26px}\n.fl-btn{padding:10px 22px;border-radius:8px;border:1px solid var(--coin);background:transparent;color:var(--coin);font-size:14px;cursor:pointer;transition:all .15s}\n.fl-btn:hover{background:var(--coin);color:#1f2328}\n#postBody .gm-disclaimer{text-align:center;font-size:12px;color:var(--color-fg-muted);margin-top:36px}\n.gm-toast{position:fixed;left:50%;bottom:40px;transform:translateX(-50%) translateY(20px);background:var(--color-fg-default);color:var(--color-canvas-default);padding:10px 22px;border-radius:99px;font-size:14px;opacity:0;pointer-events:none;transition:all .3s;z-index:9999}\n.gm-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}\n@keyframes gmSpin{0%{transform:rotateY(0)}100%{transform:rotateY(360deg)}}\n@keyframes gmPop{0%{transform:scale(1)}40%{transform:scale(1.5) rotate(-12deg)}100%{transform:scale(1)}}\n@keyframes gmDraw{to{stroke-dashoffset:0}}\n@keyframes gmDrop{to{opacity:1;transform:translateY(0)}}\n@media (prefers-reduced-motion:reduce){.gm-coin,.gm-chart polyline,.gm-chart circle{animation:none}.fl-card,.fl-av{transition:none}}";
var s=document.createElement('style');s.textContent=css;document.head.appendChild(s);

(function(){
  var b=document.getElementById('postBody');if(!b)return;
  var ps=b.querySelectorAll('p'),title,status;
  for(var i=0;i<ps.length;i++){
    var t=ps[i].textContent.trim();
    if(t.indexOf('₿')===0)title=ps[i];
    else if(t==='加载中…')status=ps[i];
    else if(t.indexOf('免责声明')===0)ps[i].className='gm-disclaimer';
  }
  var isLink=title && /LINKS|友情链接/i.test(title.textContent);
  if(title){
    title.className='fl-hero-title';
    var coin=document.createElement('span');
    coin.textContent='₿';coin.className='gm-coin';coin.title='点我试试';
    title.insertBefore(coin,title.firstChild);
    var toast=document.createElement('div');toast.className='gm-toast';b.appendChild(toast);
    var tid;
    coin.addEventListener('click',function(){
      coin.classList.remove('fly');void coin.offsetWidth;coin.classList.add('fly');
      toast.textContent=isLink?'加友链？在 Issue 里添一行 - [名字](链接) 简介 就行':'欢迎来到关于页，点个 star 支持一下';
      toast.classList.add('show');
      clearTimeout(tid);tid=setTimeout(function(){toast.classList.remove('show')},2600);
    });
  }
  if(status){
    // 友链页的 status 在下方会写入「已连接 N 位朋友」，随机文案只对关于页生效
    var aboutLines=['长期主义，慢慢变富','独立思考，持续上涨','欢迎价值投资者长期持有','本金有限，耐心无限','今天也在认真生活'];
    if(!isLink){status.textContent=aboutLines[Math.floor(Math.random()*aboutLines.length)];}
    status.className='gm-status';
    var wrap=document.createElement('div');wrap.className='gm-chart';
    wrap.innerHTML="<svg viewBox='0 0 420 90'><polyline points='10,72 60,66 100,70 140,56 180,60 225,44 270,48 320,30 370,26 410,14'/><circle cx='410' cy='14' r='5'/></svg>";
    b.insertBefore(wrap,status);
  }
  b.className+=(isLink?' sp-link':' sp-about');
  if(!isLink)return;
  var ul=b.querySelector('ul');if(!ul)return;
  var items=[],lis=ul.querySelectorAll('li');
  for(var j=0;j<lis.length;j++){
    var a=lis[j].querySelector('a');if(!a)continue;
    var name=a.textContent.trim(),url=a.getAttribute('href');
    var full=lis[j].textContent.trim();
    var desc=full.replace(name,'').replace(/^[\s—\-\|·:：]+/,'').trim();
    if(!desc)desc='一个值得常去的地方';
    items.push({name:name,url:url,desc:desc});
  }
  if(!items.length)return;
  var palette=['#c99a10','#1a7f37','#2f6fb0','#6a56b0','#b0456a','#0f6e56','#a8651a','#8a3d3d'];
  function hash(s){var h=0;for(var k=0;k<s.length;k++){h=(h*31+s.charCodeAt(k))|0;}return Math.abs(h);}
  function firstChar(s){s=s.trim();return s?s.charAt(0).toUpperCase():'?';}
  var grid=document.createElement('div');grid.className='fl-grid';
  items.forEach(function(it,idx){
    var card=document.createElement('a');card.className='fl-card';card.href=it.url;
    card.target='_blank';card.rel='noopener noreferrer';
    var av=document.createElement('span');av.className='fl-av';
    av.textContent=firstChar(it.name);av.style.background=palette[hash(it.name)%palette.length];
    var meta=document.createElement('span');meta.className='fl-meta';
    var nm=document.createElement('span');nm.className='fl-name';nm.textContent=it.name;
    var ds=document.createElement('span');ds.className='fl-desc';ds.textContent=it.desc;
    meta.appendChild(nm);meta.appendChild(ds);card.appendChild(av);card.appendChild(meta);
    var ix=document.createElement('span');ix.className='fl-idx';
    ix.textContent=String(idx+1).padStart(3,'0');card.appendChild(ix);
    grid.appendChild(card);
  });
  ul.style.display='none';
  ul.parentNode.insertBefore(grid,ul);
  var bar=document.createElement('div');bar.className='fl-bar';
  var rnd=document.createElement('button');rnd.className='fl-btn';rnd.type='button';
  rnd.textContent='随便串一家';
  rnd.addEventListener('click',function(){
    var pick=items[Math.floor(Math.random()*items.length)];
    window.open(pick.url,'_blank','noopener,noreferrer');
  });
  bar.appendChild(rnd);grid.parentNode.insertBefore(bar,grid.nextSibling);
  if(status){status.textContent='已连接 '+items.length+' 位朋友';}
})();

})();
