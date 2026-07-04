# Changelog

## 2.0.2 (2026-07-01)

### 修复
- 修复 HACS 下载时报 "unknown error" 的问题
  - `hacs.json` 中 `zip_release` 被错误配置为 URL 字符串（应为布尔值）
  - HACS 解析时 `filename` 为 None，触发 `AttributeError` 被吞掉，显示为 unknown error
  - 该 URL 还指向旧仓库 `sctale/panel_iframe_new`（改名时遗漏）
  - 移除 `zip_release` 字段，改用 HACS 默认的源码 archive 下载方式
- 修复 `manifest.json` 中 `documentation` 和 `issue_tracker` 仍指向旧仓库 `sctale/panel_iframe_new` 的问题

## 2.0.1 (2026-07-01)

### 修复
- 移除 `manifest.json` `codeowners` 中的原作者 `@shaonianzhentan`，仅保留当前维护者 `@sctale`
  - HACS 解析 manifest 时会将 `codeowners` 存为 `data.authors` 用于 UI 展示
  - 原作者仍存在会导致 HACS 列表中新仓库的作者与原版 `panel_iframe` 相同，造成"合并"观感

## 2.0.0 (2026-06-19)

### 破坏性变更
- 为彻底避免与原版 `panel_iframe` 的 HACS 冲突，集成域名从 `panel_iframe_new` 改为 `custom_sidebar_panel`
- 目录从 `custom_components/panel_iframe_new` 改为 `custom_components/custom_sidebar_panel`
- 静态资源路径从 `/panel_iframe_new_www` 改为 `/custom_sidebar_panel_www`
- 前端组件名从 `ha-panel_iframe_new` 改为 `ha-custom-sidebar-panel`
- JS 文件从 `panel_iframe_new.js` 改为 `custom_sidebar_panel.js`
- manifest `name` 从「侧边栏面板」改为「自定义侧边栏面板」
- 1.x 用户升级后需要删除旧面板并重新添加配置

### 变更
- 版本号从 1.0.1 升级至 2.0.0（主版本号 +1）
- 更新所有代码、配置、翻译、文档中的域名引用
- manifest codeowners 中 `@Sid` 修正为 `@sctale`

## 1.0.1 (2026-06-19)

### 修复
- 修复 `config_flow.py` 中 `VERSION = 2` 未重置为新 domain 初始版本的问题，改为 `VERSION = 1`
- 修复 `URL_ALLOWED_SCHEMES` 包含 `ws://`/`wss://` 但代理和 iframe 均不支持的问题
- 修复 `http_proxy.py` 中路由匹配使用子串判断导致误匹配的问题，改为精确匹配
- 修复代理路由在面板删除/卸载时未注销的问题，新增 `unregister` 方法并在卸载时调用
- 修复 `__init__.py` 卸载时未清理 `STATIC_PATH_KEY` 的问题
- 修复默认模式仍通过 `index.html` 中转导致多一次请求的问题，改为 iframe 直接嵌入
- 修复 `window.open` features 参数包含不标准 `noopener` 的问题
- 修复冒号开头 URL 简写验证过宽的安全问题，限制为仅 `:端口` 或 `:端口/路径`

### 优化
- `__init__.py` 中 `async_setup` 参数类型改为 `ConfigType`
- `__init__.py` 中静态资源路径改为使用 `os.path.dirname(__file__)` 相对定位
- 提取 `STATIC_URL_PATH` 常量，避免硬编码
- `async_get_options_flow` 和 `http_proxy.py` 多个方法补充类型注解
- 增强代理请求头过滤，新增 `x-forwarded-*`、`x-real-ip` 等转发头过滤
- `diagnostics.py` 中 `urlparse` 导入移至顶部，并抽取 `_mask_credentials` 函数
- 移除未使用的 `PLATFORMS` 常量和空的 `services.yaml`
- 移除不再使用的 `www/index.html` 中转页

### 文档
- 更新 README.md 兼容性说明和链接格式支持表

