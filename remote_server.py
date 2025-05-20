from typing import List
from mcp.server.fastmcp import FastMCP
from llama_index.llms.ollama import Ollama
from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec
from llama_index.tools.brave_search import BraveSearchToolSpec
import dotenv
import os
import json
dotenv.load_dotenv()
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')

ddg_tool_spec = DuckDuckGoSearchToolSpec()

brave_tool_spec = BraveSearchToolSpec(api_key='BSAFpjzRxO0-ITXXUlQGpY8RAEQgLs6')

ollama_llm = Ollama(model=OLLAMA_MODEL, request_timeout=60.0, base_url="http://localhost:11434" )

port = 8010
mcp = FastMCP("weather", port=port)


def extract_brave_results(doc, index_offset=1):
    formatted = ""
    try:
        # ① JSON 문자열을 파싱
        if hasattr(doc, "text"):
            raw_json_str = doc.text
        elif "text_resource" in doc and "text" in doc["text_resource"]:
            raw_json_str = doc["text_resource"]["text"]
        else:
            return "[error] 텍스트 필드 없음\n"

        data = json.loads(raw_json_str)

        # ② 웹 검색 결과 가져오기
        results = data.get("web", {}).get("results", [])
        if not results:
            return "[error] 검색 결과 없음\n"

        # ③ 각 검색 결과 정리
        for i, item in enumerate(results, index_offset):
            title = item.get("title", "제목 없음")
            url = item.get("url", "링크 없음")
            desc = item.get("description", "요약 없음")

            formatted += f"{i}. {title}\n"
            formatted += f"   링크: {url}\n"
            formatted += f"   요약: {desc}\n\n"

    except Exception as e:
        formatted += f"⚠️ 파싱 실패: {e}\n"

    return formatted


# @mcp.tool()
# async def query_expansion(query: str) -> List[str]:
#     """
#     키워드 확장을 위한 Query Expansion을 수행합니다.
#     """
#     few_shot_prompt = f"""
#         검색 쿼리에서 주요 키워드를 뽑고 이를 확장하여 최대 3가지 키워드만 만드세요. 
#         콤마로 구분하여 출력하세요. 너무 일반적이지 않고 중심 키워드와 연관된 키워드여야 합니다.
        
#         예시: 
#             쿼리: 대한민국 대선
#             확장: 대통령 후보, 대한민국 대선 여론조사, 대통령 후보 지지율, 대통령 후보 정책비교

#             쿼리: 이재명
#             확장: 이재명 후보, 이재명 정책, 이재명 지지율, 이재명 여론조사


#         쿼리: "{query}"
#         확장: 
#         """
        
#     response = await ollama_llm.acomplete(few_shot_prompt)
#     expanded = response.text.strip()
    
#     # 콤마로 분리하고 각 항목의 공백 제거
#     keywords = [keyword.strip() for keyword in expanded.split(',')]
#     return keywords



from llama_index.core.workflow import (
    Context,
)
from openai import OpenAI
client = OpenAI()


@mcp.tool()
async def web_search(keyword_list: list) -> str:
    """ 키워드 리스트를 받아 키워드 별로 웹 검색을 수행합니다. 검색 결과는 영어로 되어있을 수 있으니 반드시 한국어로 번역하세요.
        호출 형식 : web_search(keyword_list=["키워드1", "키워드2", "키워드3"])
            
        Returns: 웹 검색 결과는 다음과 같습니다. 이것을 research_notes에 저장하세요.
    """   
    print(f"keyword_list : ", keyword_list)
    all_results = []  # 모든 결과를 저장할 리스트

    try:
        for keyword in keyword_list:
            print(f"키워드 {str(keyword).strip()} 검색 ===============")

            response = client.responses.create(
            model="gpt-4o-mini",
            tools=[{"type": "web_search_preview"}],
            input=f"keyword : {keyword} 검색 결과를 한국어로 번역하세요."
            )
            print(response.output_text)
            
            keyword_results = []
            keyword_results.append(f"\n### {keyword} 검색 결과\n ### {response.output_text} \n")            
            
            all_results.extend(keyword_results)
            
    except Exception as e:
        import traceback
        error_msg = f"검색 중 오류 발생: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return error_msg
    
    

    # 모든 결과를 하나의 문자열로 결합
    return "\n".join(all_results)





