from llama_index.core.agent.workflow.workflow_events import Event

class WebSearchResultEvent(Event):
    """웹 검색 결과 이벤트"""
    content: str
    
class QueryExpansionResultEvent(Event):
    """쿼리 확장 결과 이벤트"""
    content: list[str]

