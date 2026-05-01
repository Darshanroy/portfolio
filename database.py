import os
import asyncio
from typing import List, Optional
from supabase import create_async_client, AsyncClient, AsyncClientOptions
from dotenv import load_dotenv
import data_store as ds

load_dotenv()

# ---------------------------------------------------------------------------
# High-Performance Data Manager
# ---------------------------------------------------------------------------

class SupabaseService:
    _async_client: Optional[AsyncClient] = None

    @classmethod
    async def get_client(cls) -> AsyncClient:
        if cls._async_client is None:
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")
            if not url or not key:
                return None # Return None if not configured
            opts = AsyncClientOptions(postgrest_client_timeout=10)
            try:
                cls._async_client = await create_async_client(url, key, options=opts)
            except:
                return None
        return cls._async_client

    @classmethod
    async def get_projects(cls) -> List[ds.Project]:
        """Clearly returns projects from the Seed Data with Cloud sync attempt."""
        # Start with our high-quality seed data
        projects = ds.PROJECTS
        
        # Optionally try to sync with Cloud (Supabase)
        client = await cls.get_client()
        if client:
            try:
                res = await client.table("projects").select("*").execute()
                if res.data:
                    # If cloud has data, it can override or augment local data
                    return [ds.Project(**item) for item in res.data]
            except:
                pass # Fallback to seed data on any network issue
        
        return projects

    @classmethod
    async def get_project(cls, project_id: str) -> Optional[ds.Project]:
        projects = await cls.get_projects()
        return next((p for p in projects if p.id == project_id), None)

    @classmethod
    async def get_skills(cls, skill_type: Optional[str] = None) -> List[ds.Skill]:
        skills = ds.SKILLS
        if skill_type:
            skills = [s for s in skills if s.type == skill_type]
        return skills

    @classmethod
    async def get_skills_by_types(cls, types: List[str]) -> List[ds.Skill]:
        return [s for s in ds.SKILLS if s.type in types]

    @classmethod
    async def get_skill_with_sections(cls, skill_id: str) -> Optional[ds.Skill]:
        return next((s for s in ds.SKILLS if s.id == skill_id), None)

    @classmethod
    async def get_achievements(cls) -> List[ds.Achievement]:
        return ds.ACHIEVEMENTS

    @classmethod
    async def add_contact_message(cls, name: str, email: str, message: str):
        """Always sends contact messages to Supabase (if available)."""
        client = await cls.get_client()
        if client:
            try:
                await client.table("contact_messages").insert({
                    "name": name, 
                    "email": email, 
                    "message": message
                }).execute()
            except:
                print("Failed to save contact message to cloud.")
