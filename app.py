import streamlit as st
import asyncio

from graph import create_newsletter_graph

st.title("AI News Letter Generator")

keyword = st.text_input("뉴스레터의 키워드를 입력해주세요!")
if keyword.strip() == "":
    st.warning("키워드 입력 필요!")
    st.stop()


async def run_graph(inputs):
    graph = create_newsletter_graph()

    status_container = st.container()   # 프로그레스 생성 컨테이너

    with status_container:
        col1, col2 = st.columns([2,1])
        with col1:
            status_text = st.empty()
        with col2:
            progress_bar = st.progress(0)

        with st.expander("Detailed Progress", expanded=True):
            search_status = st.empty()
            theme_status = st.empty()
            subtheme_status = st.empty()
            write_status = st.empty()
            aggregate_status = st.empty()
            edit_status = st.empty()
    
    step = 0
    totla_steps = 10

    try:
        async for output in graph.astream(inputs):
            for key, value in output.items():
                step += 1
                progress_bar.progress(step / totla_steps)
                status_text.text(f"현재 실행중인 노드 : {key}")

                if key == "search_news":
                    search_status.success("✓ 뉴스 검색 Completed")
                elif key == "generate_theme":
                    theme_status.success("✓ 주제 생성 Completed")
                elif key == "search_sub_themes":
                    subtheme_status.success("✓ 소주제 관련 내용 검색 Completed")
                elif key.startswith("write_section"):
                    write_status.success(f"✓ Section {key[-1]} 작성됨")
                elif key == "aggregate":
                    aggregate_status.success("✓ 내용 종합 Completed")
                    # Show draft in status container
                    with st.expander("Draft Newsletter", expanded=False):
                        st.markdown(value['messages'][0].content)
                elif key == "editor":
                    edit_status.success("✓ 최종 편집 Completed")
                    # Show final result outside status container
                    st.markdown("## Final Newsletter")
                    st.markdown(value['messages'][0].content)

        status_text.success("Newsletter generation completed!")
    except Exception as e:
        status_text.error("Newsletter generation failed.")
        with st.expander("Error Details"):
            st.error(f"An error occurred: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

if st.button("뉴스레터 생성하기"):
    inputs = {"keyword": keyword}
    asyncio.run(run_graph(inputs))
