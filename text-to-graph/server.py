import json
from typing import Dict, List, Any
import spacy
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("text2graph")

def create_nlp_pipeline():
    """Create basic spaCy pipeline for entity extraction."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        print("spaCy model not found. Run: python -m spacy download en_core_web_sm")
        return None

# Initialize NLP pipeline
nlp = create_nlp_pipeline()

def extract_entities_and_relationships(text: str) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Extract both entities and relationships in one pass - no redundancy!"""
    
    # nlp is None when model is not downloaded: might mean error in config
    if nlp is None:
        # Basic fallback without spaCy
        words = text.split()
        entities = {
            "PERSON": {"count": 0, "examples": [], "description": "Person names"},
            "ORG": {"count": 0, "examples": [], "description": "Organizations"},
        }
        
        # Simple capitalized word detection
        for word in words:
            if word.istitle() and len(word) > 2:
                entities["PERSON"]["count"] += 1
                entities["PERSON"]["examples"].append(word)
        
        return entities, []  # No relationships without spaCy
    
    # Process text with spaCy
    doc = nlp(text)
    
    # Extract entities
    entities = {}
    for ent in doc.ents:
        entity_type = ent.label_
        if entity_type not in entities:
            entities[entity_type] = {
                "count": 0,
                "examples": [],
                "description": spacy.explain(entity_type) or entity_type
            }
        
        entities[entity_type]["count"] += 1
        if ent.text not in entities[entity_type]["examples"]:
            entities[entity_type]["examples"].append(ent.text)
        
        # Keep only top 5 examples per type
        entities[entity_type]["examples"] = entities[entity_type]["examples"][:5]
    
    # Extract relationships from the SAME doc (no reprocessing!)
    relationships = []
    for token in doc:
        if token.pos_ == "VERB":  # Find verbs (actions)
            # Look for subject-verb-object relationships
            subject = None
            obj = None
            
            for child in token.children:
                if child.dep_ in ["nsubj", "nsubjpass"]:  # Subject
                    subject = child
                elif child.dep_ in ["dobj", "attr", "pobj"]:  # Object
                    obj = child
            
            if subject and obj:
                # Check if both are entities
                subj_ent = None
                obj_ent = None
                
                for ent in doc.ents:
                    if ent.start <= subject.i < ent.end:
                        subj_ent = ent
                    if ent.start <= obj.i < ent.end:
                        obj_ent = ent
                
                if subj_ent and obj_ent:
                    relationships.append({
                        "from_entity": subj_ent.text,
                        "from_type": subj_ent.label_,
                        "relationship": token.lemma_.upper(),
                        "to_entity": obj_ent.text,
                        "to_type": obj_ent.label_,
                        "confidence": 0.9,
                        "source": "dependency_parsing"
                    })
    
    return entities, relationships

@mcp.tool()
async def text2schema(text: str) -> Dict[str, Any]:
    """
    Analyze text and extract graph schema.
    
    Args:
        text: The text to analyze for entities and relationships
        
    Returns:
        Dictionary with entities, relationships, and basic schema suggestions
    """
    
    if not text.strip():
        return {"error": "Empty text provided"}
    
    try:
        # Extract both entities and relationships in ONE pass
        entities, relationships = extract_entities_and_relationships(text)
        
        # Generate summary
        summary = {
            "text_length": len(text),
            "total_entities": sum(e["count"] for e in entities.values()),
            "unique_entity_types": len(entities),
            "total_relationships": len(relationships),
            "extraction_method": "dependency_parsing"
        }
        
        return {
            "entities": entities,
            "relationships": relationships,
            "summary": summary,
            "status": "success"
        }
        
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

if __name__ == "__main__":
    print("Starting text2graph MCP Server...")
    print("Tools available: analyze_text_schema")
    
    # Run the server
    mcp.run()