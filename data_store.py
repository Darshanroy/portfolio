import json
from typing import List
from pydantic import BaseModel, AnyUrl

# ---------------------------------------------------------------------------
# Data Models (Source of Truth)
# ---------------------------------------------------------------------------

class Project(BaseModel):
    id: str
    name: str
    summary: str
    metrics: str = ""
    architecture: str = ""
    failure_handling: str = ""
    tradeoffs: str = ""
    impact: str = ""
    tech_stack: str = ""
    images: List[str] = []
    github_url: str = ""
    live_url: str = ""
    chat_url: str = ""

    def get_images(self) -> List[str]:
        return self.images

class Skill(BaseModel):
    id: str
    title: str
    type: str # 'skill', 'blog', 'learning'
    date: str = ""
    reading_time: str = ""

class Achievement(BaseModel):
    id: str
    title: str
    issuer: str
    date: str
    description: str
    link_url: str = ""

# ---------------------------------------------------------------------------
# The Seed Data (Connected to Main App)
# ---------------------------------------------------------------------------

PROJECTS = [
    Project(
        id='p1',
        name='Jan Sahayak — Civic Assistant',
        summary='A production-grade, multi-agent AI system using LangGraph that orchestrates 5+ specialized agents with RAG-based retrieval to help Indian citizens navigate government schemes.',
        metrics='Evaluated with RAGAS for RAG quality. Supports 5+ Indian languages simultaneously.',
        architecture='5-agent LangGraph pipeline (Policy, Eligibility, Benefits, Advocacy, Conversation) with Agentic RAG across ChromaDB.',
        tech_stack='LangGraph, ChromaDB, FAISS, Flask, Supabase, Docker, Hugging Face',
        images=['https://images.unsplash.com/photo-1517245386807-bb43f82c33c4'],
        github_url='https://github.com/Darshanroy/zynd-hackathon-prod'
    ),
    Project(
        id='p2',
        name='Gandivam — Rural Healthcare',
        summary='An 8-agent clinical AI pipeline using LangGraph, Google Gemini 2.0 Flash, and LangChain to automate multilingual patient intake.',
        metrics='Achieved 78–98% AI confidence on SOAP-note generation. Maintained <2s latency SLA.',
        architecture='Multilingual clinical intake via Sarvam AI SDK. RAG pipeline querying 10+ MoHFW/ICMR protocols.',
        tech_stack='LangGraph, Google Gemini, Pinecone, FastAPI, Supabase, LlamaParse',
        images=['https://images.unsplash.com/photo-1576091160399-112ba8d25d1d'],
        github_url='https://github.com/Darshanroy/et-hackathon'
    ),
    Project(
        id='p3',
        name='InovateHub — Hackathon Platform',
        summary='Backend for a multi-role hackathon management platform with RESTful APIs, JWT authentication, and AI-powered teammate matching.',
        metrics='Built 20+ robust endpoints. Optimized for query performance.',
        tech_stack='Flask, MongoDB Atlas, JWT, Google Genkit AI, Docker',
        images=['https://images.unsplash.com/photo-1504868584819-f8e905b68763'],
        github_url='https://github.com/Darshanroy/inovate-hub'
    )
]

SKILLS = [
    Skill(id='s1', title='LLM Fine-Tuning (QLoRA, PEFT)', type='skill'),
    Skill(id='s2', title='AI Agents (LangGraph, CrewAI)', type='skill'),
    Skill(id='s3', title='Vector Databases (ChromaDB, Pinecone)', type='skill'),
    Skill(id='s4', title='Backend APIs (Flask, FastAPI)', type='skill'),
    Skill(id='s5', title='Cloud & DevOps (Docker, AWS)', type='skill'),
    Skill(id='l1', title='Orchestrating Multi-Agent Systems', type='learning', date='April 2024', reading_time='10 min read'),
    Skill(id='b1', title='Optimizing LLMs with PEFT', type='blog', date='November 2024', reading_time='8 min read')
]

ACHIEVEMENTS = [
    Achievement(id='a1', title='AI Engineer Intern', issuer='EduGorilla Pvt. Ltd', date='Sep 2024', description='Implemented PEFT on Qwen-3B using AWS SageMaker.'),
    Achievement(id='a2', title='B.S. Data Science and AI', issuer='IIT Madras', date='2023 - 2027', description='Pursuing degree in Data Science and AI with a CGPA of 8.0.')
]
