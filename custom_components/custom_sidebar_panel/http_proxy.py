"""HTTP 代理模块 - 处理跨域请求和 WebSocket 代理"""

import asyncio
import logging
from urllib.parse import urlparse

import aiohttp
from aiohttp import web

_LOGGER = logging.getLogger(__name__)

# 代理请求超时（秒）
PROXY_TIMEOUT = aiohttp.ClientTimeout(total=30)

# 最大请求体大小（10MB）
MAX_REQUEST_BODY = 10 * 1024 * 1024

# 代理请求时过滤的请求头
FILTERED_REQUEST_HEADERS = frozenset({
    'host', 'transfer-encoding', 'cookie', 'authorization',
    'connection', 'content-length', 'upgrade', 'proxy-connection',
    'expect', 'keep-alive', 'proxy-authorization',
    'x-forwarded-for', 'x-forwarded-host', 'x-forwarded-proto',
    'x-forwarded-port', 'x-real-ip',
})

# 代理响应时过滤的响应头
FILTERED_RESPONSE_HEADERS = frozenset({
    'transfer-encoding', 'set-cookie', 'connection', 'keep-alive',
})

# 跳过响应体的状态码（304 Not Modified 等）
NO_BODY_STATUS_CODES = frozenset({204, 304})


class HttpProxy:
    """HTTP 反向代理，用于在 HA 内访问外部页面"""

    # 类级别 ClientSession，跨请求复用
    _session: aiohttp.ClientSession | None = None
    _connector: aiohttp.TCPConnector | None = None

    def __init__(self, url: str):
        parsed_url = urlparse(url)
        route_path = parsed_url.path.strip('/')

        if route_path == '':
            route_path = parsed_url.netloc.replace(':', '').replace('.', '')
            self.is_root = True
        else:
            self.is_root = False

        self.proxy_scheme = parsed_url.scheme or 'http'
        self.proxy_host = parsed_url.netloc
        self.proxy_path = route_path
        self._route: web.Resource | None = None

    @classmethod
    def _get_session(cls) -> aiohttp.ClientSession:
        """获取或创建复用的 ClientSession（带连接池限制）"""
        if cls._session is None or cls._session.closed:
            # 连接池限制：最多 100 个连接，每个 host 最多 30 个
            cls._connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                enable_cleanup_closed=True,
            )
            cls._session = aiohttp.ClientSession(
                timeout=PROXY_TIMEOUT,
                connector=cls._connector,
            )
        return cls._session

    @classmethod
    async def cleanup(cls) -> None:
        """清理 ClientSession 和 Connector（集成卸载时调用）"""
        if cls._session and not cls._session.closed:
            await cls._session.close()
            cls._session = None
        if cls._connector and not cls._connector.closed:
            await cls._connector.close()
            cls._connector = None
        _LOGGER.debug("代理 ClientSession 和 Connector 已关闭")

    def register(self, router: web.UrlDispatcher) -> None:
        """注册路由（如果路由已存在则跳过）"""
        route_url = f'/{self.proxy_path}/'
        # 检查路由是否已注册（精确匹配，避免子串误匹配）
        target_path = route_url.rstrip('/')
        for resource in router.resources():
            resource_path = ''
            if hasattr(resource, 'canonical'):
                resource_path = resource.canonical
            elif hasattr(resource, 'get_info'):
                info = resource.get_info()
                resource_path = info.get('path', '') if isinstance(info, dict) else str(info)
            # aiohttp 动态路由的 canonical 形如 /path/{tail:.*}
            if resource_path.rstrip('/') == target_path:
                _LOGGER.debug("代理路由已存在，跳过注册: %s", route_url)
                return
        self._route = router.add_route('*', route_url + '{tail:.*}', self.handler)
        _LOGGER.debug("代理路由已注册: %s", route_url)

    def unregister(self, router: web.UrlDispatcher) -> None:
        """注销路由"""
        if self._route is not None:
            router.remove_resource(self._route)
            self._route = None
            _LOGGER.debug("代理路由已注销: %s", self.proxy_path)

    def get_url(self, hostname: str = '') -> str:
        """获取访问地址"""
        return f'{hostname}/{self.proxy_path}/'

    def get_path(self, request: web.Request) -> str:
        """获取真实路径地址"""
        url_path = request.rel_url.path
        if self.is_root:
            url_path = url_path.replace(f'/{self.proxy_path}', '')
        return url_path

    @property
    def _ws_scheme(self) -> str:
        """根据代理协议返回 WebSocket 协议"""
        return 'wss' if self.proxy_scheme == 'https' else 'ws'

    async def handler(self, request: web.Request) -> web.StreamResponse:
        """请求处理器"""
        target_ws = f'{self._ws_scheme}://{self.proxy_host}'
        target_http = f'{self.proxy_scheme}://{self.proxy_host}'
        if request.headers.get('Upgrade', '').lower() == 'websocket':
            return await self.websocket_handler(request, target_ws)
        return await self.http_handler(request, target_http)

    async def http_handler(self, request: web.Request, target_url: str) -> web.Response:
        """HTTP 请求代理"""
        target = target_url + self.get_path(request)
        if request.query_string:
            target += '?' + request.query_string

        # 请求体大小限制
        body = await request.read()
        if len(body) > MAX_REQUEST_BODY:
            _LOGGER.warning("代理请求体过大: %d bytes (限制 %d)", len(body), MAX_REQUEST_BODY)
            return web.Response(
                status=413,
                text="请求体过大",
                content_type="text/plain",
            )

        session = self._get_session()
        try:
            async with session.request(
                method=request.method,
                url=target,
                headers={k: v for k, v in request.headers.items()
                         if k.lower() not in FILTERED_REQUEST_HEADERS},
                data=body,
                ssl=False,  # 允许自签名证书的内网服务
            ) as resp:
                headers = {k: v for k, v in resp.headers.items()
                           if k.lower() not in FILTERED_RESPONSE_HEADERS}
                # 无响应体的状态码
                if resp.status in NO_BODY_STATUS_CODES:
                    return web.Response(status=resp.status, headers=headers)
                response_body = await resp.read()
                return web.Response(body=response_body, status=resp.status, headers=headers)
        except aiohttp.ClientError as err:
            _LOGGER.warning("代理请求失败 %s: %s", target, err)
            return web.Response(
                status=502,
                text=f"代理请求失败: {err}",
                content_type="text/plain",
            )
        except asyncio.TimeoutError:
            _LOGGER.warning("代理请求超时 %s", target)
            return web.Response(
                status=504,
                text="代理请求超时",
                content_type="text/plain",
            )

    async def websocket_handler(self, request: web.Request, target_url: str) -> web.WebSocketResponse:
        """WebSocket 代理"""
        ws_server = web.WebSocketResponse()
        await ws_server.prepare(request)

        target = target_url + self.get_path(request)
        session = self._get_session()
        try:
            async with session.ws_connect(target) as ws_client:
                async def ws_forward(ws_from: aiohttp.ClientWebSocketResponse | web.WebSocketResponse,
                                     ws_to: aiohttp.ClientWebSocketResponse | web.WebSocketResponse) -> None:
                    async for msg in ws_from:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await ws_to.send_str(msg.data)
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            await ws_to.send_bytes(msg.data)
                        elif msg.type == aiohttp.WSMsgType.CLOSE:
                            await ws_to.close(code=msg.data, message=b'')
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            _LOGGER.debug("WebSocket 错误: %s", ws_from.exception())
                            await ws_to.close()

                await asyncio.gather(
                    ws_forward(ws_server, ws_client),
                    ws_forward(ws_client, ws_server)
                )
        except aiohttp.ClientError as err:
            _LOGGER.warning("WebSocket 代理连接失败 %s: %s", target, err)
        except Exception as err:
            _LOGGER.warning("WebSocket 代理异常 %s: %s", target, err)

        return ws_server
