"""Initialization of the Alexa To-do Lists integration."""

from typing import TYPE_CHECKING

from aioamazondevices.api import AmazonEchoApi
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.helpers import aiohttp_client
from pyalexatodo.api import AlexaToDoAPI

from .const import CONF_LOGIN_DATA

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [Platform.TODO]

type AlexaTodoListsConfigEntry = ConfigEntry[AlexaToDoAPI]


async def async_setup_entry(
    hass: HomeAssistant, entry: AlexaTodoListsConfigEntry
) -> bool:
    """
    Set up Alexa Devices platform.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry.

    Returns:
        True if setup was successful.

    """
    session = aiohttp_client.async_create_clientsession(hass)

    amazon_echo_api = AmazonEchoApi(
        session,
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        entry.data[CONF_LOGIN_DATA],
    )

    alexa_todo_lists_api = AlexaToDoAPI(amazon_echo_api)

    entry.runtime_data = alexa_todo_lists_api

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
