
def arch_diagram():
    return "```mermaid\ngraph TD\n  Client -->|HTTP| API[FastAPI]\n  API --> Agents\n  Agents --> DB[(PostgreSQL+pgvector)]\n```"

def sequence_auth():
    return "```mermaid\nsequenceDiagram\n  participant U as User\n  participant A as API\n  participant D as DB\n  U->>A: POST /auth/login\n  A->>D: Verify credentials\n  D-->>A: OK\n  A-->>U: JWT Token\n```"

def data_flow():
    return "```mermaid\nflowchart LR\n  CodeRepo --> Ingest --> Preprocess --> Chunk --> Embed --> RAG\n```"

def erd_example():
    return "```mermaid\nerDiagram\n  USER ||--o{ PROJECT : owns\n  PROJECT ||--o{ CODECHUNK : has\n  PROJECT ||--o{ AGENTRUN : triggers\n```"
