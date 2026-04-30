import json
from app import app
from models import db, Project, Skill, SkillSection, Achievement

mock_projects = [
    {
        'id': 'p1',
        'name': 'Distributed Ledger Engine',
        'summary': 'A high-performance distributed ledger engine built for high-throughput financial transactions, ensuring eventual consistency across heterogeneous nodes.',
        'metrics': 'Achieved 50k TPS with <50ms P99 latency. Horizontal scaling tested up to 128 nodes with linear performance gains.',
        'architecture': 'Event-sourced architecture with a custom consensus protocol optimized for read-heavy workloads. Uses gRPC for low-latency node communication.',
        'failure_handling': 'Implemented automatic partition recovery and state reconcile loops. Graceful degradation via circuit breakers for non-critical services.',
        'tradeoffs': 'Chose Eventual Consistency over Strong Consistency to prioritize availability during regional network partitions.',
        'impact': 'Reduced transaction processing costs by 40% and improved system uptime from 99.5% to 99.99%.',
        'images': json.dumps([
            'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&q=80&w=400',
            'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=400',
            'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80&w=400'
        ]),
        'github_url': 'https://github.com/example/ledger',
        'live_url': 'https://demo.example.com',
        'chat_url': '#'
    },
    {
        'id': 'p2',
        'name': 'AI Agent Orchestrator',
        'summary': 'A multi-agent system that coordinates complex long-running tasks by breaking them into manageable sub-goals handled by specialized LLM agents.',
        'metrics': 'Reduced task completion time by 60% compared to single-agent approaches. Successfully handled 10+ concurrent sub-tasks.',
        'architecture': 'Centralized commander with dynamic worker pool. State managed via a shared knowledge graph for context persistence.',
        'failure_handling': 'Recursive self-correction loops where agents can audit and repair each other\'s work. Fallback models for cost optimization.',
        'tradeoffs': 'Accepted higher initial latency for significantly improved final output quality and reasoning accuracy.',
        'impact': 'Automated 80% of routine customer support escalations for a pilot enterprise client.',
        'images': json.dumps([
            'https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=400',
            'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=400',
            'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=400'
        ]),
        'github_url': '', 'live_url': '', 'chat_url': ''
    },
    {
        'id': 'p3',
        'name': 'Real-time Analytics Pipeline',
        'summary': 'Cloud-native pipeline for processing millions of events per second with sub-second latency for real-time dashboarding.',
        'metrics': 'Ingesting 2.5M events/sec. E2E latency of 150ms. 99.99% data integrity guarantee.',
        'architecture': 'Kafka-centric ingestion with Flink for stream processing. Data sunk into ClickHouse for rapid querying.',
        'failure_handling': 'Replay capabilities via Kafka offsets. Dead-letter queues for schema violations.',
        'tradeoffs': 'ClickHouse chosen over Snowflake for sub-second query performance despite more complex operational overhead.',
        'impact': 'Enabled real-time fraud detection saving estimated $200k/month in losses.',
        'images': json.dumps([
            'https://images.unsplash.com/photo-1518186285589-2f7649de83e0?auto=format&fit=crop&q=80&w=400',
            'https://images.unsplash.com/photo-1504868584819-f8e905b68763?auto=format&fit=crop&q=80&w=400',
            'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=400'
        ]),
        'github_url': '', 'live_url': '', 'chat_url': ''
    }
]

