"""Platform for Alexa To-do integration."""

from __future__ import annotations

import datetime

# Import to avoid "Detected blocking call to import_module" warning
import encodings.ascii  # noqa: F401
from typing import TYPE_CHECKING

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import slugify

from .utils import alexa_api_call, async_update_error_context

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import (
        AddConfigEntryEntitiesCallback,
    )
    from pyalexatodo.api import AlexaToDoAPI
    from pyalexatodo.models.list_info import ListInfo
    from pyalexatodo.models.list_item import ListItem

    from custom_components.alexa_todo import AlexaTodoListsConfigEntry


SCAN_INTERVAL = datetime.timedelta(minutes=10)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: AlexaTodoListsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """
    Set up the Alexa To-do Lists platform.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry.
        async_add_entities: The callback to add entities.

    """
    alexa_list_api: AlexaToDoAPI = entry.runtime_data

    async with async_update_error_context():
        await alexa_list_api.alexa_echo_api.login.login_mode_stored_data()
        available_lists = await alexa_list_api.get_lists()

    async_add_entities(
        [AlexaToDoList(alexa_list, alexa_list_api) for alexa_list in available_lists],
        update_before_add=True,
    )


class AlexaToDoList(TodoListEntity):
    """Representation of an Alexa To-do List."""

    _attr_has_entity_name = True
    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
    )

    def __init__(self, alexa_list: ListInfo, alexa_list_api: AlexaToDoAPI) -> None:
        """
        Initialize an AlexaTodoList.

        Args:
            alexa_list: The Alexa list information.
            alexa_list_api: The Alexa To-do API.

        """
        self._list: ListInfo = alexa_list
        self._alexa_list_api: AlexaToDoAPI = alexa_list_api

        self._attr_unique_id = slugify(self._list.name)

        self.name = alexa_list.name

    async def async_update(self) -> None:
        """Update the To-do list items."""
        async with async_update_error_context():
            await self._alexa_list_api.alexa_echo_api.login.login_mode_stored_data()
            list_items: list[ListItem] = await self._alexa_list_api.get_list_items(
                self._list.id
            )

        self._alexa_todo_items_lookup: dict[str, ListItem] = {
            item.id: item for item in list_items
        }
        self.todo_items: list[TodoItem] = [
            TodoItem(
                uid=entry.id,
                summary=entry.name,
                status=TodoItemStatus.COMPLETED
                if entry.is_checked
                else TodoItemStatus.NEEDS_ACTION,
            )
            for entry in list_items
        ]

    @alexa_api_call
    async def async_create_todo_item(self, item: TodoItem) -> None:
        """
        Add an item to the To-do list.

        Args:
            item: The item to add.

        Raises:
            ServiceValidationError: If the item summary is missing.

        """
        if not item.summary:
            raise ServiceValidationError
        await self._alexa_list_api.add_item(self._list.id, item.summary)

    @alexa_api_call
    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """
        Delete items from the to-do list.

        Args:
            uids: The unique IDs of the items to delete.

        """
        for uid in uids:
            version = self._alexa_todo_items_lookup[uid].version
            await self._alexa_list_api.delete_item(self._list.id, uid, version)

    @alexa_api_call
    async def async_update_todo_item(self, item: TodoItem) -> None:
        """
        Update an item in the To-do list.

        Args:
            item: The item to update.

        Raises:
            ServiceValidationError: If the item summary or UID is missing.

        """
        if not item.summary or not item.uid:
            raise ServiceValidationError

        existing_item = self._alexa_todo_items_lookup[item.uid]

        if existing_item.name != item.summary:
            # Name has changed, update it
            await self._alexa_list_api.rename_item(
                self._list.id, item.uid, item.summary, existing_item.version
            )
        else:
            # Onlyupdate the checked status
            await self._alexa_list_api.set_item_checked_status(
                self._list.id,
                item.uid,
                item.status == TodoItemStatus.COMPLETED,
                existing_item.version,
            )
