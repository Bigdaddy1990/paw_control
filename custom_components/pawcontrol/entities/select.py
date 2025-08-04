# entities/select.py
from homeassistant.components.select import SelectEntity

from .base import PawControlBaseEntity
from ..helpers.entity import ensure_option, format_name, get_icon

class PawControlSelectEntity(PawControlBaseEntity, SelectEntity):
    """Basisklasse für Select-Entities mit Validierung."""

    def __init__(
        self,
        coordinator,
        name: str | None = None,
        dog_name: str | None = None,
        unique_suffix: str | None = None,
        *,
        key: str | None = None,
        icon: str | None = None,
        options: list[str] | None = None,
    ) -> None:
        if dog_name and key and not name:
            name = format_name(dog_name, key)
        if key and not unique_suffix:
            unique_suffix = key
        super().__init__(coordinator, name, dog_name, unique_suffix)
        if icon or key:
            self._attr_icon = icon or get_icon(key)
        self._attr_options = options or []
        if self._attr_options:
            self._state = self._attr_options[0]

    @property
    def current_option(self):
        return self._state

    async def async_select_option(self, option: str):
        """Wähle eine Option aus der Optionsliste."""
        self._state = ensure_option(option, self.options)

    @property
    def options(self):
        return self._attr_options
