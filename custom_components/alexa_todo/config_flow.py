"""
Config flow for the Alexa ToDo integration.

ATTRIBUTION: The code of this class is mainly taken from the Alexa Device integration
which is licensed under the Apache License Version 2.0.
It has been slightly modified to fit the needs of this integration.
Original code: https://github.com/home-assistant/core/blob/dev/homeassistant/components/alexa_devices/config_flow.py
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from aioamazondevices.api import AmazonEchoApi
from aioamazondevices.exceptions import (
    CannotAuthenticate,
    CannotConnect,
    CannotRetrieveData,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_CODE, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import aiohttp_client

from .const import CONF_LOGIN_DATA, DOMAIN

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.core import HomeAssistant

STEP_REAUTH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_CODE): cv.string,
    }
)
STEP_RECONFIGURE = vol.Schema(
    {
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_CODE): cv.string,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """
    Validate the user input allows us to connect.

    Args:
        hass: The Home Assistant instance.
        data: The user input data.

    Returns:
        The validated login data.

    """
    session = aiohttp_client.async_create_clientsession(hass)
    api = AmazonEchoApi(
        session,
        data[CONF_USERNAME],
        data[CONF_PASSWORD],
    )

    return await api.login.login_mode_interactive(data[CONF_CODE])


class AlexaToDoListsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Alexa ToDo Lists."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle the initial step.

        Args:
            user_input: The user input.

        Returns:
            The config flow result.

        """
        errors = {}
        if user_input:
            try:
                data = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except CannotAuthenticate:
                errors["base"] = "invalid_auth"
            except CannotRetrieveData:
                errors["base"] = "cannot_retrieve_data"
            else:
                await self.async_set_unique_id(data["customer_info"]["user_id"])
                self._abort_if_unique_id_configured()
                user_input.pop(CONF_CODE)
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input | {CONF_LOGIN_DATA: data},
                )

        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): cv.string,
                    vol.Required(CONF_PASSWORD): cv.string,
                    vol.Required(CONF_CODE): cv.string,
                }
            ),
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """
        Handle reauth flow.

        Args:
            entry_data: The entry data.

        Returns:
            The config flow result.

        """
        self.context["title_placeholders"] = {CONF_USERNAME: entry_data[CONF_USERNAME]}
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle reauth confirm.

        Args:
            user_input: The user input.

        Returns:
            The config flow result.

        """
        errors: dict[str, str] = {}

        reauth_entry = self._get_reauth_entry()
        entry_data = reauth_entry.data

        if user_input is not None:
            try:
                data = await validate_input(
                    self.hass, {**reauth_entry.data, **user_input}
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except CannotAuthenticate:
                errors["base"] = "invalid_auth"
            except CannotRetrieveData:
                errors["base"] = "cannot_retrieve_data"
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data={
                        CONF_USERNAME: entry_data[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_CODE: user_input[CONF_CODE],
                        CONF_LOGIN_DATA: data,
                    },
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            description_placeholders={CONF_USERNAME: entry_data[CONF_USERNAME]},
            data_schema=STEP_REAUTH_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle reconfiguration of the device.

        Args:
            user_input: The user input.

        Returns:
            The config flow result.

        """
        reconfigure_entry = self._get_reconfigure_entry()
        if not user_input:
            return self.async_show_form(
                step_id="reconfigure",
                data_schema=STEP_RECONFIGURE,
            )

        updated_password = user_input[CONF_PASSWORD]

        self._async_abort_entries_match(
            {CONF_USERNAME: reconfigure_entry.data[CONF_USERNAME]}
        )

        errors: dict[str, str] = {}

        try:
            data = await validate_input(
                self.hass, {**reconfigure_entry.data, **user_input}
            )
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except CannotAuthenticate:
            errors["base"] = "invalid_auth"
        except CannotRetrieveData:
            errors["base"] = "cannot_retrieve_data"
        else:
            return self.async_update_reload_and_abort(
                reconfigure_entry,
                data_updates={
                    CONF_PASSWORD: updated_password,
                    CONF_LOGIN_DATA: data,
                },
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=STEP_RECONFIGURE,
            errors=errors,
        )
