"""Initialisierung und Setup für Paw Control."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import dashboard
from .const import (
    CONF_CREATE_DASHBOARD,
    CONF_DOG_NAME,
)

from .module_manager import (
    async_ensure_helpers,
    async_setup_modules,
    async_unload_modules,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setze die Integration samt aller gewählten Module auf."""
    opts = entry.options if entry.options else entry.data

    # 1. Alle benötigten Helper automatisch prüfen/erstellen (je nach Modulstatus)
    await async_ensure_helpers(hass, opts)

    # 2. Modul-Setup je nach Opt-in/Opt-out
    await async_setup_modules(hass, entry, opts)

    if opts.get(CONF_CREATE_DASHBOARD, False):
        await dashboard.create_dashboard(hass, opts[CONF_DOG_NAME])

    return True


async def async_unload_entry(hass, entry):
    """Beim Entfernen der Integration: alle Module/Helper aufräumen."""
    await async_unload_modules(hass, entry)
    # Dashboard bleibt, falls es nicht explizit entfernt werden soll.
    return True