mock_skills = [
    { 'id': 's1', 'title': 'Kubernetes Orchestration', 'type': 'skill', 'date': '', 'reading_time': '', 'sections': [] },
    { 'id': 's2', 'title': 'Rust Systems Programming', 'type': 'skill', 'date': '', 'reading_time': '', 'sections': [] },
    { 'id': 's3', 'title': 'PostgreSQL Internals', 'type': 'skill', 'date': '', 'reading_time': '', 'sections': [] },
    { 'id': 's4', 'title': 'gRPC & Protobuf', 'type': 'skill', 'date': '', 'reading_time': '', 'sections': [] },
    { 
      'id': 'l1', 'title': 'Distributed Systems Design', 'type': 'learning', 'date': 'March 15, 2024', 'reading_time': '12 min read', 
      'sections': [
          {'title': 'The Core Concept', 'content': 'Distributed systems are collections of independent computers that appear to users as a single coherent system. The fundamental challenge is managing state across nodes that might fail or have delayed communication.'},
          {'title': 'Key Logic & Patterns', 'content': 'Implementing Paxos and Raft consensus algorithms. Understanding the CAP theorem and when to prioritize consistency over availability.'},
          {'title': 'Implementation Details', 'content': 'Built a toy key-value store in Rust using a custom Raft implementation. Focused on membership changes and log compaction.'},
          {'title': 'Key Challenges', 'content': 'Handling network partitions where both sides think they are the leader (split-brain). Managing clock skew in Lamport timestamps.'},
          {'title': 'Future Roadmap', 'content': 'Explore move-based state transition systems and content-addressable storage for decentralized networks.'},
          {'title': 'Practical Applications', 'content': 'This knowledge is directly applicable to building global-scale databases like CockroachDB or streaming platforms like Kafka.'}
      ]
    },
    { 
      'id': 'b1', 'title': 'Low-latency JVM Tuning', 'type': 'blog', 'date': 'February 28, 2024', 'reading_time': '8 min read',
      'sections': [
          {'title': 'The Core Thesis', 'content': 'Standard JVM garbage collection is the enemy of low-latency systems. To achieve microsecond-level stability, we must avoid allocation on the hot path.'},
          {'title': 'Advanced Metrics', 'content': 'Measured P99.99 latency shifts from 20ms to 2ms by switching to the ZGC collector and using off-heap memory buffers.'},
          {'title': 'System Architecture', 'content': 'Utilizing the LMAX Disruptor pattern for inter-thread communication. Zero-copy techniques using direct ByteBuffers.'},
          {'title': 'Failure Handling', 'content': 'Managing OutOfMemory errors in off-heap pools. Implementing heartbeats that don\'t trigger safe-point pauses.'},
          {'title': 'Trade-offs', 'content': 'Manual memory management increases complexity and risk of memory leaks, but is necessary for High-Frequency Trading requirements.'},
          {'title': 'Deployment Impact', 'content': 'Successfully stabilized a matching engine processing 1M events/sec with strictly bounded latency guarantees.'}
      ]
    },
    { 
      'id': 'b2', 'title': 'Effective Error Handling in Rust', 'type': 'blog', 'date': 'January 12, 2024', 'reading_time': '6 min read',
      'sections': [
          {'title': 'Philosophy', 'content': 'Rust forces you to acknowledge error states. This is not a burden, but a blueprint for reliability.'},
          {'title': 'The Error Trait', 'content': 'Using `thiserror` and `anyhow` to build robust error hierarchies in a library vs an application.'}
      ]
    },
    { 
      'id': 'l2', 'title': 'Vector Databases Explained', 'type': 'learning', 'date': 'December 05, 2023', 'reading_time': '15 min read',
      'sections': [
          {'title': 'Summary', 'content': 'Deep dive into HNSW and IVF_flat indexing strategies for high-dimensional nearest neighbor search.'}
      ]
    }
]

mock_achievements = [
    {
        'id': 'a1', 'title': 'Top 1% Contributor: Distributed Systems', 'issuer': 'GitHub Engineering', 'date': '2023',
        'description': 'Recognized for significant contributions to core consensus logic in major open-source cloud infrastructure projects.',
        'link_url': 'https://github.com/example-certificate'
    },
    {
        'id': 'a2', 'title': 'AWS Certified Solutions Architect – Professional', 'issuer': 'Amazon Web Services', 'date': '2023',
        'description': 'Demonstrated advanced technical skills and experience in designing optimized, complex cloud solutions on AWS.',
        'link_url': '#'
    },
    {
        'id': 'a3', 'title': 'Grand Prize: Global AI Infrastructure Hackathon', 'issuer': 'NVIDIA', 'date': '2022',
        'description': 'Awarded for developing a novel scheduling algorithm that improved multi-tenant GPU utilization by 35%.',
        'link_url': None
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
