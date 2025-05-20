#!/usr/bin/env python3
# start_services.py

import subprocess
import time
import os
import sys
from datetime import datetime
import signal
import psutil

# 색상 코드
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def create_log_dir():
    """로그 디렉토리 생성"""
    log_dir = "./logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir

def start_service(command, log_file, service_name):
    """서비스 백그라운드 실행"""
    try:
        process = subprocess.Popen(
            command,
            # stdout=open(log_file, 'w'),
            # stderr=subprocess.STDOUT,
            shell=True,
            preexec_fn=os.setsid
        )
        print(f"{Colors.GREEN}✓ {service_name} started (PID: {process.pid}){Colors.NC}")
        return process.pid
    except Exception as e:
        print(f"{Colors.RED}Failed to start {service_name}: {e}{Colors.NC}")
        return None

def main():
    print(f"{Colors.GREEN}Starting AI Research Assistant Services...{Colors.NC}")
    
    # 로그 디렉토리 생성
    log_dir = create_log_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Setup.py 실행
    print(f"{Colors.YELLOW}Starting MCP servers and Ollama...{Colors.NC}")
    setup_log = os.path.join(log_dir, f"setup_{timestamp}.log")
    setup_pid = start_service("python setup.py", setup_log, "Setup.py")
    
    if setup_pid:
        with open(os.path.join(log_dir, "setup.pid"), 'w') as f:
            f.write(str(setup_pid))
    
    # 초기화 대기
    print("Waiting for services to initialize...")
    time.sleep(10)
    
    # 2. Streamlit 앱 실행
    print(f"{Colors.YELLOW}Starting Streamlit app...{Colors.NC}")
    streamlit_log = os.path.join(log_dir, f"streamlit_{timestamp}.log")
    streamlit_pid = start_service("streamlit run app_03.py", streamlit_log, "Streamlit")
    
    if streamlit_pid:
        with open(os.path.join(log_dir, "streamlit.pid"), 'w') as f:
            f.write(str(streamlit_pid))
    
    print(f"{Colors.GREEN}All services started successfully!{Colors.NC}")
    print(f"{Colors.YELLOW}Logs are saved in: {log_dir}{Colors.NC}")
    print(f"{Colors.YELLOW}Setup log: {setup_log}{Colors.NC}")
    print(f"{Colors.YELLOW}Streamlit log: {streamlit_log}{Colors.NC}")
    
    # 프로세스 상태 확인
    time.sleep(2)
    print(f"\n{Colors.GREEN}Process Status:{Colors.NC}")
    
    for service, pid in [("Setup.py", setup_pid), ("Streamlit", streamlit_pid)]:
        try:
            if pid and psutil.pid_exists(pid):
                print(f"{service}: {Colors.GREEN}Running{Colors.NC} (PID: {pid})")
                if service == "Streamlit":
                    print(f"\n{Colors.GREEN}Streamlit is available at: http://localhost:8501{Colors.NC}")
            else:
                print(f"{service}: {Colors.RED}Not Running{Colors.NC}")
        except:
            print(f"{service}: {Colors.RED}Status Unknown{Colors.NC}")
    
    print(f"\nTo stop services, run: {Colors.YELLOW}python stop_services.py{Colors.NC}")

if __name__ == "__main__":
    main()