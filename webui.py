##########################
# Chatbot User Interface #
##########################

# Python Standard Library Imports
import io  # Input/Output operations
import random  # Random number generation
import uuid  # Universally Unique Identifier generation
from pathlib import Path  # Handling file system paths
from typing import NamedTuple  # Type hinting for named tuples

# Third-Party Library Imports
import PyPDF2  # PDF manipulation library
import streamlit as st  # UI Framework for creating web applications
from streamlit_feedback import streamlit_feedback # Feedback widget for Streamlit

# Local Imports
from webui_config import UiConfig  # Configuration settings for the web UI
from llm_connector import llm_stream_result, LlmGenerationParameters, craft_prompt
from document_rag_processor import topk_documents, RagParameters


def feedback_callback(user_prompt, response):
    def inner(*args):

        feedback_info = args[0]
        feedback_type = feedback_info.get("type")
        feedback_score = feedback_info.get("score")
        feedback_text = feedback_info.get("text")

        if feedback_type == "thumbs":
            if feedback_score == "👍":
                feedback_score = 1
            elif feedback_score == "👎":
                feedback_score = 0
        else:
            raise NotImplementedError(f"Feedback type {feedback_type} is not supported.")
        print("feedback_callback", user_prompt, response, feedback_type, feedback_score, feedback_text)

    return inner

def main_ui_logic(config: UiConfig):

    st.title("LMPoC Chatbot Interface")

    ### Environment prepare.
    document_folder = Path(config.document_folder)
    # TODO: Logger: display warning.
    document_folder.mkdir(exist_ok=True)

    ### States
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "documents" not in st.session_state:
        st.session_state.documents = []

    if "session_id" not in st.session_state:
        # Generate user session identifier.
        st.session_state.session_id = uuid.uuid4().hex

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
        model_repetition_penalty = st.slider("Repetition Penalty", 0.0, 2.0, 1.10, key="model_repetition_penalty")

        # TODO: Refactor, extract document processing logic.
        st.markdown("### RAG Settings")
        rag_chunk_size = st.slider("Chunk Size", 0, 500, 100, key="rag_chunk_size")
        rag_chunk_overlap = st.slider("Chunk Overlap", 0, 100, 25, key="rag_chunk_overlap")
        rag_topk = st.slider("Top K", 0, 100, 3, key="rag_topk")


    # File upload interface
    with st.expander("文件上傳"):
        uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)

        if uploaded_files is not None:

            all_document_full_names = []
            for _file in uploaded_files:
                file_full_name = f"{st.session_state.session_id}-{_file.name}"  # Create file name.
                bytes_data = _file.getvalue() # Get raw data.
                doc_output = document_folder / file_full_name # Destination file.
                doc_output.write_bytes(bytes_data) # Write file to document folder.
                all_document_full_names.append(doc_output.absolute()) # Append current file to list.

            st.session_state.documents = all_document_full_names

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # HACK: This is a strange solution to handle StreamLit internal states.
    #      If we don't add the feedback widget here, it simply doesn't work (callback won't be fired).
    #      I haven't trace the internal source code yet, but we may figure out some better solutions.
    if len(st.session_state.messages) >= 1:
        streamlit_feedback(feedback_type="thumbs",
                                            on_submit=feedback_callback(st.session_state.messages[-2], st.session_state.messages[-1]),
                                            optional_text_label="[可選] 提供您的Feedback",
                                            key=f"feedback_{int(len(st.session_state.messages)) // 2}")

    # React to user input
    if user_input := st.chat_input("How can I help you today?"):

        # TODO: User model selection.
        llm_model_conf = config.llm_models[0]
        embedding_conf = config.embedding_model

        llm_param = LlmGenerationParameters.new_generation_parameter(
            top_k=model_topk,
            top_p=model_topp,
            temperature=model_temperature,
            repetition_penalty=model_repetition_penalty,
        )

        rag_param = RagParameters.new_rag_parameter(
            chunk_size=rag_chunk_size,
            chunk_overlap=rag_chunk_overlap,
            top_k=rag_topk,
        )

        # Display user message in chat message container
        st.chat_message("user").markdown(user_input)

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

        ## RAG     
        rag_docs = []
        if st.session_state["documents"]:   # Document list is not null, invoke RAG.
            topk_doc_score = topk_documents(user_input, embedding_conf, rag_param, st.session_state["documents"])
            rag_docs = [x for x, _ in topk_doc_score]
            rag_reference = ""
            for d, score in topk_doc_score:
                rag_reference += "```\n"
                rag_reference += d.page_content
                rag_reference += "\n"
                rag_reference += "```\n"
            with st.expander("參考文件 Referenced Document"):
                st.markdown(rag_reference)

        # Prompt crafting.
        prompt = craft_prompt(user_input, rag_docs)

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
        st.rerun()


if __name__ == "__main__":

    st.set_page_config(page_title="LMPoC Chat Interface")

    # Load config.
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = UiConfig.load_config_from_file(f)
    
    main_ui_logic(config=config)