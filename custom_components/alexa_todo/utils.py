"""Utils for Alexa Devices."""

from contextlib import asynccontextmanager
from functools import wraps
from typing import TYPE_CHECKING, Any, Concatenate

from aioamazondevices import CannotAuthenticate
from aioamazondevices.exceptions import CannotConnect, CannotRetrieveData
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import DOMAIN

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable, Callable, Coroutine


def alexa_api_call[T, **P](
    func: Callable[Concatenate[T, P], Awaitable[None]],
) -> Callable[Concatenate[T, P], Coroutine[Any, Any, None]]:
    """
    Catch Alexa API call exceptions.

    Args:
        func: The function to wrap.

    Returns:
        The wrapped function.

    """

    @wraps(func)
    async def cmd_wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> None:
        """Wrap all command methods."""
        try:
            await func(self, *args, **kwargs)
        except CannotConnect as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="cannot_connect_with_error",
                translation_placeholders={"error": repr(err)},
            ) from err
        except CannotRetrieveData as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="cannot_retrieve_data_with_error",
                translation_placeholders={"error": repr(err)},
            ) from err

    return cmd_wrapper


@asynccontextmanager
async def async_update_error_context() -> AsyncGenerator[None]:
    """
    Context manager to handle Alexa API call exceptions during updates.

    Yields:
        None.

    Raises:
        ConfigEntryAuthFailed: If authentication fails.
        UpdateFailed: If connection or data retrieval fails.

    """
    try:
        yield
    except CannotAuthenticate as err:
        raise ConfigEntryAuthFailed from err
    except (CannotConnect, CannotRetrieveData) as err:
        raise UpdateFailed from err