## 1.0.0 (2026-06-19)

### 破坏性变更
- Home Assistant 集成域名从 `panel_iframe` 变更为 `panel_iframe_new`
- 静态资源路径从 `/panel_iframe_www` 变更为 `/panel_iframe_new_www`
- 前端组件名称从 `ha-panel_iframe` 变更为 `ha-panel_iframe_new`
- 旧版本用户升级后需要删除旧面板并重新添加配置

### 变更
- 版本号从 0.3.6 升级至 1.0.0（主版本号 +1）
- 更新 `manifest.json`、`package.json`、`hacs.json` 中的域名和版本号
- 更新 README.md 中所有相关引用和安装说明

## 0.3.6 (2026-06-19)

### 修复
- 修复 `panel_iframe.js` 中双斜杠 URL 简写（如 `//192.168.1.100:1880`）解析错误的问题，现在会复用当前协议并保留输入的主机
- 修正 README.md 中的多处描述错误

### 文档
- 重写 README.md，修正 badge 文本、原版说明、链接格式解析表、代理访问说明
- 新增「升级注意事项」章节，强调升级后需清空浏览器缓存
- 新增「兼容性」说明，明确 HA 2026.6+ 推荐使用 0.3.6+
- 新增面板名称唯一性提示

## 0.3.5 (2026-06-19)

### 修复
- 修复 `config_flow.py` 中 `OptionsFlow.__init__()` 未传递 `entry` 参数的问题，兼容 HA 2026.6+ 的选项流程 API
- 修复 `panel_iframe.js` 中 `location-changed` 等事件使用 `Event` 构造函数导致 `detail` 丢失的问题，改用 `CustomEvent`
- 修复 `panel_iframe.js` 中 `narrow` 属性变化时重新渲染整个 iframe 的问题，改为仅更新 narrow 相关样式
- 修复 `panel_iframe.js` 中相同配置下重复渲染导致 iframe 重新加载的问题，增加渲染缓存 key
- 修复 `http_proxy.py` 中代理路由重复注册判断依赖 `canonical` 属性的兼容性问题
- 修复 `http_proxy.py` 中 WebSocket 代理在 `finally` 块中 `return` 的语法警告问题

### 安全
- 增强 `http_proxy.py` 代理请求头过滤，新增 `upgrade`、`proxy-connection`、`expect`、`proxy-authorization` 等敏感头
- 增强 `http_proxy.py` 代理响应头过滤，新增 `connection`、`keep-alive` 头

## 0.3.4 (2026-06-19)

### 新增
- `panel_iframe.js` 添加 `connectedCallback` 生命周期方法，仅在组件已连接 DOM 时渲染
- `__init__.py` 添加 `async_reload_entry` 方法（HA 2025.1+ 标准）
- `index.html` 添加 CSP meta 标签
- README 新增「诊断与修复」章节

### 变更
- `panel_iframe.js` 新页面模式改为直接 `window.open()` 打开新标签页，不再经过 index.html 中间跳转
- `panel_iframe.js` `set panel` 和 `set narrow` 添加 `isConnected` 检查，避免未挂载时渲染

### 性能
- 新页面模式减少一次中间页面跳转，打开速度更快

## 0.3.3 (2026-06-19)

### 新增
- 添加 `diagnostics.py` 诊断支持，允许用户下载集成诊断信息（URL 自动脱敏）
- 添加 `repair_issues` 支持：YAML 配置弃用时在 HA 修复页面显示警告
- `manifest.json` 添加 `loggers` 字段（HA 标准要求）
- `async_migrate_entry` 实现版本迁移逻辑（版本 1 → 2）
- 翻译文件添加 `issues` 翻译（YAML 弃用警告）

### 变更
- `ConfigFlow.VERSION` 从 1 升级到 2
- `async_setup` 检测 YAML 配置时创建修复建议 issue

## 0.3.2 (2026-06-19)