# @mcp.tool()
# async def web_search(keyword_list: list, max_results: int = 5) -> str:
#     """ 키워드 리스트를 받아 키워드 별로 웹 검색을 수행합니다.
#         Args:
#             keyword_list: 검색할 키워드의 리스트
            
#         Returns: 검색 결과
#     """   
#     print(f"keyword list : ", keyword_list)
#     all_results = []  # 모든 결과를 저장할 리스트

#     try:
#         for keyword in keyword_list:
#             print(f"키워드 {str(keyword).strip()} 검색 ===============")
#             results = ddg_tool_spec.duckduckgo_full_search(query=keyword, max_results=max_results)  
            
#             print(f"검색 결과 개수: {len(results)}")
            
#             # 각 키워드에 대한 결과 처리
#             keyword_results = []
#             keyword_results.append(f"\n### 키워드: {keyword}\n")
            
#             for i, item in enumerate(results, 1):
#                 title = item.get("title", "제목 없음")
#                 url = item.get("href", "링크 없음")
#                 summary = item.get("body", "요약 없음")
                
#                 result_text = f"""
#                     {i}. {title}
#                     링크: {url}
#                     요약: {summary}
#                     """
#                 keyword_results.append(result_text)
            
#             # 현재 키워드의 결과를 전체 결과에 추가
#             all_results.extend(keyword_results)
            
#     except Exception as e:
#         import traceback
#         error_msg = f"검색 중 오류 발생: {str(e)}\n{traceback.format_exc()}"
#         print(error_msg)
#         return error_msg

#     # 모든 결과를 하나의 문자열로 결합
#     return "\n".join(all_results)





# @mcp.tool()
# async def web_search(keyword_list: list, max_results: int = 5) -> str:
#     """ 키워드 리스트를 받아 키워드 별로 웹 검색을 수행합니다.
#         Args:
#             keyword_list: 검색할 키워드의 리스트
            
#         Returns: 검색 결과
#     """   
#     print(f"keyword list : ", keyword_list)
#     all_results = []  # 모든 결과를 저장할 리스트

#     try:
#         for keyword in keyword_list:
#             print(f"키워드 {str(keyword).strip()} 검색 ===============")
            
            
#             results = brave_tool_spec.brave_search(query=keyword, num_results=max_results)  
            
#             # 각 결과가 Document 객체라면, extract_brave_results 함수 사용
#             keyword_results = []
#             keyword_results.append(f"\n### 키워드: {keyword}\n")
            
#             for i, doc in enumerate(results):
#                 # extract_brave_results 함수를 사용해 Document 객체 파싱
#                 formatted_result = extract_brave_results(doc, index_offset=i)
#                 keyword_results.append(formatted_result)
            
#             all_results.extend(keyword_results)
            
#     except Exception as e:
#         import traceback
#         error_msg = f"검색 중 오류 발생: {str(e)}\n{traceback.format_exc()}"
#         print(error_msg)
#         return error_msg

#     # 모든 결과를 하나의 문자열로 결합
#     return "\n".join(all_results)


# import asyncio
# import json
# from typing import List, Optional
# import aiohttp
# from bs4 import BeautifulSoup
# from pydantic import BaseModel
# from brave_search_python_client import (
#     BraveSearch,
#     WebSearchApiResponse,
#     WebSearchRequest,
# )




# # Brave Search API 초기화 (실제 API 키로 교체하세요)
# BRAVE_API_KEY = "BSAFpjzRxO0-ITXXUlQGpY8RAEQgLs6"
# bs = BraveSearch(api_key=BRAVE_API_KEY)


# class SearchResult(BaseModel):
#     title: str
#     url: str
#     snippet: str
#     content: Optional[str] = None


# async def fetch_page_content(url: str, timeout: int = 10) -> str:
#     """웹 페이지의 전체 콘텐츠를 가져옵니다."""
#     try:
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }
        
