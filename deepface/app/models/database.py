"""
Async PostgreSQL database layer for session tracking and violation logging.

Uses asyncpg connection pool for non-blocking database operations.
Tables: deepface_sessions, deepface_violations, deepface_engagement_snapshots

All tables are prefixed with 'deepface_' to coexist safely with Django tables
in the shared 'verifihir' PostgreSQL database.
"""

import asyncpg
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.config import PG_HOST, PG_PORT, PG_NAME, PG_USER, PG_PASSWORD

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """Get or create the connection pool."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_NAME,
            user=PG_USER,
            password=PG_PASSWORD,
            min_size=2,
            max_size=10,
        )
        # Tables are managed by Django migrations (backend/deepface_proctoring/models.py)
        logger.info(f"PostgreSQL pool created — {PG_USER}@{PG_HOST}:{PG_PORT}/{PG_NAME}")
    return _pool


async def close_db():
    """Close the connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None



# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def _row_to_dict(row: asyncpg.Record) -> Dict[str, Any]:
    """Convert an asyncpg Record to a plain dict."""
    return dict(row)


# ──────────────────────────────────────────────
# SESSION CRUD
# ──────────────────────────────────────────────

async def create_session(
    session_id: str,
    person_id: str,
    config: Optional[Dict] = None,
    camera_device: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new monitoring session."""
    pool = await get_pool()
    now = datetime.utcnow().isoformat()
    config_json = json.dumps(config) if config else "{}"

    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO deepface_sessions
               (session_id, person_id, started_at, config, camera_device)
               VALUES ($1, $2, $3, $4, $5)""",
            session_id, person_id, now, config_json, camera_device,
        )

    return {
        "session_id": session_id,
        "person_id": person_id,
        "status": "active",
        "started_at": now,
    }


async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session by ID."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM deepface_sessions WHERE session_id = $1", session_id
        )
    if row:
        return _row_to_dict(row)
    return None


async def update_session(session_id: str, **kwargs):
    """Update session fields."""
    pool = await get_pool()
    set_clauses = ", ".join(f"{k} = ${i+1}" for i, k in enumerate(kwargs.keys()))
    values = list(kwargs.values()) + [session_id]
    idx = len(kwargs) + 1

    async with pool.acquire() as conn:
        await conn.execute(
            f"UPDATE deepface_sessions SET {set_clauses} WHERE session_id = ${idx}",
            *values,
        )


async def end_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Mark a session as completed."""
    pool = await get_pool()
    now = datetime.utcnow().isoformat()

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE deepface_sessions SET status = 'completed', ended_at = $1 WHERE session_id = $2",
            now, session_id,
        )

    return await get_session(session_id)


async def increment_session_counters(
    session_id: str,
    frames: int = 0,
    violations: int = 0,
    engagement_score: Optional[float] = None,
    verification_attempt: bool = False,
    verification_success: bool = False,
):
    """Increment frame/violation counters and update engagement stats."""
    pool = await get_pool()

    updates = []
    params = []
    idx = 1  # asyncpg $1-based parameter index

    if frames > 0:
        updates.append(f"total_frames = total_frames + ${idx}")
        params.append(frames)
        idx += 1

    if violations > 0:
        updates.append(f"total_violations = total_violations + ${idx}")
        params.append(violations)
        idx += 1

    if engagement_score is not None:
        updates.append(f"engagement_sum = engagement_sum + ${idx}")
        params.append(engagement_score)
        idx += 1
        updates.append("avg_engagement = engagement_sum / GREATEST(total_frames, 1)")
        updates.append(f"min_engagement = LEAST(min_engagement, ${idx})")
        params.append(engagement_score)
        idx += 1
        updates.append(f"max_engagement = GREATEST(max_engagement, ${idx})")
        params.append(engagement_score)
        idx += 1

    if verification_attempt:
        updates.append("verification_attempts = verification_attempts + 1")

    if verification_success:
        updates.append("verification_successes = verification_successes + 1")

    if updates:
        params.append(session_id)
        query = f"UPDATE deepface_sessions SET {', '.join(updates)} WHERE session_id = ${idx}"
        async with pool.acquire() as conn:
            await conn.execute(query, *params)


async def update_micro_violation_score(session_id: str, score: float):
    """Update the accumulated micro-violation score."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE deepface_sessions SET micro_violation_score = $1 WHERE session_id = $2",
            score, session_id,
        )


# ──────────────────────────────────────────────
# VIOLATION CRUD
# ──────────────────────────────────────────────

async def log_violation(
    session_id: str,
    violation_type: str,
    severity: str,
    message: str,
    details: Optional[Dict] = None,
    frame_snapshot: Optional[str] = None,
) -> int:
    """Log a violation event. Returns the violation ID."""
    pool = await get_pool()
    now = datetime.utcnow().isoformat()
    details_json = json.dumps(details) if details else None

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO deepface_violations
               (session_id, type, severity, message, timestamp, details, frame_snapshot)
               VALUES ($1, $2, $3, $4, $5, $6, $7)
               RETURNING id""",
            session_id, violation_type, severity, message, now, details_json, frame_snapshot,
        )

    # Also increment session violation counter
    await increment_session_counters(session_id, violations=1)

    return row["id"]


async def get_violations(
    session_id: str,
    violation_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    """Get violations for a session with optional filtering."""
    pool = await get_pool()

    query = "SELECT * FROM deepface_violations WHERE session_id = $1"
    params: list = [session_id]
    idx = 2

    if violation_type:
        query += f" AND type = ${idx}"
        params.append(violation_type)
        idx += 1

    if severity:
        query += f" AND severity = ${idx}"
        params.append(severity)
        idx += 1

    query += f" ORDER BY timestamp DESC LIMIT ${idx}"
    params.append(limit)

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)

    results = []
    for row in rows:
        d = _row_to_dict(row)
        if d.get("details"):
            try:
                d["details"] = json.loads(d["details"])
            except (json.JSONDecodeError, TypeError):
                pass
        results.append(d)

    return results


async def get_violation_breakdown(session_id: str) -> Dict[str, int]:
    """Get count of violations by type for a session."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT type, COUNT(*) as count FROM deepface_violations WHERE session_id = $1 GROUP BY type",
            session_id,
        )
    return {row["type"]: row["count"] for row in rows}


# ──────────────────────────────────────────────
# ENGAGEMENT SNAPSHOTS
# ──────────────────────────────────────────────

async def log_engagement_snapshot(
    session_id: str,
    score: float,
    components: Optional[Dict] = None,
):
    """Log an engagement score snapshot."""
    pool = await get_pool()
    now = datetime.utcnow().isoformat()
    comp_json = json.dumps(components) if components else None

    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO deepface_engagement_snapshots
               (session_id, timestamp, score, components)
               VALUES ($1, $2, $3, $4)""",
            session_id, now, score, comp_json,
        )


async def get_engagement_timeline(session_id: str) -> List[Dict[str, Any]]:
    """Get engagement score timeline for a session."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT timestamp, score FROM deepface_engagement_snapshots WHERE session_id = $1 ORDER BY timestamp",
            session_id,
        )
    return [_row_to_dict(row) for row in rows]
