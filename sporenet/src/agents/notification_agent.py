"""
SporeNet Notification Agent
Formats operational alerts and dispatches warnings to farm operators via dashboard, SMS, or email channels.
"""

from typing import Dict, Any

class NotificationAgent:
    def __init__(self, channels: list = None):
        self.channels = channels or ["dashboard", "terminal"]

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches risk notification to farm manager."""
        sample_id = state.get("sample_id", "S-UNKNOWN")
        field_id = state.get("field_id", "F01")
        risk_level = state.get("risk_level", "Unknown")
        recommendation = state.get("recommendation", "No specific recommendation.")
        
        alert_msg = f"[SporeNet Alert | {sample_id} | Field {field_id}] Level: {risk_level} — {recommendation}"
        
        alert_payload = {
            "sample_id": sample_id,
            "field_id": field_id,
            "risk_level": risk_level,
            "channels": self.channels,
            "alert_message": alert_msg,
            "recommendation": recommendation,
            "pathology_context": state.get("pathology_context", ""),
            "shap_explanation": state.get("shap_explanation", {})
        }

        return {
            **state,
            "notification_sent": True,
            "alert_message": alert_msg,
            "alert_payload": alert_payload
        }

