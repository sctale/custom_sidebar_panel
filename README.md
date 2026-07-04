# 自定义侧边栏面板 (custom_sidebar_panel)

[![home-assistant](https://img.shields.io/badge/Home-Assistant-%23049cdb)](https://www.home-assistant.io/)
[![hacs](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/sctale/panel_iframe_new)

在 Home Assistant 侧边栏添加自定义 iframe 面板，支持将任意网页嵌入到 HA 界面中。

> **2.0.0 破坏性变更**：为彻底避免与原版 `panel_iframe` 冲突，集成域名已从 `panel_iframe_new` 改为 `custom_sidebar_panel`。升级后需要删除旧面板并重新添加配置。

## 致谢

本项目基于 **[@shaonianzhentan](https://github.com/shaonianzhentan)** 的原创项目 [panel_iframe](https://github.com/shaonianzhentan/panel_iframe) 开发，感谢原作者的贡献和付出！

## 与原版的区别

原版 `panel_iframe` 是 Home Assistant 核心内置的 YAML 配置方式（通过 `panel_iframe:` 配置），已被移除。本改版改为自定义组件集成，域名 `custom_sidebar_panel` 与原版完全不同，不会产生冲突。

| 特性 | 原版 (HA 内置) | 本改版 |
|------|---------------|--------|
| 集成域名 | `panel_iframe` | `custom_sidebar_panel` |
| 配置方式 | YAML (`configuration.yaml`) | UI 配置流（设置 → 设备与服务 → 集成） |
| 多面板支持 | 一个 YAML 节点配置多个面板 | 每个面板单独添加一个集成实例 |
| 动态增删 | 修改 YAML 后需重启 HA | 无需重启，即改即生效 |
| 代理访问 | 不支持 | 支持 HTTP/HTTPS 反向代理 |
| HTTPS 兼容 | 无提示 | 自动检测并提示在新标签页打开 |
| MDI 图标预览 | 不支持 | 内置图标预览页面 |

## 功能特性

- 在 HA 侧边栏添加自定义网页面板
- 支持四种显示模式：默认、全屏、新页面、内置页面
- 支持代理访问，解决跨域问题（HTTP/HTTPS 均支持）
- 支持管理员可见设置
- 支持 WebSocket 代理
- HTTPS 环境下自动检测并提示安全限制
- 兼容 Home Assistant 2025.1+，已针对 2026.6.3 验证

## 兼容性

| HA 版本 | 最低插件版本 | 状态 |
|---------|-------------|------|
| 2025.1+ | 2.0.0 | 兼容 |
| 2026.6.3 | 2.0.0 | 推荐 |

> **注意**：HA 2026.6+ 请使用 **2.0.0 及以上版本**。

## 安装方式

### 通过 HACS 安装（推荐）

本插件不在 HACS 默认仓库中，需要先添加自定义仓库：

1. 打开 HACS → 右上角 ⋯ → 自定义仓库
2. 仓库地址填入：`https://github.com/sctale/panel_iframe_new`
3. 类别选择：**集成**
4. 点击**添加**
5. 在 HACS 中搜索「自定义侧边栏面板」或 `custom_sidebar_panel`
6. 点击**安装**
7. 重启 Home Assistant
8. 清空浏览器缓存并刷新页面

### 手动安装

1. 从 [Releases](https://github.com/sctale/panel_iframe_new/releases/latest) 下载最新源码或 zip 包
2. 将 `custom_components/custom_sidebar_panel` 目录复制到你的 Home Assistant `custom_components/` 目录下
3. 重启 Home Assistant
4. 清空浏览器缓存并刷新页面

## 升级注意事项

- 从 1.x 升级到 2.0.0 属于**破坏性更新**：集成域名已变更，升级后需要删除旧面板并重新添加
- 升级后请务必**清空浏览器缓存**或强制刷新页面（Ctrl+F5 / Cmd+Shift+R），否则前端可能继续使用旧版 JS
- 每个面板是一个独立的集成配置项

## 使用方法

### 添加面板

安装完成后，在 **设置 → 设备与服务 → 添加集成** 中搜索 `custom_sidebar_panel` 或「自定义侧边栏面板」：

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=custom_sidebar_panel)

1. 搜索并选择「自定义侧边栏面板」
2. 输入面板名称（如：Node-RED）
3. 点击提交后，在选项中配置各项参数

> **面板名称唯一性**：每个面板的名称会作为唯一标识，不支持重复名称。

### 配置项说明

| 参数 | 说明 | 示例 |
|------|------|------|
| 图标 | 侧边栏显示的 MDI 图标 | `mdi:nodejs` |
| 链接 | 要嵌入的网页地址 | `http://192.168.1.100:1880` |
| 显示模式 | 面板的展示方式 | 见下方说明 |
| 管理员可见 | 开启后仅管理员可在侧边栏看到此面板 | 开/关 |
| 代理访问 | 通过 HA 服务器代理请求，解决跨域问题 | 开/关 |

### 显示模式

| 模式 | 说明 |
|------|------|
| 默认 | 带 HA 顶部工具栏的 iframe 嵌入 |
| 全屏 | 无工具栏的全屏 iframe，适合监控大屏等场景 |
| 新页面 | 在新浏览器标签页中打开链接 |
| 内置页面 | 在 HA 内部导航到指定路径（如 `/config/dashboard`），无需 iframe |

### 链接格式支持

链接字段支持多种简写格式，会自动补全为完整 URL：

| 输入 | 解析结果 |
|------|---------|
| `http://192.168.1.100:1880` | 原样使用 |
| `1880` | `http://当前主机:1880` |
| `//192.168.1.100:1880` | `当前协议://192.168.1.100:1880`（复用当前协议，保留输入的主机） |
| `:1880/node-red/` | `当前协议://当前主机:1880/node-red/` |
| `ws://` / `wss://` | 不支持作为面板链接，WebSocket 请通过代理访问自动处理 |

### 代理访问

启用代理访问后，请求会通过 HA 服务器转发到目标内网服务，解决浏览器跨域限制：

- 代理路径根据目标 URL 自动生成
- 例如目标为 `http://192.168.1.100:1880/node-red/`，代理地址可能为 `http://HA地址:8123/node-red/`
- 代理路径以目标 URL 中的路径部分为准，具体可在 HA 日志中查看注册信息

**注意事项：**
- 代理访问适用于内网 HTTP/HTTPS 服务
- 代理会忽略 SSL 证书验证（适用于自签名证书的内网服务）
- 内置页面模式自动禁用代理
- 不了解代理原理请勿勾选此选项

### 添加多个面板

本插件支持添加多个面板，每个面板是一个独立的集成实例：

1. 重复「添加面板」步骤即可
2. 每个面板可以独立配置图标、链接、模式等
3. 在集成列表中可以修改或删除单个面板

### 更新面板

1. 进入 **设置 → 设备与服务**
2. 找到对应的面板集成，点击**配置**
3. 修改参数后点击提交，面板立即生效，无需重启

### 删除面板

1. 进入 **设置 → 设备与服务**
2. 找到对应的面板集成，点击右上角 ⋯ → **删除**
3. 面板立即从侧边栏移除

## 已知限制

- **HTTPS 混合内容**：当 HA 使用 HTTPS 时，无法在 iframe 中嵌入 HTTP 页面（浏览器安全限制），插件会自动提示在新标签页打开
- **部分网站禁止嵌入**：某些网站设置了 `X-Frame-Options` 或 `Content-Security-Policy` 头，会阻止被 iframe 嵌入
- **不支持 YAML 配置**：本改版仅支持 UI 配置流，不支持 `configuration.yaml` 方式

## 诊断与修复

### 诊断信息

1. 进入 **设置 → 设备与服务**
2. 点击对应的面板集成卡片
3. 点击右上角 ⋯ → **下载诊断**
4. 下载的文件中包含配置信息（URL 中的敏感信息会自动脱敏），可用于问题排查

### 修复建议

- 本插件不支持 YAML 配置，如需迁移请删除 `configuration.yaml` 中的旧配置节点，并通过 UI 配置流重新添加面板
- 升级后若页面行为异常，请先清空浏览器缓存并刷新页面

## 许可证

MIT License - 详见 [LICENSE](LICENSE)