### 新增
- 代理模块使用 `TCPConnector` 配置连接池（最多 100 连接，每 host 最多 30 连接）
- 代理请求体大小限制（10MB），超出返回 413 错误
- 代理响应处理 204/304 等无响应体状态码
- WebSocket 代理传递 close code，添加 ERROR 消息类型处理
- `__init__.py` 代理实例存储到 `hass.data`，支持多面板独立代理管理
- `__init__.py` 仅在所有代理移除后才关闭共享 ClientSession

### 变更
- `HttpProxy.cleanup()` 同时关闭 Connector 和 ClientSession
- `async_remove_entry` 改为按面板清理代理，而非全局清理

## 0.3.1 (2026-06-19)

### 安全
- iframe 添加 `sandbox` 属性限制权限（allow-scripts/allow-same-origin/allow-forms/allow-popups 等）
- iframe 添加 `referrerpolicy="no-referrer"` 防止 Referer 信息泄露

### 新增
- iframe 添加 `loading="lazy"` 延迟加载属性
- iframe 加载超时处理（30秒），超时显示提示信息
- 全屏模式添加刷新按钮（右下角浮动按钮）
- 默认模式工具栏添加刷新按钮
- `disconnectedCallback()` 生命周期方法，清理加载超时定时器
- `_getSandbox()` 方法统一管理 iframe sandbox 权限

### 变更
- 全屏模式移动端菜单按钮与刷新按钮合并到同一浮动按钮容器
- 默认模式加载状态改为纵向排列（spinner + 文字 + 超时提示）

## 0.3.0 (2026-06-19)

### 新增
- 配置流程添加 URL 格式验证：支持 http/https/ws/wss 协议、端口号、双斜杠和冒号开头的简写格式
- 内置页面模式验证 URL 必须以 `/` 开头
- URL 输入框添加 placeholder 提示（`http://192.168.1.100:1880`）
- `const.py` 添加 `URL_ALLOWED_SCHEMES` 常量
- 翻译文件添加 `invalid_url` 和 `invalid_builtin_url` 错误消息

### 变更
- 配置流程内置页面模式判断从硬编码 `"3"` 改为使用 `MODE_BUILTIN` 常量
- `config_flow.py` 提取 URL 验证逻辑为独立方法 `_validate_url()`

## 0.2.9 (2026-06-19)

### 变更
- 移除 `__init__.py` 中未使用的 `ServiceCall` 导入
- `config_flow.py` `async_get_options_flow` 添加 `entry: ConfigEntry` 类型注解
- `const.py` `PLATFORMS` 类型从 `list` 改为 `list[str]`
- README 新增「更新面板」和「删除面板」操作说明

## 0.2.8 (2026-06-19)

### 新增
- `__init__.py` 添加 `async_setup` 入口函数（HA 标准要求）
- `__init__.py` 添加 `async_migrate_entry` 配置项版本迁移方法
- `manifest.json` 添加 `iot_class: "local_push"` 字段
- `services.yaml` 空服务定义文件（HA 标准要求）

### 变更
- `manifest.json` `documentation` URL 从原作者仓库改为当前仓库 `sctale/panel_iframe`

## 0.2.7 (2026-06-19)

### 安全
- 代理请求过滤更多敏感请求头（`cookie`、`authorization`、`connection`、`content-length`）
- 代理响应过滤 `set-cookie` 头，防止代理目标设置 HA 域的 cookie

### 新增
- 代理路由注册前检查是否已存在，避免重复注册
- WebSocket 代理协议跟随代理目标协议（HTTPS 目标使用 `wss://`）
- `_ws_scheme` 属性自动根据 `proxy_scheme` 返回正确的 WebSocket 协议

### 变更
- 请求头和响应头过滤改用 `frozenset` 常量（`FILTERED_REQUEST_HEADERS`、`FILTERED_RESPONSE_HEADERS`）

## 0.2.6 (2026-06-19)

### 安全
- `panel_iframe.js` 添加 `_escapeHtml()` 方法，对 title 和 url 进行 HTML 转义防止 XSS
- `index.html` 外部链接添加 `rel="noreferrer noopener"` 防止 `window.opener` 攻击

