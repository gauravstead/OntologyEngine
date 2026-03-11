from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Global Ontology Engine API",
    description="Core orchestrator for semantic extraction and Neo4j querying.",
    version="1.0.0",
)

# Allow Next.js frontend to interact with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Global Ontology Engine backend is running."}

@app.get("/")
async def root():
    return {"message": "Welcome to the Global Ontology Engine API."}
