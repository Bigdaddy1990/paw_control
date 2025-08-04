# helpers/entity.py
def get_icon_by_status(status):
    icons = {
        "online": "mdi:check-circle",
        "offline": "mdi:alert-circle",
        "unknown": "mdi:help-circle",
    }
    return icons.get(status, "mdi:help-circle")