### 新增
- `panel_iframe.js` iframe 添加 `title` 属性（无障碍访问）
- `panel_iframe.js` 添加 ARIA 属性：`role="banner"`（工具栏）、`role="alert"`（警告）、`role="status"`（加载状态）、`aria-hidden`（装饰元素）、`aria-label`（导航按钮）
- `index.html` 添加 `role="status"`、`role="button"`、`tabindex`、`aria-label` 等无障碍属性
- `index.html` 添加键盘事件支持（Enter 键打开链接）
- `index.html` 添加 `<meta http-equiv="X-UA-Compatible">` 兼容性标签
- `index.html` 添加 `'use strict'` 严格模式

### 变更
- `panel_iframe.js` mode 比较从 `==` 改为 `===`（严格比较）
- `panel_iframe.js` 内置页面模式使用 `config.url` 原始路径（不经过 URL 规范化）
- `panel_iframe.js` iframe 加载状态改用 `.iframe-wrapper` 包裹层 + CSS `~` 兄弟选择器，修复之前 `+` 选择器不生效的问题

## 0.2.5 (2026-06-19)

### 新增
- `__init__.py` 添加 `_LOGGER` 日志记录器，记录面板添加/移除/更新/代理注册等关键操作
- `http_proxy.py` 添加 `_LOGGER` 日志记录器，记录代理请求失败和超时
- `http_proxy.py` 添加代理请求异常处理：`ClientError` 返回 502、`TimeoutError` 返回 504
- `http_proxy.py` 添加 WebSocket 代理连接失败的异常捕获
- `http_proxy.py` 添加请求超时配置 `PROXY_TIMEOUT`（30秒）
- `const.py` 添加 `PLATFORMS` 常量（HA 标准）
- `hacs.json` 添加 `zip_release` 配置
- `manifest.json` codeowners 添加 `@Sid`

### 变更
- `config_flow.py` `OptionsFlow.__init__` 添加类型注解 `entry: ConfigEntry` -> `None`
- `http_proxy.py` ClientSession 创建时传入 `timeout=PROXY_TIMEOUT`

## 0.2.4 (2026-06-19)

### 新增
- 配置流程添加面板名称唯一性检查，防止重复添加同名面板
- 配置流程添加输入验证：面板名称不能为空、链接地址不能为空
- strings.json 和翻译文件添加错误消息翻译（`empty_title`、`empty_url`、`already_configured`）

### 变更
- 移除 `config_flow.py` 中未使用的 `section` 导入
- 配置流程使用 `async_set_unique_id` + `_abort_if_unique_id_configured` 替代手动检查

## 0.2.3 (2026-06-19)

### 变更
- `http_proxy.py` ClientSession 改为类级别复用，避免每次请求创建新连接
- `http_proxy.py` 新增 `cleanup()` 方法，集成卸载时正确关闭 session
- `__init__.py` 使用 `hass.data` 替代全局变量存储静态路径注册状态
- `__init__.py` 新增 `async_remove_entry` 钩子，移除配置项时清理代理资源
- `__init__.py` 使用 `const.py` 常量替代硬编码配置键名

## 0.2.2 (2026-06-19)

### 新增
- 前端面板组件添加 iframe 加载状态指示（spinner + 文字提示）
- 前端面板组件拆分为独立渲染方法（`_renderDefault`/`_renderFullscreen`/`_renderHttpsWarning`），代码更清晰
- URL 处理逻辑提取为 `_normalizeUrl` 方法，更健壮
- HTTPS 安全提示页面优化：添加警告图标、圆角按钮、更好的视觉层次
- 全屏模式移动端导航按钮改用原生 `<button>` + 圆角阴影样式

### 变更
- `index.html` 重写：使用 IIFE 避免全局污染、添加 URL 解析错误处理、优化加载动画样式
- `panel_iframe.js` 使用 HA CSS 变量（`--divider-color`、`--secondary-text-color`、`--card-background-color` 等）替代硬编码颜色
- `panel_iframe.js` iframe 加载完成后才显示，之前是直接显示空白 iframe

