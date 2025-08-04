from typing import Any

from custom_components.pawcontrol.entities.health import PawControlHealthEntity
from custom_components.pawcontrol.const import ATTR_DOG_NAME, ATTR_LAST_UPDATED


class DummyLogger:
    """Simple logger stub returning a fixed health entry."""

    def get_latest(self, activity_type: str | None = None) -> dict[str, Any]:
        return {
            "timestamp": "2023-10-10T10:00:00",
            "details": {"status": "ok"},
        }


def test_health_entity_attributes_use_helper():
    logger = DummyLogger()
    entity = PawControlHealthEntity(logger, "entry", "Health", "health", dog_name="Bello")

    attrs = entity.extra_state_attributes

    assert attrs[ATTR_DOG_NAME] == "Bello"
    assert ATTR_LAST_UPDATED in attrs
    assert attrs["details"]["status"] == "ok"
