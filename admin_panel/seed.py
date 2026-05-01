import json
from app import app
from models import db, Project, Skill, SkillSection, Achievement

mock_projects = [
    {
        'id': 'p1',
        'name': 'Jan Sahayak — Civic Assistant',
        'summary': 'A production-grade, multi-agent AI system using LangGraph that orchestrates 5+ specialized agents with RAG-based retrieval, 4-layer guardrails, and real-time observability to help Indian citizens navigate government schemes and benefits.',
        'metrics': 'Evaluated with RAGAS for RAG quality. Supports 5+ Indian languages simultaneously with continuous SSE streaming for immediate token delivery.',
        'architecture': 'Orchestrated a 5-agent LangGraph pipeline (Policy, Eligibility, Benefits, Advocacy, Conversation) with Agentic RAG across ChromaDB + FAISS. Uses SQLite checkpointing for persistent conversation history.',
        'failure_handling': 'Achieved end-to-end pipeline trustworthiness with a 4-layer Guardrails AI safety architecture including input filtering, anti-hallucination grounding, and output consistency verification.',
        'tradeoffs': 'Leveraged a multi-agent orchestrated approach over a single monolithic LLM, accepting slight latency increases for a massive gain in domain-specific accuracy and hallucination prevention.',
        'impact': 'Deployed a multilingual production backend via Flask and Telegram Bot integration. Features long-term user memory via mem0 + Supabase, containerized with Docker and live on Hugging Face Spaces.',
        'images': json.dumps([
            'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&q=80&w=600',
            'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=600',
            'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=600'
        ]),
        'github_url': 'https://github.com/Darshanroy/zynd-hackathon-prod',
        'live_url': '#',
        'chat_url': '#'
    },
    {
        'id': 'p2',
        'name': 'Gandivam — Rural Healthcare',
        'summary': 'An 8-agent clinical AI pipeline using LangGraph, Google Gemini 2.0 Flash, Sarvam LLMs, and LangChain to automate multilingual patient intake and generate SOAP-format clinical summaries.',
        'metrics': 'Achieved 78–98% AI confidence on SOAP-note generation with real-time contradiction detection across 7+ clinical entity types. Maintained <2s latency SLA.',
        'architecture': 'Multilingual clinical intake (Hindi, Tamil, Kannada) via Sarvam AI SDK (STT → translation → TTS). RAG pipeline querying 10+ MoHFW/ICMR protocols on Pinecone with Google text-embedding-004.',
        'failure_handling': 'Incorporated Human-in-the-Loop doctor review dashboards to safely handle edge cases and AI uncertainty for rural Primary Health Centers. Utilized LlamaParse OCR for Aadhaar verification.',
        'tradeoffs': 'Chose a complex 4 parallel session phases (Intake → Processing → Review → Feedback) design to ensure maximum clinical safety over a simpler direct-response chatbot.',
        'impact': 'Delivered DISHA/ABDM-compliant infrastructure on Supabase (PostgreSQL) with 11 tables, RLS policies, RBAC across 4 roles, and 20+ REST/WebSocket endpoints via FastAPI + Flask.',
        'images': json.dumps([
            'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&q=80&w=600',
            'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=600',
            'https://images.unsplash.com/photo-1530497610245-94d3c16cda28?auto=format&fit=crop&q=80&w=600'
        ]),
        'github_url': 'https://github.com/Darshanroy/et-hackathon', 'live_url': '', 'chat_url': ''
    },
    {
        'id': 'p3',
        'name': 'InovateHub — Hackathon Platform',
        'summary': 'Backend for a multi-role hackathon management platform with RESTful APIs, JWT authentication, MongoDB data modeling, and AI-powered teammate matching.',
        'metrics': 'Built 20+ robust endpoints. Optimized for query performance across multiple concurrent hackathons serving organizer, participant, and judge workflows.',
        'architecture': 'Flask (Python) REST API covering event CRUD, team management, and submissions. Secured via stateless JWT authentication and role-based authorization.',
        'failure_handling': 'Engineered a MongoDB Atlas data layer across 7 collections with compound unique indexes, upsert operations, and ObjectId-based referential integrity to prevent data corruption.',
        'tradeoffs': 'Used MongoDB over PostgreSQL for highly flexible schema requirements inherent in varying hackathon submission structures.',
        'impact': 'Integrated Google Genkit AI for skill-based teammate matching with Zod schema validation. Containerized the full service using Docker & Docker Compose for reproducible deployment.',
        'images': json.dumps([
            'https://images.unsplash.com/photo-1504868584819-f8e905b68763?auto=format&fit=crop&q=80&w=600',
            'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80&w=600',
            'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=600'
        ]),
        'github_url': 'https://github.com/Darshanroy/inovate-hub', 'live_url': '', 'chat_url': ''
    }
]

