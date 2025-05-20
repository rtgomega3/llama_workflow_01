# agent_chat_app_enhanced.py
import streamlit as st
import asyncio
import nest_asyncio
from datetime import datetime
import json
import time
import traceback
import logging
from typing import Dict, List, Any
import uuid
import pandas as pd
from css import css
from llama_index.core.workflow import Context

from llama_index.core.agent.workflow import (
    AgentOutput,
    ToolCall,
    ToolCallResult,
)

from agent_managers.agent_manager7 import AgentManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

nest_asyncio.apply()


st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(f"""
{css}
""", unsafe_allow_html=True)


class SessionState:
    @staticmethod
    def init():
        defaults = {
            "messages": [],
            "agent_workflow": None,
            "initialized": False,
            "processing": False,
            "last_activity": time.time(),
            "session_id": str(uuid.uuid4()),
            "agent_info": {
                "RootAgent": "사용자 질의 분석 및 키워드 확장",
                "ResearchAgent": "웹 검색 및 정보 수집",
                "NewsAnalysisAgent": "뉴스 분석 및 여론 분석",
                
            },
            "conversation_history": [],
            "current_research": {},
            "error_log": [],
            "user_preferences": {
                "theme": "light",
                "auto_scroll": True,
                "show_debug": False
            },
            # 실시간 상태 추가
            "current_agent": None,
            "current_tool": None,
            "agent_status": {},
            "workflow_status": "idle"
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

SessionState.init()


class UIComponents:
    @staticmethod
    def render_chat_message(message: Dict[str, Any]):
        """채팅 메시지 렌더링"""
        role = message["role"]
        content = message["content"]
        timestamp = message.get("timestamp", "")
        
        with st.chat_message(role):
            # 메시지 헤더
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"**{role.title()}**")
            with col2:
                st.caption(timestamp)
            
            # 메시지 내용
            st.markdown(content)
            
            # 추가 정보
            if "agent_log" in message and message["agent_log"]:
                with st.expander("🔍 에이전트 활동 로그", expanded=False):
                    for log_entry in message["agent_log"]:
                        if "Agent:" in log_entry:
                            st.info(log_entry)
                        elif "Tool:" in log_entry:
                            st.warning(log_entry)
                        elif "Result:" in log_entry:
                            st.success(log_entry)
                        else:
                            st.text(log_entry)

            if "state" in message and message["state"]:
                with st.expander("🔍 워크플로우 최종 상태", expanded=False):
                    st.json(message["state"])

                    
    
    @staticmethod
    def render_agent_card(agent_name: str, description: str):
        """에이전트 정보 카드 렌더링"""
        # 현재 활성 에이전트 확인
        is_active = st.session_state.current_agent == agent_name
        
        st.markdown(f"""
        <div class="status-card">
            <h4>
                <span class="agent-indicator {'agent-active' if is_active else 'agent-idle'}"></span>
                {agent_name}
            </h4>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_metric_card(label: str, value: Any, delta: Any = None):
        """메트릭 카드 렌더링"""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {f'<div class="metric-delta">{delta}</div>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)



class ChatInterface:
    """채팅 인터페이스 관리"""
    
    @staticmethod
    def render_sidebar():
        """사이드바 렌더링"""
        with st.sidebar:
            st.title("🎛️ 제어판")
            
            # 시스템 상태
            st.header("📊 시스템 상태")
            
            status_cols = st.columns(2)
            with status_cols[0]:
                status_icon = "🟢" if st.session_state.initialized else "🔴"
                status_text = "정상" if st.session_state.initialized else "미연결"
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <small style="color: #666;">연결 상태</small><br>
                    <span style="font-size: 1.2rem;">{status_icon} {status_text}</span>
                </div><br>
                """, unsafe_allow_html=True)
            
            with status_cols[1]:
                last_activity = int(time.time() - st.session_state.last_activity)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <small style="color: #666;">마지막 활동</small><br>
                    <span style="font-size: 1.2rem;">{last_activity}초 전</span>
                </div><br>
                """, unsafe_allow_html=True)
            
            # 초기화 버튼
            if st.button("시스템 재시작", type="primary", use_container_width=True):
                ChatInterface.initialize_system()
            
            st.divider()
            
            # 에이전트 목록
            st.header("🤖 에이전트 목록")
            
            for agent_name, description in st.session_state.agent_info.items():
                UIComponents.render_agent_card(
                    agent_name,
                    description
                )
            
            st.divider()
            
            # 도구 목록
            st.header("🛠️ 사용 가능한 도구")
            
            if st.session_state.initialized and st.session_state.agent_workflow:
                try:
                    llm, tools, tool_desc, _ = asyncio.run(AgentManager.initialize_agents())
                    for tool in tools:
                        st.text(f"• {tool.metadata.name}")
                    # for desc in tool_desc:
                    #     st.text(f"• {desc}")
                except Exception as e:
                    st.error(f"도구 로드 실패: {e}")
            else:
                st.info("시스템 초기화 필요")
            
            st.divider()
            
            # 설정
            with st.expander("⚙️ 고급 설정"):
                st.session_state.user_preferences["show_debug"] = st.checkbox(
                    "디버그 모드",
                    value=st.session_state.user_preferences["show_debug"]
                )
                
                st.session_state.user_preferences["auto_scroll"] = st.checkbox(
                    "자동 스크롤",
                    value=st.session_state.user_preferences["auto_scroll"]
                )
                
                if st.button("세션 초기화"):
                    st.session_state.clear()
                    st.rerun()
    
    @staticmethod
    def render_main_chat():
        """메인 채팅 인터페이스"""
        st.title("🤖 AI Research Assistant")
        st.caption("연구 및 리포트 작성 어시스턴트")
        
        st.divider()
        
        # 채팅 히스토리
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                UIComponents.render_chat_message(message)
        
        # 처리 중인 경우 실시간 상태 표시
        if st.session_state.processing and len(st.session_state.messages) > 0:
            last_message = st.session_state.messages[-1]
            if last_message["role"] == "user" and "assistant_processing" not in st.session_state:
               
                with st.chat_message("assistant"):
                    
                    status_placeholder = st.empty()
                    
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    st.session_state.assistant_processing = True
                    result = loop.run_until_complete(
                        ChatInterface.run_agent_workflow_with_status(
                            last_message["content"], 
                            status_placeholder
                        )
                    )
                    
                   
                    status_placeholder.empty()
                    
                    
                    assistant_message = {
                        "role": "assistant",
                        "content": result["content"],
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "agent_log": result.get("log", []),
                        "tools_used": result.get("tools_used", []),
                        "metadata": result.get("metadata", {}),
                        "state": result.get("state", {})
                    }
                    st.session_state.messages.append(assistant_message)
                    
                    
                    st.session_state.processing = False
                    del st.session_state.assistant_processing
                    st.rerun()
        
        
        input_container = st.container()
        with input_container:
            col1, col2 = st.columns([5, 1])
            
            with col1:
                user_input = st.chat_input(
                    "메시지를 입력하세요...",
                    key="chat_input",
                    disabled=st.session_state.processing
                )
            
            with col2:
                if st.session_state.processing:
                    st.button("처리 중...", disabled=True)
            
           
            quick_actions = st.columns(4)
            with quick_actions[0]:
                if st.button("📊 시장 분석", use_container_width=True):
                    user_input = "최신 AI 시장 동향 분석 리포트를 작성해주세요"
            with quick_actions[1]:
                if st.button("🔬 기술 리서치", use_container_width=True):
                    user_input = "최근 딥러닝 기술 발전 동향을 조사해주세요"
            with quick_actions[2]:
                if st.button("📰 뉴스 요약", use_container_width=True):
                    user_input = "오늘의 주요 기술 뉴스를 요약해주세요"
            with quick_actions[3]:
                if st.button("🌐 주식 분석", use_container_width=True):
                    user_input = "미국 주식과 한국 주식을 간략하게 분석해주세요"
        
       
        if user_input and not st.session_state.processing:
            asyncio.run(ChatInterface.process_user_input(user_input))
    
    @staticmethod
    async def process_user_input(user_input: str):
        """사용자 입력 처리"""
        try:
            st.session_state.processing = True
            st.session_state.last_activity = time.time()
            
           
            user_message = {
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "metadata": {
                    "session_id": st.session_state.session_id,
                    "message_id": str(uuid.uuid4())
                }
            }
            st.session_state.messages.append(user_message)
            
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"메시지 추가 중 오류: {e}")
            st.session_state.processing = False

    
    
    @staticmethod
    async def run_agent_workflow_with_status(user_input: str, status_placeholder) -> Dict[str, Any]:
        """에이전트 워크플로우 실행 및 실시간 상태 표시"""
        try:
            start_time = time.time()
            
            agent_log = []
            tools_used = []
            current_agent = None
            
            ctx = Context(st.session_state.agent_workflow)
            chat_history = []
            handler = st.session_state.agent_workflow.run(user_msg=user_input, chat_history=chat_history, memory=st.session_state.memory, ctx=ctx)
            
            async for event in handler.stream_events():

                # print("EVENT :", event)
                # print("*********************************")
                
                if hasattr(event, "current_agent_name") and event.current_agent_name != current_agent:
                    current_agent = event.current_agent_name
                    st.session_state.current_agent = current_agent
                    agent_log.append(f"🤖 Agent: {current_agent}")
                    
                    # 실시간 상태 업데이트
                    status_placeholder.info(f"🤖 **{current_agent}** 가 작업 중입니다...")
                
                # 에이전트 출력
                elif isinstance(event, AgentOutput):
                    if event.response.content:
                        agent_log.append(f"📤 Output: {event.response.content}...")
                    
                    if event.tool_calls:
                        for call in event.tool_calls:
                            st.session_state.current_tool = call.tool_name
                            agent_log.append(f"🛠️ Tool: {call.tool_name}")
                            tools_used.append({
                                "name": call.tool_name,
                                "args": call.tool_kwargs,
                                "result": "pending"
                            })
                            
                            # 실시간 도구 사용 표시
                            status_placeholder.warning(
                                f"🛠️ **{current_agent}** 가 **{call.tool_name}** 도구를 사용하고 있습니다..."
                            )
                
                
                elif isinstance(event, ToolCallResult):
                    agent_log.append(f"✅ Result: {event.tool_name}")
                    
                    # 도구 사용 결과 
                    for tool in tools_used:
                        if tool["name"] == event.tool_name:
                            tool["result"] = str(event.tool_output)
                    
                    if event.tool_name == "query_expansion":
                        # query_expansion 도구인 경우 결과도 함께 표시
                        status_placeholder.success(
                            f"✅ **{event.tool_name}** 도구 실행 완료"
                        )
                        
                        # 확장된 키워드 표시
                        if isinstance(event.tool_output, list):
                            keyword_display = "📝 확장된 키워드:\n" + "\n".join([f"  • {keyword}" for keyword in event.tool_output])
                            
                        else:
                            keyword_display = f"📝 확장된 키워드: {event.tool_output}"
                        
                        agent_log.append(f"✅ Result: {keyword_display}")
                        status_placeholder.info(keyword_display)

                    elif event.tool_name in ["fetch_news_documents", "web_search"]:
                        
                        result_preview = str(event.tool_output)[:500] + "..." if len(str(event.tool_output)) > 500 else str(event.tool_output)
                        st.info(f"📄 결과 미리보기: {result_preview}")
                    else:
                        # 다른 도구들은 기존 방식대로
                        status_placeholder.success(
                            f"✅ **{event.tool_name}** 도구 실행 완료"
                        )
                
                
                elif isinstance(event, ToolCall):
                    # agent_log.append(f"🔧 Calling: {event.tool_name}")
                    pass
                    
                    
                    status_placeholder.info(
                        f"🔧 **{event.tool_name}** 도구를 호출하고 있습니다..."
                    )
            
            final_response = await handler            
            execution_time = time.time() - start_time

            # initial_state에서 query_expansion_results 가져오기
            if (hasattr(st.session_state, 'initial_state') and 
                'query_expansion_results' in st.session_state.initial_state):
                query_expansion_results = st.session_state.initial_state['query_expansion_results']

            st.text("--------------------------------")
            st.info(st.session_state.agent_workflow.initial_state)
            st.text("--------------------------------")


            # 상태 초기화
            st.session_state.current_agent = None
            st.session_state.current_tool = None
            
            return {
                "content": str(final_response),
                "log": agent_log,
                "tools_used": tools_used,
                "query_expansion_results": query_expansion_results,
                "state" : st.session_state.agent_workflow.initial_state,
                
                "metadata": {
                    "execution_time": execution_time,
                    "agent_count": len(set(a.split(": ")[1] for a in agent_log if "Agent:" in a)),
                    "tool_count": len(tools_used)
                }
            }
            
        except Exception as e:
            logger.error(f"워크플로우 실행 오류: {e}")
            logger.error(traceback.format_exc())
                        
            status_placeholder.error(f"❌ 오류 발생: {str(e)}")
                        
            st.session_state.current_agent = None
            st.session_state.current_tool = None
            
            raise
    
    @staticmethod
    def initialize_system():
       
        try:
            with st.spinner("시스템을 초기화하는 중..."):
                # 비동기 초기화 실행
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                llm, tools, tool_desc, mcp_connected = loop.run_until_complete(
                    AgentManager.initialize_agents()
                )
                
                
                st.session_state.agent_workflow, st.session_state.memory = AgentManager.create_workflow(
                    llm, tools, tool_desc
                )
                
                
                st.session_state.initialized = True
                st.success("시스템 초기화 완료")
                
                if mcp_connected:
                    st.success("MCP 서버 연결됨")
                else:
                    st.warning("MCP 서버 미연결 - 제한된 기능")
                
                st.session_state.messages.append({
                    "role": "system",
                    "content": "무엇을 도와드릴까요?",
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "metadata": {
                        "mcp_connected": mcp_connected,
                        "tools_count": len(tools)
                    }
                })
                
                st.rerun()
                
        except Exception as e:
            logger.error(f"시스템 초기화 실패: {e}")
            logger.error(traceback.format_exc())
            st.error(f"초기화 실패: {str(e)}")
            
            if st.session_state.user_preferences.get("show_debug", False):
                with st.expander("🐛 디버그 정보"):
                    st.code(traceback.format_exc())

def main():
    ChatInterface.render_sidebar()
   
    if not st.session_state.initialized:
        st.info("👈 왼쪽 사이드바에서 '시스템 재시작' 버튼을 눌러 초기화하세요.")
        ChatInterface.initialize_system()
    else:
        ChatInterface.render_main_chat()
    
    
    if st.session_state.user_preferences.get("auto_scroll", True):
        st.markdown(
            "<script>window.scrollTo(0, document.body.scrollHeight);</script>",
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"애플리케이션 오류: {e}")
        logger.error(traceback.format_exc())
        st.error("오류가 발생했습니다.")
        
        if st.session_state.user_preferences.get("show_debug", False):
            st.code(traceback.format_exc())
        
        if st.button("앱 재시작"):
            st.session_state.clear()
            st.rerun()