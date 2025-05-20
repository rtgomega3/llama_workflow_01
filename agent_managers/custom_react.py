from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context
from llama_index.core.memory import BaseMemory
from typing import List
import streamlit as st
from llama_index.core.agent.workflow.workflow_events import ToolCallResult
import time


class CustomReActAgent(ReActAgent):
    """확장된 ReActAgent"""
    
    async def handle_tool_call_results(self, ctx: Context, results: List[ToolCallResult], memory: BaseMemory) -> None:
        try:
            # 원래 메소드 호출
            await super().handle_tool_call_results(ctx, results, memory)
            
            # 웹 검색 결과 처리 테스트
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
                        
                        
                        st.session_state.initial_state["research_notes"].append(content)
                        
                       
                        print(f"저장된 research_notes 타입: {type(st.session_state.initial_state['research_notes'])}")
                        print(f"웹 검색 결과 자동 저장: {content[:min(100, len(content))]}...")
                        
        except Exception as e:
            
            print(f"도구 결과 처리 중 오류 발생: {e}")
            import traceback
            print(traceback.format_exc())