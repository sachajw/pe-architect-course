import os
import re
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List

import aiosqlite
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class TeamCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 63:
            raise ValueError("Team name must be between 2 and 63 characters")
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Team name may only contain alphanumeric characters, hyphens, and underscores"
            )
        return v


class Team(BaseModel):
    id: str
    name: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Database / lifespan
# ---------------------------------------------------------------------------
DB_PATH = os.getenv("DB_PATH", "teams.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS teams (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    await db.commit()
    app.state.db = db
    yield
    await db.close()


# ---------------------------------------------------------------------------
# App & CORS
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Teams API",
    description="A simple API for team leads to create and manage teams",
    version="1.0.0",
    lifespan=lifespan,
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:4200").split(",")
is_wildcard = allowed_origins == ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False if is_wildcard else True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
async def root():
    return {"message": "Teams API is running"}


@app.post("/teams", response_model=Team)
async def create_team(team: TeamCreate):
    """Create a new team"""
    db: aiosqlite.Connection = app.state.db

    async with db.execute(
        "SELECT id FROM teams WHERE LOWER(name) = LOWER(?)", (team.name,)
    ) as cursor:
        if await cursor.fetchone():
            raise HTTPException(status_code=400, detail="Team name already exists")

    team_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)

    await db.execute(
        "INSERT INTO teams (id, name, created_at) VALUES (?, ?, ?)",
        (team_id, team.name, created_at.isoformat()),
    )
    await db.commit()

    return Team(id=team_id, name=team.name, created_at=created_at)


@app.get("/teams", response_model=List[Team])
async def get_teams(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Get teams with pagination"""
    db: aiosqlite.Connection = app.state.db

    async with db.execute(
        "SELECT id, name, created_at FROM teams ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ) as cursor:
        rows = await cursor.fetchall()

    return [Team(id=row["id"], name=row["name"], created_at=row["created_at"]) for row in rows]


@app.get("/teams/{team_id}", response_model=Team)
async def get_team(team_id: str):
    """Get a specific team by ID"""
    db: aiosqlite.Connection = app.state.db

    async with db.execute(
        "SELECT id, name, created_at FROM teams WHERE id = ?", (team_id,)
    ) as cursor:
        row = await cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Team not found")

    return Team(id=row["id"], name=row["name"], created_at=row["created_at"])


@app.delete("/teams/{team_id}")
async def delete_team(team_id: str):
    """Delete a team"""
    db: aiosqlite.Connection = app.state.db

    async with db.execute(
        "SELECT id, name FROM teams WHERE id = ?", (team_id,)
    ) as cursor:
        row = await cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Team not found")

    await db.execute("DELETE FROM teams WHERE id = ?", (team_id,))
    await db.commit()

    return {"message": f"Team '{row['name']}' deleted successfully"}


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes"""
    db: aiosqlite.Connection = app.state.db

    async with db.execute("SELECT COUNT(*) as cnt FROM teams") as cursor:
        row = await cursor.fetchone()

    return {"status": "healthy", "teams_count": row["cnt"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
