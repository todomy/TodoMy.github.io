/**
 * 自托管访问量计数接口（Cloudflare Workers + KV）
 * 数据存在你自己的 Cloudflare 账户，不依赖任何第三方统计服务。
 *
 * 接口：
 *   GET /api/count?p=/post/xxx.html  ->  { page: 12, site: 3456 }
 *   GET /api/all                     ->  全部计数（需 Authorization: Bearer <TOKEN>）
 *
 * 部署：见同目录 wrangler.toml 与 README。
 */

const HEADERS = {
  'Content-Type': 'application/json; charset=utf-8',
  'Access-Control-Allow-Origin': '*',
  'Cache-Control': 'no-store',
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: HEADERS });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 允许前端跨域 GET
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    if (request.method !== 'GET') {
      return json({ error: 'method not allowed' }, 405);
    }

    // 计数读取/累加
    if (url.pathname === '/api/count') {
      const page = url.searchParams.get('p') || '/';
      const pageKey = 'page:' + page;
      const siteKey = 'site:total';

      try {
        const [pageVal, siteVal] = await Promise.all([
          env.COUNTER_KV.get(pageKey),
          env.COUNTER_KV.get(siteKey),
        ]);
        const pageCount = (parseInt(pageVal || '0', 10) || 0) + 1;
        const siteCount = (parseInt(siteVal || '0', 10) || 0) + 1;

        // 写入是异步后台任务，不阻塞响应
        const writes = Promise.all([
          env.COUNTER_KV.put(pageKey, String(pageCount)),
          env.COUNTER_KV.put(siteKey, String(siteCount)),
        ]);
        if (env.WAIT_UNTIL) env.WAIT_UNTIL(writes);

        return json({ page: pageCount, site: siteCount });
      } catch (e) {
        return json({ error: String(e) }, 500);
      }
    }

    // 管理接口：查看全部（需令牌）
    if (url.pathname === '/api/all') {
      const auth = request.headers.get('Authorization') || '';
      if (!env.ADMIN_TOKEN || auth !== 'Bearer ' + env.ADMIN_TOKEN) {
        return json({ error: 'unauthorized' }, 401);
      }
      const list = await env.COUNTER_KV.list({ prefix: 'page:' });
      const pages = {};
      for (const key of list.keys) {
        pages[key.name.slice(5)] = parseInt((await env.COUNTER_KV.get(key.name)) || '0', 10);
      }
      const site = parseInt((await env.COUNTER_KV.get('site:total')) || '0', 10);
      return json({ site, pages });
    }

    return json({ ok: true, service: 'TodoMy-Next counter' });
  },
};
