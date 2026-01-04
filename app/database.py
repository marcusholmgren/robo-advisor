"""
/home/marcus/code/marcus/robo-advisor/app/database.py
Database configuration for TortoiseORM.
This file sets up the connection to the SQLite database and defines the app models.
RELEVANT FILES: app/models.py, app/main.py
"""

# TortoiseORM configuration
TORTOISE_ORM = {
    "connections": {"default": "sqlite://portfolio-db.sqlite3"},
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
