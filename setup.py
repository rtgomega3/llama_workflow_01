#!/usr/bin/env python3

import subprocess
import time
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import threading
import dotenv
import os
dotenv.load_dotenv()
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')
BRAVE_SEARCH_API_KEY = 'BSAFpjzRxO0-ITXXUlQGpY8RAEQgLs6'




def run_mcp_server(mcp_path):
    """MCP 서버 실행"""
    print(f"[MCP] 서버 시작: {mcp_path}")
    subprocess.run([sys.executable, mcp_path])

def run_ollama_model(model_name):
    """OLLAMA 모델 실행"""
    print(f"[OLLAMA] 모델 시작: {OLLAMA_MODEL}")
    subprocess.run(["ollama", "run", OLLAMA_MODEL])

def setup_llamaindex():
    """LlamaIndex 설정"""
    time.sleep(8)  # 서비스들이 시작될 때까지 대기
    
    try:
        from llama_index.llms.ollama import Ollama
        from llama_index.core import Settings
        
        # Ollama LLM 설정
        llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0)
        Settings.llm = llm
        
        print("[LlamaIndex] 에이전트가 준비되었습니다!")
        
        # 여기에 실제 에이전트 코드 추가
        # agent = YourAgent()
        # agent.run()
        
    except Exception as e:
        print(f"[LlamaIndex] 초기화 실패: {e}")

def main():
    # 설정
    MCP_SERVER_PATH = "./remote_server.py"  # 실제 경로로 변경
    
    
    # 스레드 풀을 사용해 동시 실행
    with ThreadPoolExecutor(max_workers=3) as executor:
        # MCP 서버 실행
        mcp_future = executor.submit(run_mcp_server, MCP_SERVER_PATH)
        
        # OLLAMA 모델 실행
        ollama_future = executor.submit(run_ollama_model, OLLAMA_MODEL)
        
        # LlamaIndex 설정 (별도 스레드)
        llamaindex_future = executor.submit(setup_llamaindex)
        
        # 모든 작업이 완료될 때까지 대기
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n프로그램 종료 중...")
            executor.shutdown(wait=False)

if __name__ == "__main__":
    main()