css = '''
<style>
/* 메인 컨테이너 스타일 */
.main-container {
    max-width: 1200px;
    margin: 0 auto;
}

/* 채팅 메시지 스타일 */
.chat-message {
    padding: 1rem 1.5rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    animation: fadeIn 0.5s ease-in;
}

.user-message {
    background-color: #e3f2fd;
    margin-left: 2rem;
}

.assistant-message {
    background-color: #f5f5f5;
    margin-right: 2rem;
}

/* 상태 카드 스타일 */
.status-card {
    background: white;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
    color: black;
}

/* 에이전트 활동 인디케이터 */
.agent-indicator {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 8px;
}

.agent-active {
    background-color: #4caf50;
    animation: pulse 1.5s infinite;
}

.agent-idle {
    background-color: #9e9e9e;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* 도구 카드 스타일 */
.tool-card {
    background: #f8f9fa;
    border-left: 4px solid #2196f3;
    padding: 0.5rem 1rem;
    margin-bottom: 0.5rem;
    border-radius: 4px;
}

/* 메트릭 카드 */
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
}

.metric-value {
    font-size: 2rem;
    font-weight: bold;
}

.metric-label {
    font-size: 0.875rem;
    opacity: 0.9;
}

/* 스피너 커스터마이징 */
.stSpinner > div {
    border-color: #667eea !important;
}
</style>
'''