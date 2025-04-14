import os
import streamlit as st
from dotenv import load_dotenv
from utils.state import State
from tavily import TavilyClient, AsyncTavilyClient

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
tavily_api_key = os.getenv('TAVILY_API_KEY')

if not openai_api_key or not tavily_api_key:
    raise ValueError("API KEY가 설정되지 않았습니다.")

# 대주제 뉴스 검색
def search_recent_news(keyword: str) -> list:
    try:
        client = TavilyClient(api_key=tavily_api_key)
        search_result = client.search(
            query=keyword,
            max_results=5,
            topic="news",
            days=5
        )
        titles = [result['title'] for result in search_result['results']]
        return titles
    except Exception as e:
        st.error(f"뉴스 검색 중 오류가 발생했습니다: {str(e)}")
        return []

# 소주제 뉴스 검색 함수
async def search_news_for_subtheme(subtheme: str):
    try:
        async_tavily_client = AsyncTavilyClient(api_key=tavily_api_key)
        search_params = {
            "query": subtheme, 
            "max_results": 5,  # 결과 수 증가
            "topic": "news", 
            "days": 30,  # 검색 기간 확장
            "include_images": True,
            "include_raw_content": True,
            "search_depth": "advanced"  # 더 깊은 검색 수행
        }
        with st.status(label=f"'{subtheme}'와 관련된 뉴스 검색중...", expanded=True) as status:
            st.markdown(f"'{subtheme}'와 관련된 뉴스를 검색하고 있습니다.")
            response = await async_tavily_client.search(**search_params)
            images = response.get('images', [])
            results = response.get('results', [])
        
            if not results:
                st.warning(f"'{subtheme}'에 대한 검색 결과가 없습니다.")
                return {subtheme: []}
            
            article_info = []
            for i, result in enumerate(results):
                article_info.append({
                    'title': result.get('title', ''),
                    'image_url': images[i] if i < len(images) else '',
                    'raw_content': result.get('raw_content', '')
                })
        
            status.update(
                label=f"'{subtheme}'와 관련된 {len(article_info)}개의 기사를 찾았습니다.",
                state='complete',
                expanded=False
                )
        return {subtheme: article_info}
    except Exception as e:
        st.error(f"서브테마 '{subtheme}' 검색 중 오류가 발생했습니다: {str(e)}")
        return {subtheme: []} 
