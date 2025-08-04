"""Push-Modul für Paw Control – Service, Target-Handling, Setup/Teardown."""

from .const import *
from .utils import register_services

async def setup_push(hass, entry):
    """Registriert Push-Service, Helper für Benachrichtigungen."""
    dog = entry.data[CONF_DOG_NAME]
    helper_id = f"input_boolean.{dog}_push_active"

    # Helper für Push-Benachrichtigungen anlegen (falls nicht vorhanden)
    if not hass.states.get(helper_id):
        await hass.services.async_call(
            "input_boolean", "create",
            {"name": f"{dog} Push aktiviert", "entity_id": helper_id},
            blocking=True,
        )

    # Service registrieren
    async def handle_send_notification(call):
        message = call.data.get("message", "Aktion erforderlich!")
        title = call.data.get("title", f"Paw Control: {dog}")
        target = call.data.get("target", None)
        # Beispiel: persistent_notification (Push via App kannst du analog mit notify.notify machen)
        hass.components.persistent_notification.create(
            f"{dog}: {message}",
            title=title
        )
    register_services(
        hass,
        DOMAIN,
        {SERVICE_SEND_NOTIFICATION: handle_send_notification},
    )

async def teardown_push(hass, entry):
    """Entfernt Push-Service und zugehörige Helper."""
    dog = entry.data[CONF_DOG_NAME]
    helper_id = f"input_boolean.{dog}_push_active"
    # Helper entfernen
    if hass.states.get(helper_id):
        await hass.services.async_call(
            "input_boolean", "remove",
            {"entity_id": helper_id},
            blocking=True,
        )
    # Service deregistrieren
    if hass.services.has_service(DOMAIN, SERVICE_SEND_NOTIFICATION):
        hass.services.async_remove(DOMAIN, SERVICE_SEND_NOTIFICATION)

async def ensure_helpers(hass, opts):
    """Stellt sicher, dass Push-Helper existieren."""
    dog = opts[CONF_DOG_NAME]
    helper_id = f"input_boolean.{dog}_push_active"
    if not hass.states.get(helper_id):
        await hass.services.async_call(
            "input_boolean", "create",
            {"name": f"{dog} Push aktiviert", "entity_id": helper_id},
            blocking=True,
        )
