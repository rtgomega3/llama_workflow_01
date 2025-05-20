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
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.core.memory import BaseMemory
from llama_index.core.agent.workflow import ReActAgent, AgentWorkflow
from llama_index.core.tools import FunctionTool
from llamaindex_mcp_adapter import MCPToolAdapter
from mcp_client import MCPClient
from logger_config import setup_logger
import dotenv
import os
from llama_index.llms.anthropic import Anthropic
from prompts import REPORT_WRITING_PROMPT
from llama_index.core.workflow import Context
from llama_index.core.memory import Memory
from llama_index.core.agent.workflow.workflow_events import AgentSetup, AgentOutput
from llama_index.core.workflow import Context, step
from llama_index.core.llms import ChatMessage
from llama_index.core.memory import Memory
from .custom_react import CustomReActAgent
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .prompts import ROOT_PROMPT_TEMPLATE, NEWS_ANALYSIS_PROMPT_TEMPLATE, RESEARCH_PROMPT_TEMPLATE
from tool_desc import *
from llama_index.core.bridge.pydantic import PrivateAttr


dotenv.load_dotenv()
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')
ollama_llm = Ollama(model=OLLAMA_MODEL, request_timeout=60.0, base_url="http://localhost:11434" )



# logger = setup_logger(__name__)
import nest_asyncio
nest_asyncio.apply() 

   


