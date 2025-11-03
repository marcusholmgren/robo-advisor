"""Database configuration for TortoiseORM."""


# TortoiseORM configuration
TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://db.sqlite3"
    },
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        }
    },
}


def get_tortoise_config() -> dict:
    """Get TortoiseORM configuration."""
    return TORTOISE_ORM
