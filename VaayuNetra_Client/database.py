"""SQLite persistence layer for VaayuNetra incidents using SQLAlchemy."""

from typing import Any, Dict, List, Optional
import datetime
import json
import logging
import os
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger("vaayunetra.database")

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "vaayunetra.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class IncidentRecord(Base):
    __tablename__ = "incidents"

    ticket_id = Column(String(64), primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    category = Column(String(128), index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    verification_json = Column(Text, nullable=False)
    atmospheric_json = Column(Text, nullable=False)
    impact_json = Column(Text, nullable=False)
    plume_geojson = Column(Text, nullable=False)
    full_ticket_json = Column(Text, nullable=False)


def init_db():
    """Create tables if they do not exist."""
    Base.metadata.create_all(bind=engine)
    logger.info("Initialized SQLite database at %s", DB_PATH)


def save_incident(ticket: Dict[str, Any]) -> Dict[str, Any]:
    """Persist an incident ticket into SQLite database."""
    init_db()
    session = SessionLocal()
    try:
        ts_str = ticket.get("timestamp")
        ts = None
        if ts_str:
            try:
                # Handle ISO format with Z or timezone
                clean_ts = ts_str.replace("Z", "+00:00")
                ts = datetime.datetime.fromisoformat(clean_ts)
                if ts.tzinfo is not None:
                    ts = ts.astimezone(datetime.timezone.utc).replace(tzinfo=None)
            except Exception:
                ts = datetime.datetime.utcnow()
        else:
            ts = datetime.datetime.utcnow()

        record = IncidentRecord(
            ticket_id=ticket["ticket_id"],
            timestamp=ts,
            category=ticket.get("category", "general"),
            latitude=float(ticket["latitude"]),
            longitude=float(ticket["longitude"]),
            verification_json=json.dumps(ticket.get("verification", {})),
            atmospheric_json=json.dumps(ticket.get("atmospheric", {})),
            impact_json=json.dumps(ticket.get("impact", {})),
            plume_geojson=json.dumps(ticket.get("plume_geojson", {})),
            full_ticket_json=json.dumps(ticket),
        )
        session.merge(record)
        session.commit()
        logger.info("Persisted incident %s to vaayunetra.db", ticket["ticket_id"])
        return ticket
    except Exception as exc:
        session.rollback()
        logger.error("Failed to persist incident %s: %s", ticket.get("ticket_id"), exc)
        raise
    finally:
        session.close()


def get_all_incidents() -> List[Dict[str, Any]]:
    """Retrieve all persisted incidents ordered by most recent."""
    init_db()
    session = SessionLocal()
    try:
        records = (
            session.query(IncidentRecord)
            .order_by(IncidentRecord.timestamp.desc())
            .all()
        )
        incidents = []
        for r in records:
            try:
                incidents.append(json.loads(r.full_ticket_json))
            except Exception:
                incidents.append({
                    "ticket_id": r.ticket_id,
                    "timestamp": r.timestamp.isoformat() + "Z",
                    "category": r.category,
                    "latitude": r.latitude,
                    "longitude": r.longitude,
                    "verification": json.loads(r.verification_json),
                    "atmospheric": json.loads(r.atmospheric_json),
                    "impact": json.loads(r.impact_json),
                    "plume_geojson": json.loads(r.plume_geojson),
                })
        return incidents
    finally:
        session.close()


def get_active_incidents(hours: float = 4.0) -> List[Dict[str, Any]]:
    """Retrieve active incidents created within the last `hours` window."""
    init_db()
    session = SessionLocal()
    try:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
        records = (
            session.query(IncidentRecord)
            .filter(IncidentRecord.timestamp >= cutoff)
            .order_by(IncidentRecord.timestamp.desc())
            .all()
        )
        incidents = []
        for r in records:
            try:
                incidents.append(json.loads(r.full_ticket_json))
            except Exception:
                incidents.append({
                    "ticket_id": r.ticket_id,
                    "timestamp": r.timestamp.isoformat() + "Z",
                    "category": r.category,
                    "latitude": r.latitude,
                    "longitude": r.longitude,
                    "verification": json.loads(r.verification_json),
                    "atmospheric": json.loads(r.atmospheric_json),
                    "impact": json.loads(r.impact_json),
                    "plume_geojson": json.loads(r.plume_geojson),
                })
        return incidents
    finally:
        session.close()