class AgentManager:
    """
    에이전트 관리 클래스
    * @staticmethod 중 record_search_result, query_expansion는 직접 정의한 도구로 mcp 툴 목록과 함께 tool list로 병합됨. 추후 별개 파일로 분리예정
    
    """
   

    @staticmethod
    async def record_search_result(result:str) -> str:
        """검색 결과 기록"""
    
        
        if "research_notes" not in st.session_state.initial_state:
            st.session_state.initial_state["research_notes"] = []
        
        st.session_state.initial_state["research_notes"].append(result)
        return f"노트 기록 완료"

    @staticmethod
    async def query_expansion(query:str) -> List[str]:

        """
        키워드 확장을 위한 Query Expansion을 수행합니다.
        """
        few_shot_prompt = f"""
            검색 쿼리에서 주요 키워드를 뽑고 이를 확장하여 최대 3가지 키워드만 만드세요. 
            콤마로 구분하여 출력하세요. 너무 일반적이지 않고 중심 키워드와 연관된 키워드여야 합니다.
            
            예시: 
                쿼리: 대한민국 대선
                확장: 대통령 후보, 대선 여론조사, 대통령 후보 지지율, 대통령 후보 정책비교

                쿼리: 이재명
                확장: 이재명 후보, 이재명 정책, 이재명 지지율, 이재명 여론조사

                쿼리: 치즈 만드는법
                확장: 치즈 만드는 방법, 치즈 생산과정, 수제 치즈 만드는법, 모짜렐라 치즈 만드는법, 크림치즈 만드는법, 간단한 치즈 만드는법



            쿼리: "{query}"
            확장: 
            """
        

        print(f"Query Expansion 진행: {query}")
        response = await ollama_llm.acomplete(few_shot_prompt)
        expanded = response.text.strip()       
        keywords = [keyword.strip() for keyword in expanded.split(',')]

        if "query_expansions" not in st.session_state:
            st.session_state.query_expansion_results = []
        
        st.session_state.query_expansion_results.append(keywords)
        st.session_state.initial_state["query_expansion_results"] = keywords
        return keywords



    from llama_index.core.base.agent.types import Task
    @staticmethod
    async def crawl_public_opinion() -> str:
        """mcp 툴 warpping - get_date_range 도구를 먼저 호출한 뒤 뉴스 수집 도구 호출, 댓글 수집 도구 호출"""
        # client = MCPClient("http://127.0.0.1:8112/sse")
        # adapter = MCPToolAdapter(client)
        # result = await client.call_tool('fetch_news_documents')
        # result = await client.call_tool('fetch_news_comments_by_article_id_list')
        # print(result)
        pass
        
                
    
    @staticmethod
    async def initialize_agents():
        """에이전트 초기화 및 로컬/MCP 도구 로드"""

        # print("에이전트 초기화 시작")
        try:
            
            ollama_llm = Ollama(
                model=OLLAMA_MODEL,
                request_timeout=60.0,
                base_url="http://localhost:11434"
            )

            # ollama_llm = OpenAI(model="gpt-4o", temperature=0.0)
            # ollama_llm = Anthropic(model="claude-3-7-sonnet-latest")
            
            # 직접 정의한 도구들
            record_search_result_tool = FunctionTool.from_defaults(
                fn=AgentManager.record_search_result,
                description="검색 결과를 기록합니다"
            )

            query_expansion_tool = FunctionTool.from_defaults(
                fn=AgentManager.query_expansion,
                description="쿼리 확장을 위한 Query expansion 수행"
            )

            
            # crawl_public_opinion_tool = FunctionTool.from_defaults(
            #     fn=AgentManager.crawl_public_opinion,
            #     description="의견 수집"
            # )
            
            # save_report_tool = FunctionTool.from_defaults(
            #     fn=AgentManager.save_report,
            #     description="최종 리포트를 저장합니다"
            # )
            
            
            tools = [record_search_result_tool, query_expansion_tool, ] # crawl_public_opinion_tool
            mcp_connected = False
            
            try:
                client = MCPClient("http://127.0.0.1:8010/sse")
                adapter = MCPToolAdapter(client)
                mcp_tools = await adapter.list_tools()

                client2 = MCPClient("http://127.0.0.1:8112/sse")
                adapter2 = MCPToolAdapter(client2)
                mcp_tools2 = await adapter2.list_tools()

                # list_tools에서 함수에 정의된 설명을 모두 가져오지 못해 수동으로 추가함
                for tool in mcp_tools2:
                    if tool.metadata.name == 'get_date_range':
                        tool.metadata.description = get_date_range_description
                    if tool.metadata.name == 'fetch_news_documents':
                        tool.metadata.description = fetch_news_documents_description
                    if tool.metadata.name == 'fetch_news_comments_by_article_id_list':
                        tool.metadata.description = fetch_news_comments_by_article_id_list_description
                    if tool.metadata.name == 'fetch_keyword_frequency':
                        tool.metadata.description = fetch_keyword_frequency_description
               
                
                tools.extend(mcp_tools)
                tools.extend(mcp_tools2)

                mcp_connected = True
                print(f"MCP 연결 성공. 총 {len(tools)} 개의 도구 사용 가능")
                print(f"MCP 도구 목록: {[tool.metadata.name for tool in tools if hasattr(tool, 'metadata')]}")
            except Exception as e:
                print(f"MCP 연결 실패: {e}")
                st.warning(f"MCP 서버 연결 실패: {e}")
            
            
            tool_desc = []
            for tool in tools:
                if hasattr(tool, 'metadata'):
                    desc = f"{tool.metadata.name}: {tool.metadata.description}"
                    tool_desc.append(desc)
                    
                else:
                    print(f"메타데이터 없는 도구: {tool}")
                       
            
            return ollama_llm, tools, tool_desc, mcp_connected
            
        except Exception as e:
            print(f"에이전트 초기화 실패: {e}")
            print(traceback.format_exc())
            raise


    @staticmethod
    async def access_chat_history(ctx: Context):
        ''' 테스트 중인 코드 '''
        
        memory: BaseMemory = await ctx.get("memory")        
        
        chat_history = await memory.aget()
                
        return chat_history  
        
    
    


    @staticmethod
    def create_workflow(llm, tools, tool_desc):
        """워크플로우 생성"""
                             

        # docs 발췌 : Lastly, there are cases (like human-in-the-loop) where you will need to provide both the Context (to resume the workflow) and the Memory (to store the chat history). 
        memory = Memory.from_defaults(session_id="my_session", token_limit=40000)
        chat_history = []

        root_llm = Ollama(model=OLLAMA_MODEL, base_url="http://localhost:11434", temperature=0.1, request_timeout=30.0)
        root_agent = CustomReActAgent(
            name="RootAgent",
            description="사용자 질의를 분석하여 적절한 에이전트를 사용자에게 추천하세요.",
            memory=memory,
            system_prompt=ROOT_PROMPT_TEMPLATE.format(
                tools='\n'.join(tool_desc),
                report_writing_prompt=REPORT_WRITING_PROMPT
            ),
            llm=root_llm,
            tools=tools,  
            verbose=True,
            can_handoff_to=["ResearchAgent", "NewsAnalysisAgent"],
            
        )

        news_analysis_agent = CustomReActAgent(
            name="NewsAnalysisAgent",
            description="쿼리를 확장하여 뉴스 분석, 여론 분석, 빈도수 분석 후 리포트 생성",
            system_prompt=NEWS_ANALYSIS_PROMPT_TEMPLATE.format(
                tools='\n'.join(tool_desc),
                report_writing_prompt=REPORT_WRITING_PROMPT
            ),
            llm=llm,
            tools=tools,
            verbose=True,
            can_handoff_to=[]  
        )

        


        research_agent = CustomReActAgent(
            name="ResearchAgent",
            description="쿼리를 확장하여 웹 검색을 통한 리포트 생성",
            system_prompt=RESEARCH_PROMPT_TEMPLATE.format(
                tools='\n'.join(tool_desc),
                report_writing_prompt=REPORT_WRITING_PROMPT
            ),
            llm=llm,
            tools=tools,
            verbose=True,
            can_handoff_to=[] 
        )

        

        
        initial_state = {
            "research_notes": {},
            "query_expansion_results": [],
            "report_content": "",
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "session_id": st.session_state.session_id
            }
        }
        
        st.session_state.initial_state = initial_state

        if "last_workflow_state" in st.session_state:
            initial_state = st.session_state.last_workflow_state
        else:
            initial_state = {
                "research_notes": [],
                "query_expansion_results": [],
                "report_content": "",
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "session_id": st.session_state.session_id
                }
            }

                             
        workflow = AgentWorkflow(
            agents=[root_agent, news_analysis_agent, research_agent], # root_agent, research_agent, 
            root_agent=root_agent.name,
            initial_state=initial_state,
            # handoff_prompt=HANDOFF_PROMPT,  
            # handoff_output_prompt=HANDOFF_OUTPUT_PROMPT, 
        )

        
        
        
        return workflow, memory