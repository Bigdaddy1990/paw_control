"""Initialisierung und Setup für Paw Control."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import dashboard
from .const import (
    CONF_CREATE_DASHBOARD,
    CONF_DOG_NAME,
)
from .module_registry import MODULES


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setze die Integration samt aller gewählten Module auf."""
    opts = entry.options if entry.options else entry.data

    # 1. Alle benötigten Helper automatisch prüfen/erstellen (je nach Modulstatus)
    await ensure_helpers(hass, opts)

    # 2. Modul-Setup je nach Opt-in/Opt-out
    for key, module in MODULES.items():
        if opts.get(key, module.default):
            await module.setup(hass, entry)
        elif module.teardown:
            await module.teardown(hass, entry)

    if opts.get(CONF_CREATE_DASHBOARD, False):
        await dashboard.create_dashboard(hass, opts[CONF_DOG_NAME])

    return True

async def async_unload_entry(hass, entry):
    """Beim Entfernen der Integration: alle Module/Helper aufräumen."""
    for module in MODULES.values():
        if module.teardown:
            await module.teardown(hass, entry)
    # Dashboard bleibt, falls es nicht explizit entfernt werden soll.
    return True

async def ensure_helpers(hass, opts):
    """Prüft und legt alle für aktivierte Module nötigen Helper/Sensoren an."""
    # Beispiel: Health-Status, Walk-Counter, GPS-Status, ...
    # (Diese Logik ruft die Helper-Init der jeweiligen Module auf.)
    for key, module in MODULES.items():
        if opts.get(key, module.default) and module.ensure_helpers:
            await module.ensure_helpers(hass, opts)
    # Usw. für weitere Module
