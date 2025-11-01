# Workflow
This document summarizes the end-to-end workflow and includes simple diagrams to explain the system.

## High-level Workflow
1. Ingest job sources (boards, referrals, ATS portals)
2. Parse job descriptions and extract key requirements
3. Match candidate profile/resume to roles
4. Tailor resume and cover letter per job
5. Prepare and submit application via automation
6. Track status, outcomes, and feedback
7. Learn from outcomes to improve future applications

## Diagram: End-to-End Flow (Mermaid)

Below is the simple end-to-end workflow diagram for jobhunt, generated in Mermaid.

```mermaid
flowchart LR
    A[Job Sources] --> B[Job Parser]
    B --> C[Matching Engine]
    C --> D[ATS Tailoring]
    D --> E[Application Automator]
    E --> F[Tracker]
    F --> G[Learning Loop]
    G -- feedback --> C
```

## Diagram: System Architecture (Mermaid)

Architecture diagram below—shows decentralized, modular system flow as in the original design.

```mermaid
flowchart TB
    subgraph Client
        CLI[Typer CLI]
        UI[FastAPI UI]
    end
    subgraph Core_Services
        Parser[JD Parser]
        Matcher[Semantic Matcher]
        Tailor[ATS Tailoring]
        Automator[Playwright Automator]
        Tracker[State DB]
    end
    subgraph Data
        DB[(SQLite/PG)]
        Vstore[(FAISS/Chroma)]
        Files[[Resumes/Artifacts]]
    end
    LLM[LLM Provider(s)]
    
    CLI --> Parser
    UI --> Parser
    Parser --> Matcher
    Matcher --> Tailor
    Tailor --> Automator
    Automator --> Tracker
    Tracker --> DB
    Matcher --> Vstore
    Tailor --> Files
    Parser -- prompts --> LLM
    Matcher -- embeddings --> LLM
```
