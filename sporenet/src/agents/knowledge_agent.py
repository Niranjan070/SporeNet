"""
SporeNet Knowledge / RAG Agent
Queries domain pathology knowledge bases and agronomic documents for host-pathogen infection rules and intervention thresholds.
"""

from typing import Dict, Any

class KnowledgeAgent:
    def __init__(self, kb_path: str = None):
        self.kb_path = kb_path

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves pathology knowledge context for identified risks."""
        spore_counts = state.get("spore_counts", {})
        aligned = state.get("aligned_features", {})
        
        mo_count = spore_counts.get("magnaporthe_oryzae", 0)
        fusarium_count = spore_counts.get("fusarium", 0)
        bipolaris_count = spore_counts.get("bipolaris", 0)
        
        rules = []

        if mo_count > 0 or aligned.get("proxy_risk_label") in ["High", "Critical"]:
            rules.append(
                "Rice Blast (Magnaporthe oryzae): Spore germination occurs in dew/free water within 6-8 hours at 24-28°C (>90% RH). "
                "Appressorium formation triggers cuticular penetration. High nitrogen fertilization increases tissue susceptibility."
            )
        
        if fusarium_count > 0:
            rules.append(
                "Fusarium Species: Soilborne & foliar necrotroph causing seedling blight / bakanae. "
                "Favored by warm humid microclimates (25-32°C). Prolific microconidia dispersal."
            )
            
        if bipolaris_count > 0:
            rules.append(
                "Bipolaris oryzae (Brown Spot): Foliar lesion development correlates with potassium/silicon deficient soils and high relative humidity (>85%)."
            )

        if not rules:
            rules.append(
                "General Phytopathology: Continuous leaf wetness >12 hours at moderate temperatures (20-30°C) elevates overall foliar fungal germination risk."
            )

        pathology_context = "\n".join(rules)

        return {
            **state,
            "pathology_context": pathology_context
        }

