"""Initialisierung und Setup für Paw Control."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .installation_manager import InstallationManager


manager = InstallationManager()

from . import dashboard
from .const import (
    CONF_CREATE_DASHBOARD,
    CONF_DOG_NAME,
)

from .module_registry import (
    ensure_helpers as module_ensure_helpers,
    setup_modules as module_setup_modules,
    unload_modules as module_unload_modules,

from .module_manager import (
    async_ensure_helpers,
    async_setup_modules,
    async_unload_modules,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setze die Integration samt aller gewählten Module auf."""
    opts = entry.options if entry.options else entry.data

    # 1. Alle benötigten Helper automatisch prüfen/erstellen (je nach Modulstatus)
    await module_ensure_helpers(hass, opts)

    # 2. Modul-Setup je nach Opt-in/Opt-out
    await module_setup_modules(hass, entry, opts)
  
    await async_ensure_helpers(hass, opts)

    # 2. Modul-Setup je nach Opt-in/Opt-out
    await async_setup_modules(hass, entry, opts)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setze die Integration samt aller gewählten Module auf."""
    return await manager.setup_entry(hass, entry)



async def async_unload_entry(hass, entry):
    """Beim Entfernen der Integration: alle Module/Helper aufräumen."""
 
    return await manager.unload_entry(hass, entry)

    await module_unload_modules(hass, entry)

    await async_unload_modules(hass, entry)

    # Dashboard bleibt, falls es nicht explizit entfernt werden soll.
    return True