mock_skills = [
    { 'id': 's1', 'title': 'LLM Fine-Tuning (QLoRA, PEFT)', 'type': 'skill', 'date': '', 'reading_time': '', 'sections': [] },
    { 'id': 's2', 'title': 'AI Agents (LangGraph, CrewAI)', 'type': 'skill', 'date': '', 'reading_time': '', 'sections': [] },
    { 'id': 's3', 'title': 'Vector Databases (ChromaDB, Pinecone)', 'type': 'skill', 'date': '', 'reading_time': '', 'sections': [] },
    { 'id': 's4', 'title': 'Backend APIs (Flask, FastAPI)', 'type': 'skill', 'date': '', 'reading_time': '', 'sections': [] },
    { 'id': 's5', 'title': 'Cloud & DevOps (Docker, AWS)', 'type': 'skill', 'date': '', 'reading_time': '', 'sections': [] },
    { 
      'id': 'l1', 'title': 'Orchestrating Multi-Agent Systems', 'type': 'learning', 'date': 'April 2024', 'reading_time': '10 min read', 
      'sections': [
          {'title': 'The Core Concept', 'content': 'Multi-agent systems utilize multiple specialized LLMs to break down complex tasks. By compartmentalizing logic, hallucinations are reduced and accuracy skyrockets.'},
          {'title': 'Key Logic & Patterns', 'content': 'Implementing state graphs using LangGraph to pass persistent memory between Policy, Eligibility, and Feedback agents.'},
          {'title': 'Implementation Details', 'content': 'Built a 5-agent pipeline for Jan Sahayak utilizing Agentic RAG and real-time observability via OpenTelemetry.'},
          {'title': 'Key Challenges', 'content': 'Ensuring safe outputs in a clinical or government setting. Solved via a 4-layer Guardrails AI safety architecture.'}
      ]
    },
    { 
      'id': 'b1', 'title': 'Optimizing LLMs with PEFT', 'type': 'blog', 'date': 'November 2024', 'reading_time': '8 min read',
      'sections': [
          {'title': 'The Core Thesis', 'content': 'Full fine-tuning of 3B+ parameter models requires massive VRAM. Parameter-Efficient Fine-Tuning (PEFT) is the key to local AI.'},
          {'title': 'Advanced Metrics', 'content': 'Achieved a 60% reduction in GPU memory usage compared to full fine-tuning on Qwen-3B using Amazon SageMaker.'},
          {'title': 'System Architecture', 'content': 'LoRA freezes pre-trained model weights and injects trainable rank decomposition matrices into each layer of the Transformer architecture.'},
          {'title': 'Deployment Impact', 'content': 'Successfully optimized training for K–8 educational models across 3–6 epochs.'}
      ]
    }
]

mock_achievements = [
    {
        'id': 'a1', 'title': 'AI Engineer Intern', 'issuer': 'EduGorilla Pvt. Ltd', 'date': 'Sep 2024',
        'description': 'Conducted extensive research on LLMs and implemented PEFT on Qwen-3B using AWS SageMaker, achieving 60% memory reduction.',
        'link_url': '#'
    },
    {
        'id': 'a2', 'title': 'B.S. Data Science and AI', 'issuer': 'IIT Madras', 'date': '2023 - 2027',
        'description': 'Currently pursuing a Bachelors Degree in Data Science and Artificial Intelligence with a CGPA of 8.0.',
        'link_url': '#'
    },
    {
        'id': 'a3', 'title': 'Full-Stack Hackathons', 'issuer': 'Various Platforms', 'date': '2023-2024',
        'description': 'Developed complex multi-agent architectures (Jan Sahayak, Gandivam) and hackathon backends (InovateHub) competing at high levels.',
        'link_url': 'https://github.com/Darshanroy'
    }
]

with app.app_context():
    # Clear existing data
    db.session.query(SkillSection).delete()
    db.session.query(Skill).delete()
    db.session.query(Project).delete()
    db.session.query(Achievement).delete()

    for p in mock_projects:
        project = Project(**p)
        db.session.add(project)

    for s in mock_skills:
        sections = s.pop('sections')
        skill = Skill(**s)
        db.session.add(skill)
        db.session.flush() # Get skill ID
        for sec in sections:
            db.session.add(SkillSection(skill_id=skill.id, title=sec['title'], content=sec['content']))

    for a in mock_achievements:
        db.session.add(Achievement(**a))

    db.session.commit()
    print("Mock data seeded successfully!")