## 0.2.1 (2026-06-19)

### 新增
- 新增 `const.py` 集中管理常量（DOMAIN、配置键名、默认值、模式列表）
- 新增 `strings.json` 标准 HA 翻译源文件（含 `data_description` 和 `selector` 翻译）
- 配置流程使用 HA Selectors（IconSelector、TextSelector、SelectSelector、BooleanSelector），UI 体验大幅提升
- 下拉选择模式替代原来的 vol.In，每个选项带详细描述
- 图标字段使用 IconSelector，提供图标选择器 UI
- 链接字段使用 TextSelector，提供文本输入 UI

### 变更
- 移除 `manifest.py`，改用 `const.py` + 直接读取 `manifest.json`，避免模块级实例化问题
- `config_flow.py` 使用 `ConfigFlowResult` 替代 `FlowResult`（HA 2026 新命名）
- `__init__.py` 使用 `entry.version` 替代 `manifest.VERSION` 作为缓存版本号
- `__init__.py` 从 `const.py` 导入 `DOMAIN`，不再依赖 `manifest.py`
- 翻译文件增加 `data_description` 字段，为每个配置项提供详细说明
- 翻译文件增加 `selector` 翻译，支持下拉选择模式的本地化描述

## 0.2.0 (2026-06-19)

### 新增
- 代理访问支持 HTTPS 目标站点（自动识别 URL 协议）
- 代理请求忽略 SSL 证书验证（适配自签名证书的内网服务）
- README 新增「与原版的区别」对比表
- README 新增「链接格式支持」说明
- README 新增「添加多个面板」说明
- README 新增「已知限制」章节

### 变更
- JS 面板组件修复 Shadow DOM 内 `ha-menu-button` 属性绑定问题（改用 JS 手动设置属性）
- 静态资源路径注册改为仅注册一次，避免多面板时报错
- 移除 `update_listener` 中的 `asyncio.sleep(1)`，选项更新更即时
- 移除 `config_flow.py` 中未使用的 `cv` 导入
- `package.json` 清理：移除 gitee 仓库引用、修正描述、更新版本号
- 删除过时的 Windows 批处理脚本 `build.cmd`，MDI 更新改为 npm script

### 修复
- 修复多面板场景下静态路径重复注册可能报错的问题
- 修复 Shadow DOM 内 HA 自定义元素属性无法正确传递的问题
- 修复 `http_proxy.py` 代理请求转发时未过滤 `transfer-encoding` 请求头的问题

## 0.1.0 (2026-06-19)

### 新增
- 添加 `integration_type: "service"` 到 manifest.json（HA 2026 必填项）
- 添加 `panel_custom` 到 manifest.json 依赖项
- 添加 `issue_tracker` 到 manifest.json
- 添加中文翻译文件 (zh-CN.json)
- HTTPS 环境下嵌入 HTTP 页面时显示友好提示和新标签页链接

### 变更
- manifest.json `quality_scale` 从 `internal` 改为 `bronze`（`internal` 仅适用于核心集成）
- manifest.json `documentation` 从本地路径改为 GitHub 仓库 URL
- 最低 HA 版本要求从 2024.7.0 提升至 2025.1.0
- JS 面板组件从依赖 `ha-panel-lovelace` LitElement 继承改为独立 HTMLElement + Shadow DOM（更稳定，不受 HA 内部变更影响）
- manifest.py 从使用 `homeassistant.util.json.load_json` 改为标准 `json` 模块（避免 HA 内部 API 变更影响）
- 代码风格优化：添加文档字符串、类型注解、移除未使用的变量

### 修复
- 修复 config_flow.py 中未使用的 `errors` 变量
- 修复 manifest.py 中路径拼接使用 f-string 的问题（改用 `os.path.join`）

## 2026.4.13

- 初始版本
