from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context
from llama_index.core.memory import BaseMemory
import streamlit as st
from typing import Callable, List, Sequence, Optional, Union, Any
from llama_index.core.agent.workflow.workflow_events import ToolCallResult
import time
from .custom_events import WebSearchResultEvent, QueryExpansionResultEvent
from llama_index.core.workflow.checkpointer import CheckpointCallback
from llama_index.core.workflow.handler import WorkflowHandler
from llama_index.core.agent.workflow import AgentOutput
from llama_index.core.agent.react.types import (
    ActionReasoningStep,
    BaseReasoningStep,
    ObservationReasoningStep,
    ResponseReasoningStep,
)
from llama_index.core.llms import ChatMessage

class CustomReActAgent(ReActAgent):
    """ReActAgent 상속"""

    
    async def handle_tool_call_results(self, ctx: Context, results: List[ToolCallResult], memory: BaseMemory) -> None:
        try:
            
            await super().handle_tool_call_results(ctx, results, memory)
            
            # 웹 검색 결과 처리
            for tool_call_result in results:
                
                if tool_call_result.tool_name == "web_search":
                    if "research_notes" not in st.session_state.initial_state:
                        st.session_state.initial_state["research_notes"] = []
                    elif isinstance(st.session_state.initial_state["research_notes"], dict):
                        old_notes = st.session_state.initial_state["research_notes"]
                        st.session_state.initial_state["research_notes"] = list(old_notes.values())
                                       
                    if tool_call_result.tool_output:
                        content = tool_call_result.tool_output                        

                        if hasattr(content, 'content'):
                            content = content.content
                                
                        if not isinstance(content, str):
                            content = str(content)
                            
                        # 워크플로우 이벤트로 웹 검색 결과 전달                        
                        ctx.write_event_to_stream(WebSearchResultEvent(content=content))

                elif tool_call_result.tool_name == "query_expansion":
                    print("쿼리 확장 결과 처리 중...")
                    
                    if "query_expansion_results" not in st.session_state.initial_state:
                        st.session_state.initial_state["query_expansion_results"] = []
                    
                    if tool_call_result.tool_output:
                        content = tool_call_result.tool_output
                        
                        # ToolOutput 객체 처리
                        if hasattr(content, 'content'):
                            content = content.content
                        
                        if isinstance(content, str):
                            try:
                                # 쉼표로 구분된 문자열인 경우 리스트로 변환
                                content = [item.strip() for item in content.split(',')]
                            except:
                                content = [content]
                        
                        if not isinstance(content, list):
                            content = [content]
                        
                        # 세션 상태에 저장
                        st.session_state.initial_state["query_expansion_results"] = content
                        print(f"쿼리 확장 결과 저장: {content}")
                        
                        ctx.write_event_to_stream(QueryExpansionResultEvent(content=content))
                        print(f"쿼리 확장 결과 이벤트 발행: {content}")
                    
                        
        except Exception as e:
            
            print(f"도구 결과 처리 중 오류 발생: {e}")
            import traceback
            print(traceback.format_exc())