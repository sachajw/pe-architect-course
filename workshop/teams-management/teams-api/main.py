from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import uuid
from datetime import datetime
import aiosqlite
import os

# Database path - use /data directory for persistence
DATABASE_PATH = os.getenv("DATABASE_PATH", "/data/teams.db")

async def init_db():
    """Initialize the database and create tables if not exist"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()

async def get_team_by_name(name: str) -> Optional[dict]:
    """Get team by name (case-insensitive)"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM teams WHERE LOWER(name) = LOWER(?)",
            (name,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

async def get_team_by_id(team_id: str) -> Optional[dict]:
    """Get team by ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def get_all_teams() -> List[dict]:
    """Get all teams"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM teams ORDER BY created_at")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def create_team_in_db(team_id: str, name: str, created_at: datetime) -> dict:
    """Create a new team in the database"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO teams (id, name, created_at) VALUES (?, ?, ?)",
            (team_id, name, created_at.isoformat())
        )
        await db.commit()
    return {"id": team_id, "name": name, "created_at": created_at}

async def delete_team_from_db(team_id: str) -> Optional[dict]:
    """Delete a team from the database"""
    team = await get_team_by_id(team_id)
    if team:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("DELETE FROM teams WHERE id = ?", (team_id,))
            await db.commit()
    return team

async def count_teams() -> int:
    """Count total teams"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM teams")
        count = await cursor.fetchone()
        return count[0] if count else 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup: Initialize database
    await init_db()
    yield
    # Shutdown: cleanup if needed

app = FastAPI(
    title="Teams API",
    description="A simple API for team leads to create and manage teams",
    version="1.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {"message": "Teams API is running", "storage": "sqlite"}


@app.post("/teams", response_model=Team)
async def create_team(team: TeamCreate):
    """Create a new team"""
    # Check if team name already exists
    existing = await get_team_by_name(team.name)
    if existing:
        raise HTTPException(status_code=400, detail="Team name already exists")

    team_id = str(uuid.uuid4())
    created_at = datetime.now()

    await create_team_in_db(team_id, team.name, created_at)

    return Team(id=team_id, name=team.name, created_at=created_at)

@app.get("/teams", response_model=List[Team])
async def get_teams():
    """Get all teams"""
    teams = await get_all_teams()
    return [Team(
        id=t["id"],
        name=t["name"],
        created_at=datetime.fromisoformat(t["created_at"])
    ) for t in teams]

@app.get("/teams/{team_id}", response_model=Team)
async def get_team(team_id: str):
    """Get a specific team by ID"""
    team = await get_team_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return Team(
        id=team["id"],
        name=team["name"],
        created_at=datetime.fromisoformat(team["created_at"])
    )

@app.delete("/teams/{team_id}")
async def delete_team(team_id: str):
    """Delete a team"""
    deleted = await delete_team_from_db(team_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Team not found")

    return {"message": f"Team '{deleted['name']}' deleted successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes"""
    count = await count_teams()
    return {"status": "healthy", "teams_count": count, "storage": "sqlite"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
