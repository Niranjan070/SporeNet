"""
SporeNet LangGraph Orchestration Workflow
Links the 6 agents into a stateful multi-agent DAG for automated disease risk assessment.
"""

from typing import Dict, Any, TypedDict, Optional
from langgraph.graph import StateGraph, END

from src.agents.sensor_agent import SensorAgent
from src.agents.detection_agent import DetectionAgent
from src.agents.weather_agent import WeatherAgent
from src.agents.knowledge_agent import KnowledgeAgent
from src.agents.recommendation_agent import RecommendationAgent
from src.agents.notification_agent import NotificationAgent

class SporeNetState(TypedDict, total=False):
    sample_id: str
    field_id: str
    trap_id: str
    image_path: str
    spore_counts: Dict[str, int]
    telemetry: Dict[str, Any]
    telemetry_clean: Dict[str, Any]
    sensor_status: str
    detection_status: str
    alignment_status: str
    aligned_features: Dict[str, Any]
    pathology_context: str
    risk_level: str
    shap_explanation: Dict[str, float]
    recommendation: str
    notification_sent: bool
    alert_message: str
    alert_payload: Dict[str, Any]

# Instantiate singletons for agent execution nodes
sensor_agent = SensorAgent()
detection_agent = DetectionAgent()
weather_agent = WeatherAgent()
knowledge_agent = KnowledgeAgent()
recommendation_agent = RecommendationAgent()
notification_agent = NotificationAgent()

def sensor_node(state: SporeNetState) -> SporeNetState:
    """Sensor Agent node: Validates continuous microclimate stream telemetry."""
    return sensor_agent.process(state)

def detection_node(state: SporeNetState) -> SporeNetState:
    """Detection Agent node: Runs YOLO object detection on slide images."""
    return detection_agent.process(state)

def weather_node(state: SporeNetState) -> SporeNetState:
    """Weather Agent node: Computes temporal alignment & weighted inoculum burden."""
    return weather_agent.process(state)

def knowledge_node(state: SporeNetState) -> SporeNetState:
    """Knowledge / RAG Agent node: Retrieves host-pathogen infection rules."""
    return knowledge_agent.process(state)

def recommendation_node(state: SporeNetState) -> SporeNetState:
    """Recommendation Agent node: Evaluates XGBoost risk model & SHAP attributions."""
    return recommendation_agent.process(state)

def notification_node(state: SporeNetState) -> SporeNetState:
    """Notification Agent node: Dispatches operational alerts."""
    return notification_agent.process(state)

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

