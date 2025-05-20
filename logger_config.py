# logger_config.py
import logging
import sys

def setup_logger(name=__name__, level=logging.DEBUG):
    """공통 로거 설정"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # 파일 핸들러 (선택사항)
    file_handler = logging.FileHandler('agent_app.log')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 중복 핸들러 방지
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger

# 기본 로거 설정
root_logger = setup_logger('agent_app')