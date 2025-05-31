import streamlit as st
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from dotenv import load_dotenv
import os
import datetime
import csv
import uuid

if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]  # short random ID
user_id = st.session_state.user_id


# Load environment variables
load_dotenv()
os.environ['HF_TOKEN'] = os.getenv("HF_TOKEN")

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Streamlit UI
st.title("Conversational RAG With Chat History")

# Input the Groq API Key
api_key = st.text_input("Enter your Groq API key:", type="password")

# Check if Groq API key is provided
if api_key:
    llm = ChatGroq(groq_api_key=api_key, model_name="Gemma2-9b-It")

    # Chat interface
    session_id = st.text_input("Session ID", value="default_session")

    # Statefully manage chat history
    if 'store' not in st.session_state:
        st.session_state.store = {}

    # Load and split documents from the "docs" directory
    def load_and_split_documents():
        docs = []
        for file in os.listdir("docs"):
            if file.endswith(".txt"):
                loader = TextLoader(os.path.join("docs", file))
                docs.extend(loader.load())

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)
        return splits

    splits = load_and_split_documents()
    vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
    retriever = vectorstore.as_retriever()

    # Prompt templates
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise.\n\n{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # Chat history management
    def get_session_history(session: str) -> ChatMessageHistory:
        if session not in st.session_state.store:
            st.session_state.store[session] = ChatMessageHistory()
        return st.session_state.store[session]

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

    def log_interaction_to_csv(user_id, session_id, user_input, answer, chat_history):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        os.makedirs("logs", exist_ok=True)
        log_file_path = os.path.join("logs", f"{session_id}_chat_log.csv")

        history_text = ""
        for msg in chat_history.messages:
            role = "User" if msg.type == "human" else "Bot"
            history_text += f"{role}: {msg.content} | "

        with open(log_file_path, mode="a", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["Timestamp", "User ID", "Session ID", "User Input", "Answer", "History"])
            writer.writerow([timestamp, user_id, session_id, user_input, answer, history_text.strip()])

    # Input from user
    user_input = st.text_input("Your question:")

    if user_input and session_id:
        session_history = get_session_history(session_id)

        response = conversational_rag_chain.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}},
        )

        # Log interaction to CSV
        log_interaction_to_csv(user_id, session_id, user_input, response["answer"], session_history)


        # Display chat history
        st.subheader("Chat History:")
        for msg in session_history.messages:
            if msg.type == "human":
                st.markdown(f"**You:** {msg.content}")
            else:
                st.markdown(f"**Bot:** {msg.content}")

else:
    st.warning("Please enter the Groq API Key")