#         async with aiohttp.ClientSession() as session:
#             async with session.get(url, headers=headers, timeout=timeout) as response:
#                 if response.status == 200:
#                     html = await response.text()
#                     soup = BeautifulSoup(html, 'html.parser')
                    
#                     # JavaScript, CSS 제거
#                     for script in soup(["script", "style"]):
#                         script.decompose()
                    
#                     # 메인 콘텐츠 영역 찾기 (일반적인 패턴)
#                     main_content = None
#                     for selector in ['main', 'article', '[role="main"]', '#content', '.content', '.post']:
#                         main_content = soup.select_one(selector)
#                         if main_content:
#                             break
                    
#                     # 메인 콘텐츠가 없으면 body 전체 사용
#                     if not main_content:
#                         main_content = soup.body if soup.body else soup
                    
#                     # 텍스트 추출
#                     text = main_content.get_text()
                    
#                     # 여러 개의 공백을 하나로 압축
#                     lines = (line.strip() for line in text.splitlines())
#                     chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
#                     text = '\n'.join(chunk for chunk in chunks if chunk)
                    
#                     return text[:10000]  # 너무 길면 잘라냄
#                 else:
#                     return f"페이지 로드 실패: HTTP {response.status}"
                    
#     except asyncio.TimeoutError:
#         return "페이지 로드 시간 초과"
#     except Exception as e:
#         return f"페이지 로드 중 오류: {str(e)}"


# async def search_brave(query: str, num_results: int = 5) -> List[SearchResult]:
#     """Brave Search API를 사용하여 검색을 수행합니다."""
#     try:
#         response = await bs.web(WebSearchRequest(q=query, count=num_results))
        
#         results = []
#         if response.web and response.web.results:
#             for result in response.web.results:
#                 search_result = SearchResult(
#                     title=result.title,
#                     url=result.url,
#                     snippet=result.description if hasattr(result, 'description') else ""
#                 )
#                 results.append(search_result)
                
#         return results
#     except Exception as e:
#         print(f"Brave 검색 오류: {str(e)}")
#         return []


# @mcp.tool()
# async def web_search(
#     keyword_list: List[str], 
#     max_results: int = 5,
#     fetch_content: bool = True
# ) -> str:
#     """키워드 리스트를 받아 웹 검색을 수행하고, 선택적으로 전체 콘텐츠를 가져옵니다.
    
#     Args:
#         keyword_list: 검색할 키워드의 리스트
#         max_results: 각 키워드당 최대 검색 결과 수
#         fetch_content: 각 결과의 전체 콘텐츠를 가져올지 여부
        
#     Returns: 검색 결과
#     """
#     all_results = []
    
#     try:
#         for keyword in keyword_list:
#             print(f"키워드 '{keyword}' 검색 중...")
            
#             # Brave Search로 검색
#             search_results = await search_brave(keyword, max_results)
            
#             keyword_results = [f"\n### 키워드: {keyword}\n"]
            
#             for i, result in enumerate(search_results, 1):
#                 result_text = f"""
#                 {i}. {result.title}
#                 링크: {result.url}
#                 요약: {result.snippet}
# """
                
#                 # 전체 콘텐츠 가져오기
#                 if fetch_content:
#                     print(f"  - {result.url} 콘텐츠 가져오는 중...")
#                     full_content = await fetch_page_content(result.url)
#                     result.content = full_content
                    
#                     # 콘텐츠 미리보기 (처음 500자)
#                     content_preview = full_content[:500] + "..." if len(full_content) > 500 else full_content
#                     result_text += f"\n   전체 콘텐츠 (미리보기):\n   {content_preview}\n"
                
#                 result_text += "\n" + "="*50 + "\n"
#                 keyword_results.append(result_text)
            
#             all_results.extend(keyword_results)
            
#     except Exception as e:
#         import traceback
#         error_msg = f"검색 중 오류 발생: {str(e)}\n{traceback.format_exc()}"
#         print(error_msg)
#         return error_msg
    
#     return "\n".join(all_results)



if __name__ == "__main__":    

        
    print(f"원격 접속 모드로 MCP 서버를 포트 {port}에서 실행함")
    mcp.run(transport="sse", )
    
    