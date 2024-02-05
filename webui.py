##########################
# Chatbot User Interface #
##########################

import io
import random

import streamlit as st  # UI Framework

from langchain.text_splitter import RecursiveCharacterTextSplitter

from typing import NamedTuple

import PyPDF2


from typing import NamedTuple

from llm_connector import llm_stream_result, LlmGenerationParameters, LlmModelConfig, craft_prompt

class RagParameters(NamedTuple):
    chunk_size: int
    chunk_overlap: int
    top_k: int

def load_pdf_to_text(file_like) -> str:
    pdf_reader = PyPDF2.PdfFileReader(file_like)
    full_text = ""
    # Get the total number of pages in the PDF
    num_pages = pdf_reader.numPages
    for i in range(num_pages):
        page = pdf_reader.getPage(i)
        text = page.extractText()
        full_text += text
    return full_text

def text_splitter(text: str, chunk_size=100, chunk_overlap=5):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    all_splits = text_splitter.create_documents([text])
    return all_splits

def main_ui_logic():

    st.title("Chatbot Interface")

    ### States
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "documents" not in st.session_state:
        st.session_state.documents = []

    ### Components


    with st.sidebar:
        st.markdown("# General Settings")
        with st.expander("參數說明"):
            st.markdown("### LLM Generation Parameter")
            st.markdown("Top K: 保留機率最高的前 K 個字")
            st.markdown("Top P: 從機率總和為 P 的字中選擇")
            st.markdown("Temperature: 生成時的亂度")
            st.markdown("Repetition Penalty: 重複字的懲罰")
            st.markdown("### RAG Settings")
            st.markdown("Chunk Size: 文章分割的大小")
            st.markdown("Chunk Overlap: 文章分割的重疊大小")
            st.markdown("Top K: 保留機率最高的前 K 個文章")

        st.markdown("### LLM Generation Parameter")
        model_topk = st.slider("Top K", 0, 200, 10, key="model_topk")
        model_topp = st.slider("Top P", 0.0, 1.0, 0.9, key="model_topp")
        model_temperature = st.slider("Temperature", 0.0, 1.0, 0.01, key="model_temperature")
        model_repetition_penalty = st.slider("Repetition Penalty", 0.0, 2.0, 1.03, key="model_repetition_penalty")

        st.markdown("### RAG Settings")
        rag_chunk_size = st.slider("Chunk Size", 0, 500, 100, key="rag_chunk_size")
        rag_chunk_overlap = st.slider("Chunk Overlap", 0, 100, 5, key="rag_chunk_overlap")
        rag_topk = st.slider("Top K", 0, 100, 5, key="rag_topk")


    # File upload interface
    with st.expander("文件上傳"):
        uploaded_file = st.file_uploader("Choose a file")

        if uploaded_file is not None:
            print(uploaded_file)
            bytes_data = uploaded_file.getvalue()
            reader = io.BytesIO(bytes_data)
            full_text = load_pdf_to_text(reader)
            split_text = text_splitter(full_text)
            print(split_text)
            st.session_state.documents += split_text

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if user_input := st.chat_input("How can I help you today?"):

        # TODO: Load config from file.
        llm_model_conf = LlmModelConfig.new_llm_config(
            "huggingface",
            "http://localhost:15810"
        )

        # TODO: Fetch parameters.
        llm_param = LlmGenerationParameters.new_generation_parameter(
            top_k=model_topk,
            top_p=model_topp,
            temperature=model_temperature,
            repetition_penalty=model_repetition_penalty,
        )

        # Display user message in chat message container
        st.chat_message("user").markdown(user_input)

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

        # Prompt crafting.
        prompt = craft_prompt(user_input)

        # Simulating bot typing.
        for response in llm_stream_result(prompt, llm_model_conf, llm_param):
            if "undertale" in prompt.lower():
                cursor = "❤️"
            else:
                cursor = "❖"
            full_response += (response or "")
            message_placeholder.markdown(full_response + cursor)

        # While complete, display full bot response.
        message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    main_ui_logic()