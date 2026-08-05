import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest
from src.orchestrator.graph import build_sporenet_graph, SporeNetState
from src.agents.sensor_agent import SensorAgent
from src.agents.detection_agent import DetectionAgent
from src.agents.weather_agent import WeatherAgent
from src.agents.knowledge_agent import KnowledgeAgent
from src.agents.recommendation_agent import RecommendationAgent
from src.agents.notification_agent import NotificationAgent

def test_graph_compilation():
    graph = build_sporenet_graph()
    assert graph is not None

def test_individual_agents():
    # Test SensorAgent
    s_agent = SensorAgent()
    s_res = s_agent.process({"telemetry": {"temperature": 27.5, "relative_humidity": 88.0, "leaf_wetness_hours": 24.0}})
    assert s_res["sensor_status"] == "valid"
    assert s_res["telemetry_clean"]["temperature"] == 27.5

    # Test DetectionAgent fallback
    d_agent = DetectionAgent()
    d_res = d_agent.process({"image_path": "non_existent.jpg", "spore_counts": {"magnaporthe_oryzae": 12}})
    assert d_res["detection_status"] == "complete"
    assert d_res["spore_counts"]["magnaporthe_oryzae"] == 12

    # Test WeatherAgent
    w_agent = WeatherAgent()
    w_res = w_agent.process({
        "telemetry_clean": {"temperature": 26.0, "relative_humidity": 92.0, "leaf_wetness_hours": 36.0},
        "spore_counts": {"magnaporthe_oryzae": 28, "fusarium": 5}
    })
    assert w_res["alignment_status"] == "aligned"
    assert w_res["aligned_features"]["proxy_risk_label"] == "Critical"

    # Test KnowledgeAgent
    k_agent = KnowledgeAgent()
    k_res = k_agent.process(w_res)
    assert "Rice Blast" in k_res["pathology_context"]

    # Test RecommendationAgent
    r_agent = RecommendationAgent()
    r_res = r_agent.process(k_res)
    assert r_res["risk_level"] in ["Low", "Medium", "High", "Critical"]
    assert "recommendation" in r_res

    # Test NotificationAgent
    n_agent = NotificationAgent()
    n_res = n_agent.process(r_res)
    assert n_res["notification_sent"] is True
    assert "alert_payload" in n_res

def test_end_to_end_graph_execution():
    graph = build_sporenet_graph()

    initial_state: SporeNetState = {
        "sample_id": "S-TEST-001",
        "field_id": "F01",
        "trap_id": "TRAP-A",
        "image_path": "",
        "spore_counts": {
            "magnaporthe_oryzae": 30,
            "alternaria": 2,
            "bipolaris": 1,
            "curvularia": 0,
            "curvularia_eragrostidis": 0,
            "exserohilum": 0,
            "fusarium": 4,
            "fusarium_microconidie": 0,
            "mycelium": 0
        },
        "telemetry": {
            "temperature": 27.2,
            "relative_humidity": 94.5,
            "rainfall_mm": 12.0,
            "leaf_wetness_hours": 42.0,
            "lf_fc_wet_hours": 48.0,
            "lf_fc_rain_prob": 0.85,
            "lf_fc_blast_risk_days": 5
        }
    }

    final_state = graph.invoke(initial_state)

    assert final_state["sensor_status"] == "valid"
    assert final_state["detection_status"] == "complete"
    assert final_state["alignment_status"] == "aligned"
    assert final_state["risk_level"] in ["High", "Critical"]
    assert final_state["notification_sent"] is True
    assert "alert_payload" in final_state
    assert final_state["alert_payload"]["field_id"] == "F01"
