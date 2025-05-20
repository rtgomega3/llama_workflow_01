#!/usr/bin/env python3
# stop_services.py

import os
import signal
import psutil
import sys

# 색상 코드
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color

def kill_process_by_pid(pid):
    """PID로 프로세스 종료"""
    try:
        process = psutil.Process(pid)
        process.terminate()
        process.wait(timeout=5)
        return True
    except psutil.NoSuchProcess:
        return False
    except psutil.TimeoutExpired:
        process.kill()
        return True
    except Exception as e:
        print(f"Error killing process {pid}: {e}")
        return False

def kill_process_by_name(name_pattern):
    """프로세스 이름 패턴으로 종료"""
    killed = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if name_pattern in cmdline:
                proc.terminate()
                killed.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return killed

def main():
    print(f"{Colors.YELLOW}Stopping AI Research Assistant Services...{Colors.NC}")
    
    log_dir = "./logs"
    
    # PID 파일에서 프로세스 종료
    for service, pid_file in [("Setup.py", "setup.pid"), ("Streamlit", "streamlit.pid")]:
        pid_path = os.path.join(log_dir, pid_file)
        if os.path.exists(pid_path):
            try:
                with open(pid_path, 'r') as f:
                    pid = int(f.read().strip())
                
                if kill_process_by_pid(pid):
                    print(f"{Colors.GREEN}✓ {service} stopped (PID: {pid}){Colors.NC}")
                else:
                    print(f"{Colors.YELLOW}{service} was not running{Colors.NC}")
                
                os.remove(pid_path)
            except Exception as e:
                print(f"{Colors.YELLOW}Error reading {service} PID: {e}{Colors.NC}")
        else:
            print(f"{Colors.YELLOW}{service} PID file not found{Colors.NC}")
    
    # 잠재적으로 남아있는 프로세스 종료
    print(f"{Colors.YELLOW}Checking for remaining processes...{Colors.NC}")
    
    # Streamlit 프로세스
    streamlit_pids = kill_process_by_name("streamlit run app_02.py")
    if streamlit_pids:
        print(f"{Colors.GREEN}✓ Killed remaining Streamlit processes: {streamlit_pids}{Colors.NC}")
    
    # Setup.py 프로세스
    setup_pids = kill_process_by_name("python setup.py")
    if setup_pids:
        print(f"{Colors.GREEN}✓ Killed remaining setup.py processes: {setup_pids}{Colors.NC}")
    
    print(f"{Colors.GREEN}All services stopped!{Colors.NC}")

if __name__ == "__main__":
    main()