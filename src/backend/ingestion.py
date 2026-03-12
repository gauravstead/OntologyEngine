import asyncio
import random
from typing import List, Dict

# Mock Prompts mimicking the Vertex AI 'Structured Output' requirements
EXTRACTION_SYSTEM_PROMPT = """
You are an expert intelligence extractor.
You must extract entities and relationships from the provided text strictly adhering to this JSON Schema.
Allowed Entities: [Nation, Person_Politician, Person_Military, Organization_Govt, Organization_Corporate, Military_Asset, Event_Conflict, Economic_Indicator, Technology_Sector]
Allowed Edges: [ALLIED_WITH, SANCTIONED, DEPLOYED_AT, INVESTED_IN, CRITICIZED, DEPENDENT_ON]

Output Format: Array of objects with {subject, predicate, object}.
"""

class IngestionPipeline:
    """
    Mocks the Cloud-Based Asynchronous Triage of Phase 2.1
    """
    
    def __init__(self):
        self.keywords = ["India", "Border", "Semiconductor", "Sanction", "Supply Chain"]
    
    async def mock_poll_gdelt(self) -> List[Dict]:
        """Simulate polling a news API"""
        await asyncio.sleep(0.5) # Simulate network call
        
        # Mock payloads with intentional errors to test the Critic
        return [
            {
               "source": "GDELT",
               "text": "Nation X has officially SANCTIONED the Tech Corporation Y.",
               "raw_extraction": {
                   "subject": {"canonical_name": "Nation X", "type": "Nation"},
                   "predicate": {"type": "SANCTIONED", "confidence_score": 0.95},
                   "object": {"canonical_name": "Tech Corp Y", "type": "Organization_Corporate"}
               }
            },
            {
               "source": "RSS_FEED",
               "text": "Local Politician deployed at military base.",
               # Intentional error: Politician deployed at (violates critic rules)
               "raw_extraction": {
                   "subject": {"canonical_name": "Politician Z", "type": "Person_Politician"},
                   "predicate": {"type": "DEPLOYED_AT", "confidence_score": 0.8},
                   "object": {"canonical_name": "Base Alpha", "type": "Military_Asset"}
               }
            }
        ]
