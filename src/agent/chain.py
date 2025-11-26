"""Cadena principal del agente."""
from src.agent.intents import classify_intent, Intent
from src.agent.sql_generator import generate_sql, extract_parameters
from src.agent.response_builder import build_response, format_table_response
from src.data.bigquery_client import execute_query
from src.modeling.predict import predict_campaign_roas


class MarketingAgent:
    def __init__(self):
        self.conversation_history = []
    
    def ask(self, question: str) -> dict:
        intent = classify_intent(question)
        
        if intent == Intent.PREDICTION:
            return self._handle_prediction(question)
        
        parameters = extract_parameters(question)
        sql = generate_sql(intent, parameters)
        
        try:
            data = execute_query(sql)
        except Exception as e:
            return {"response": f"Error: {str(e)}", "data": None, "sql": sql, "intent": intent.value, "success": False}
        
        response = build_response(question, data, intent.value)
        table = format_table_response(data) if not data.empty else None
        
        self.conversation_history.append({"question": question, "intent": intent.value, "response": response})
        
        return {"response": response, "table": table, "data": data.to_dict(orient="records") if not data.empty else [], "sql": sql, "intent": intent.value, "success": True}
    
    def _handle_prediction(self, question: str) -> dict:
        params = extract_parameters(question)
        campaign_id = params.get("campaign_name", "default")
        proposed_spend = params.get("budget", 1000)
        
        try:
            prediction = predict_campaign_roas(campaign_id, proposed_spend)
            response = f"""
Para la campana **{campaign_id}** con presupuesto de **${proposed_spend:,.2f}**:

ROAS Esperado: {prediction['predicted_roas']}x
Revenue Estimado: ${prediction['estimated_revenue']:,.2f}
Rango: {prediction['confidence_range']['low']}x - {prediction['confidence_range']['high']}x
"""
            return {"response": response, "data": prediction, "intent": "prediction", "success": True}
        except Exception as e:
            return {"response": f"Error al predecir: {str(e)}", "intent": "prediction", "success": False}
    
    def clear_history(self):
        self.conversation_history = []


_agent = None


def get_agent() -> MarketingAgent:
    global _agent
    if _agent is None:
        _agent = MarketingAgent()
    return _agent
