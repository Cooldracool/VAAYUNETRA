"""Backend database module alias forwarding to database.py."""

from database import (
    Base,
    IncidentRecord,
    SessionLocal,
    engine,
    get_active_incidents,
    get_all_incidents,
    init_db,
    save_incident,
)

__all__ = [
    "Base",
    "IncidentRecord",
    "SessionLocal",
    "engine",
    "get_active_incidents",
    "get_all_incidents",
    "init_db",
    "save_incident",
]
