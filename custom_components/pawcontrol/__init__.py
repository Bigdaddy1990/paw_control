"""Initialisierung und Setup für Paw Control."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import dashboard, gps, health, push, walk
from .const import (
    CONF_CREATE_DASHBOARD,
    CONF_DOG_NAME,
    CONF_GPS_ENABLE,
    CONF_HEALTH_MODULE,
    CONF_NOTIFICATIONS_ENABLED,
    CONF_WALK_MODULE,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setze die Integration samt aller gewählten Module auf."""
    opts = entry.options if entry.options else entry.data

    # 1. Alle benötigten Helper automatisch prüfen/erstellen (je nach Modulstatus)
    await ensure_helpers(hass, opts)

    # 2. Modul-Setup je nach Opt-in/Opt-out
    if opts.get(CONF_GPS_ENABLE, True):
        await gps.setup_gps(hass, entry)
    else:
        await gps.teardown_gps(hass, entry)

    if opts.get(CONF_NOTIFICATIONS_ENABLED, True):
        await push.setup_push(hass, entry)
    else:
        await push.teardown_push(hass, entry)

    if opts.get(CONF_HEALTH_MODULE, True):
        await health.setup_health(hass, entry)
    else:
        await health.teardown_health(hass, entry)

    if opts.get(CONF_WALK_MODULE, True):
        await walk.setup_walk(hass, entry)
    else:
        await walk.teardown_walk(hass, entry)

    if opts.get(CONF_CREATE_DASHBOARD, False):
        await dashboard.create_dashboard(hass, opts[CONF_DOG_NAME])

    return True

async def async_unload_entry(hass, entry):
    """Beim Entfernen der Integration: alle Module/Helper aufräumen."""
    await gps.teardown_gps(hass, entry)
    await push.teardown_push(hass, entry)
    await health.teardown_health(hass, entry)
    await walk.teardown_walk(hass, entry)
    # Dashboard bleibt, falls es nicht explizit entfernt werden soll.
    return True

async def ensure_helpers(hass, opts):
    """Prüft und legt alle für aktivierte Module nötigen Helper/Sensoren an."""
    # Beispiel: Health-Status, Walk-Counter, GPS-Status, ...
    # (Diese Logik ruft die Helper-Init der jeweiligen Module auf.)
    if opts.get(CONF_HEALTH_MODULE, True):
        await health.ensure_helpers(hass, opts)
    if opts.get(CONF_WALK_MODULE, True):
        await walk.ensure_helpers(hass, opts)
    if opts.get(CONF_GPS_ENABLE, True):
        await gps.ensure_helpers(hass, opts)
    # Usw. für weitere Module
