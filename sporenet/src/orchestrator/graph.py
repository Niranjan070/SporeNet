"""
SporeNet LangGraph Orchestration Workflow
Links the 6 agents into a stateful multi-agent DAG for automated disease risk assessment.
"""

from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END

class SporeNetState(TypedDict):
    sample_id: str
    field_id: str
    image_path: str
    spore_counts: Dict[str, int]
    telemetry: Dict[str, Any]
    aligned_features: Dict[str, Any]
    pathology_context: str
    risk_level: str
    recommendation: str
    notification_sent: bool

def sensor_node(state: SporeNetState) -> SporeNetState:
    # Sensor Agent node
    return {**state}

def detection_node(state: SporeNetState) -> SporeNetState:
    # Detection Agent node
    return {**state}

def weather_node(state: SporeNetState) -> SporeNetState:
    # Weather Agent node
    return {**state}

def knowledge_node(state: SporeNetState) -> SporeNetState:
    # Knowledge / RAG Agent node
    return {**state}

def recommendation_node(state: SporeNetState) -> SporeNetState:
    # Recommendation Agent node
    return {**state}

def notification_node(state: SporeNetState) -> SporeNetState:
    # Notification Agent node
    return {**state, "notification_sent": True}

def build_sporenet_graph():
    """Constructs the 6-agent LangGraph workflow."""
    builder = StateGraph(SporeNetState)
    
    builder.add_node("sensor", sensor_node)
    builder.add_node("detection", detection_node)
    builder.add_node("weather", weather_node)
    builder.add_node("knowledge", knowledge_node)
    builder.add_node("recommendation", recommendation_node)
    builder.add_node("notification", notification_node)

    builder.set_entry_point("sensor")
    builder.add_edge("sensor", "detection")
    builder.add_edge("detection", "weather")
    builder.add_edge("weather", "knowledge")
    builder.add_edge("knowledge", "recommendation")
    builder.add_edge("recommendation", "notification")
    builder.add_edge("notification", END)

    return builder.compile()
