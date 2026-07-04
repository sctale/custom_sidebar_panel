"""侧边栏面板配置流程"""

from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    IconSelector,
    SelectSelector,
    SelectSelectorConfig,
    SelectOptionDict,
    TextSelector,
    TextSelectorConfig,
    BooleanSelector,
    BooleanSelectorConfig,
)

from .const import (
    DOMAIN,
    CONF_ICON,
    CONF_URL,
    CONF_MODE,
    CONF_REQUIRE_ADMIN,
    CONF_PROXY_ACCESS,
    DEFAULT_ICON,
    DEFAULT_MODE,
    DEFAULT_REQUIRE_ADMIN,
    DEFAULT_PROXY_ACCESS,
    MODE_LIST,
    MODE_BUILTIN,
    URL_ALLOWED_SCHEMES,
)

MODE_OPTIONS: list[SelectOptionDict] = [
    {"value": k, "label": v} for k, v in MODE_LIST.items()
]


def validate_url(url: str, mode: str) -> str | None:
    """验证 URL 格式，返回错误键名或 None

    ConfigFlow 和 OptionsFlow 共用此验证逻辑
    """
    # 内置页面模式：必须是 / 开头的 HA 内部路径
    if mode == MODE_BUILTIN:
        if not url.startswith("/"):
            return "invalid_builtin_url"
        return None
    # 其他模式：必须是完整 URL 或可识别的简写
    if url.startswith(URL_ALLOWED_SCHEMES):
        return None
    # 纯端口号（如 1880）
    if url.isdigit():
        return None
    # 双斜杠开头（如 //192.168.1.1:1880）
    if url.startswith("//"):
        return None
    # 冒号开头（仅支持 :端口 或 :端口/路径 的简写）
    if url.startswith(":") and len(url) > 1 and url[1:].split('/')[0].isdigit():
        return None
    return "invalid_url"


def build_schema(defaults: dict[str, Any]) -> vol.Schema:
    """构建配置表单 schema，ConfigFlow 和 OptionsFlow 共用

    参数:
        defaults: 各字段的默认值字典
    """
    return vol.Schema({
        vol.Required(CONF_ICON, default=defaults.get(CONF_ICON, DEFAULT_ICON)): IconSelector(),
        vol.Required(CONF_URL, default=defaults.get(CONF_URL, "")): TextSelector(
            TextSelectorConfig(placeholder="placeholder_url")
        ),
        vol.Required(CONF_MODE, default=defaults.get(CONF_MODE, DEFAULT_MODE)): SelectSelector(
            SelectSelectorConfig(options=MODE_OPTIONS, translation_key="mode")
        ),
        vol.Required(CONF_REQUIRE_ADMIN, default=defaults.get(CONF_REQUIRE_ADMIN, DEFAULT_REQUIRE_ADMIN)): BooleanSelector(
            BooleanSelectorConfig()
        ),
        vol.Required(CONF_PROXY_ACCESS, default=defaults.get(CONF_PROXY_ACCESS, DEFAULT_PROXY_ACCESS)): BooleanSelector(
            BooleanSelectorConfig()
        ),
    })


def process_user_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """规范化用户输入，返回处理后的参数字典

    ConfigFlow 和 OptionsFlow 共用此处理逻辑
    """
    # 规范化图标格式
    user_input[CONF_ICON] = user_input[CONF_ICON].strip().replace("mdi-", "mdi:")
    user_input[CONF_URL] = user_input[CONF_URL].strip()
    # 内置页面禁止使用代理
    if user_input[CONF_MODE] == MODE_BUILTIN:
        user_input[CONF_PROXY_ACCESS] = False
    return user_input


class PanelIframeConfigFlow(ConfigFlow, domain=DOMAIN):
    """处理配置流程 - 一步收集所有参数"""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """处理用户步骤 - 收集面板名称和所有配置参数"""
        errors: dict[str, str] = {}

        if user_input is not None:
            title = user_input.pop("title", "").strip()
            url = user_input.get(CONF_URL, "").strip()
            mode = user_input.get(CONF_MODE, DEFAULT_MODE)

            # 验证面板名称
            if not title:
                errors["title"] = "empty_title"
            # 验证 URL
            elif not url:
                errors[CONF_URL] = "empty_url"
            else:
                url_error = validate_url(url, mode)
                if url_error:
                    errors[CONF_URL] = url_error
                else:
                    # 检查是否已存在同名面板
                    await self.async_set_unique_id(title)
                    self._abort_if_unique_id_configured()

                    # 规范化输入
                    user_input = process_user_input(user_input)
                    # data 为空，所有参数放 options（可通过 OptionsFlow 修改）
                    return self.async_create_entry(title=title, data={}, options=user_input)

        # 显示包含所有字段的表单
        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=vol.Schema({
                vol.Required("title"): TextSelector(TextSelectorConfig()),
                **build_schema({}).schema,
            }),
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        """获取选项流程"""
        return PanelIframeOptionsFlow(entry)


class PanelIframeOptionsFlow(OptionsFlow):
    """处理选项流程 - 修改已有面板配置"""

    def __init__(self, entry: ConfigEntry) -> None:
        """初始化选项流程"""
        super().__init__(entry)
        self._entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """选项流程初始步骤"""
        return await self.async_step_user(user_input)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """处理选项更新"""
        errors: dict[str, str] = {}

        if user_input is not None:
            url = user_input[CONF_URL].strip()
            mode = user_input[CONF_MODE]

            # URL 不能为空
            if not url:
                errors[CONF_URL] = "empty_url"
            else:
                # 验证 URL 格式
                url_error = validate_url(url, mode)
                if url_error:
                    errors[CONF_URL] = url_error
                else:
                    # 规范化输入
                    user_input = process_user_input(user_input)
                    return self.async_create_entry(data=user_input)

        # 从当前 options 读取默认值
        options = self._entry.options
        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=build_schema(options),
        )
