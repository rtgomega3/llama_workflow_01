import asyncio
from app.local_tools import query_expansion, save_report, record_search_result
import streamlit as st

# Initialize st.session_state properly
if not hasattr(st, 'session_state'):
    st.session_state = {}
st.session_state.initial_state = {
    'research_notes': [],
    'query_expansion_results': [],
    'report_content': ''
}
st.session_state.query_expansion_results = []
st.session_state.final_reports = ''

async def test_query_expansion():
    print("Testing query_expansion...")
    result = await query_expansion("이재명")
    print(f"Expanded query: {result}")
    return result

async def test_record_search_result():
    print("Testing record_search_result...")
    result = await record_search_result("Test search result")
    print(f"Result: {result}")
    return result

async def test_save_report():
    print("Testing save_report...")
    result = await save_report("Test report content")
    print(f"Result: {result}")
    return result

async def main():
    try:
        await test_query_expansion()
        await test_record_search_result()
        await test_save_report()
        print("All tests completed successfully!")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 