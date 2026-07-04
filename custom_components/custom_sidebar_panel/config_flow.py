"""侧边栏面板配置流程"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    IconSelector,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    TextSelector,
)

from .const import (
    CONF_ICON,
    CONF_MODE,
    CONF_PROXY_ACCESS,
    CONF_REQUIRE_ADMIN,
    CONF_URL,
    DEFAULT_ICON,
    DEFAULT_MODE,
    DEFAULT_PROXY_ACCESS,
    DEFAULT_REQUIRE_ADMIN,
    DOMAIN,
    MODE_BUILTIN,
    MODE_LIST,
    URL_ALLOWED_SCHEMES,
)

# 显示模式下拉选项
MODE_OPTIONS: list[SelectOptionDict] = [
    {"value": k, "label": v} for k, v in MODE_LIST.items()
]


def _validate_url(url: str, mode: str) -> str | None:
    """验证 URL 格式，返回错误键名或 None"""
    if mode == MODE_BUILTIN:
        if not url.startswith("/"):
            return "invalid_builtin_url"
        return None
    if url.startswith(URL_ALLOWED_SCHEMES):
        return None
    if url.isdigit():
        return None
    if url.startswith("//"):
        return None
    if url.startswith(":") and len(url) > 1 and url[1:].split("/")[0].isdigit():
        return None
    return "invalid_url"


def _process_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """规范化用户输入"""
    user_input[CONF_ICON] = user_input[CONF_ICON].strip().replace("mdi-", "mdi:")
    user_input[CONF_URL] = user_input[CONF_URL].strip()
    if user_input[CONF_MODE] == MODE_BUILTIN:
        user_input[CONF_PROXY_ACCESS] = False
    return user_input


def _build_schema(defaults: dict[str, Any], include_title: bool = False) -> vol.Schema:
    """构建表单 schema（ConfigFlow 与 OptionsFlow 共享）

    placeholder 由翻译文件 strings.json 的 placeholders 字段提供，
    不通过 TextSelectorConfig 传递（TextSelectorConfig 不支持 placeholder 参数）。
    """
    fields: dict[vol.Required, Any] = {}
    if include_title:
        fields[
            vol.Required("title", default=defaults.get("title", ""))
        ] = TextSelector()
    fields.update(
        {
            vol.Required(
                CONF_ICON, default=defaults.get(CONF_ICON, DEFAULT_ICON)
            ): IconSelector(),
            vol.Required(
                CONF_URL, default=defaults.get(CONF_URL, "")
            ): TextSelector(),
            vol.Required(
                CONF_MODE, default=defaults.get(CONF_MODE, DEFAULT_MODE)
            ): SelectSelector(
                SelectSelectorConfig(options=MODE_OPTIONS, translation_key="mode")
            ),
            vol.Required(
                CONF_REQUIRE_ADMIN,
                default=defaults.get(CONF_REQUIRE_ADMIN, DEFAULT_REQUIRE_ADMIN),
            ): BooleanSelector(),
            vol.Required(
                CONF_PROXY_ACCESS,
                default=defaults.get(CONF_PROXY_ACCESS, DEFAULT_PROXY_ACCESS),
            ): BooleanSelector(),
        }
    )
    return vol.Schema(fields)


class PanelIframeConfigFlow(ConfigFlow, domain=DOMAIN):
    """处理配置流程 - 一步收集所有参数"""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """处理用户步骤 - 收集面板名称和所有配置参数"""
        errors: dict[str, str] = {}

        if user_input is not None:
            title = user_input.get("title", "").strip()
            url = user_input.get(CONF_URL, "").strip()
            mode = user_input.get(CONF_MODE, DEFAULT_MODE)

            if not title:
                errors["title"] = "empty_title"
            if not url:
                errors[CONF_URL] = "empty_url"

            if not errors:
                url_error = _validate_url(url, mode)
                if url_error:
                    errors[CONF_URL] = url_error

            if not errors:
                await self.async_set_unique_id(title)
                self._abort_if_unique_id_configured()

                options = {k: v for k, v in user_input.items() if k != "title"}
                options = _process_input(options)
                return self.async_create_entry(title=title, data={}, options=options)

        # 构建表单 schema，使用 default 预填（最兼容方式）
        defaults = user_input if user_input is not None else {}
        schema = _build_schema(defaults, include_title=True)

        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=schema,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """获取选项流程"""
        return PanelIframeOptionsFlow()


class PanelIframeOptionsFlow(OptionsFlow):
    """处理选项流程 - 修改已有面板配置"""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """管理选项"""
        errors: dict[str, str] = {}

        if user_input is not None:
            url = user_input.get(CONF_URL, "").strip()
            mode = user_input.get(CONF_MODE, DEFAULT_MODE)

            if not url:
                errors[CONF_URL] = "empty_url"
            else:
                url_error = _validate_url(url, mode)
                if url_error:
                    errors[CONF_URL] = url_error

            if not errors:
                user_input = _process_input(user_input)
                return self.async_create_entry(data=user_input)

        # 从当前 options 读取默认值（最兼容方式）
        schema = _build_schema(dict(self.config_entry.options), include_title=False)

        return self.async_show_form(
            step_id="init",
            errors=errors,
            data_schema=schema,
        )
