import streamlit as st
import tempfile
import os
from src.ingestion import load_document, split_text
from src.retriever import create_index
from src.generator import GigaChatRAG
from src.evaluator import evaluate_answer

st.set_page_config(page_title="RAG System", layout="wide")
st.title("RAG: Поиск по документации")

if 'rag' not in st.session_state:
    st.session_state.rag = None


def display_metrics(metrics, prefix=""):
    col1, col2, col3 = st.columns(3)
    col1.metric(f"{prefix}Faithfulness", f"{metrics['faithfulness']:.2f}")
    col2.metric(f"{prefix}Relevancy", f"{metrics['relevancy']:.2f}")
    col3.metric(f"{prefix}Precision", f"{metrics['precision']:.2f}")


with st.sidebar:
    st.header("Загрузка документа")
    uploaded_file = st.file_uploader("PDF или DOCX", type=["pdf", "docx"])
    
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        with st.spinner("Обработка..."):
            doc = load_document(tmp_path)
            chunks = split_text(doc["content"], chunk_size=1000, overlap=200)
            collection = create_index(chunks, doc["source"])
            st.session_state.rag = GigaChatRAG(collection)
            st.success("Готово!")
        
        os.remove(tmp_path)

if st.session_state.rag:
    st.subheader("Задать вопрос по документу")
    query = st.chat_input("Ваш вопрос...")
    
    if query:
        with st.chat_message("user"):
            st.write(query)
        
        with st.chat_message("assistant"):
            with st.spinner("Генерация ответа..."):
                result = st.session_state.rag.ask(query)
                st.write(result["answer"])
                
                if result["sources"]:
                    with st.expander("Источники"):
                        for i, src in enumerate(result["sources"], 1):
                            st.write(f"**Источник {i}:** {src}")
                
                metrics = evaluate_answer(result["answer"], result["contexts"], query)
                st.caption(
                    f"Метрики: Faithfulness={metrics['faithfulness']}, "
                    f"Relevancy={metrics['relevancy']}, "
                    f"Precision={metrics['precision']}"
                )
    
    st.divider()
    st.subheader("Оценка качества системы")
    
    if st.button("Запустить тест"):
        test_questions = [
            "Что это за документ?",
            "Как использовать?",
            "Какие есть требования?"
        ]
        
        with st.spinner("Тестирование..."):
            results = []
            for q in test_questions:
                result = st.session_state.rag.ask(q)
                metrics = evaluate_answer(result["answer"], result["contexts"], q)
                results.append(metrics)
            
            avg_metrics = {
                "faithfulness": sum(r["faithfulness"] for r in results) / len(results),
                "relevancy": sum(r["relevancy"] for r in results) / len(results),
                "precision": sum(r["precision"] for r in results) / len(results)
            }
            
            display_metrics(avg_metrics, "Средняя ")

else:
    st.info("Загрузите документ в меню слева")