# MultiTurn ChatBot with Conversational History
## Introduction

The Conversational RAG (Retrieval-Augmented Generation) Bot is designed to facilitate interactive question-and-answer sessions while maintaining chat history. 

## Data Flow Steps

The data flow within the bot can be outlined in the following steps:

### 1. User Identification

- **User Session Management**: Upon initiating the session, a unique `user_id` is generated and stored in the session state if it doesn't already exist. This ID helps in tracking user interactions.

### 2. Document Loading and Processing

- **Loading Documents**: The bot loads text documents from a specified directory (`docs`). Each document is split into chunks using `RecursiveCharacterTextSplitter`, which aids in efficient retrieval.

### 3. Vector Storage

- **Vector Store Creation**: Using the embeddings generated earlier usinh `HUGGING_FACE_EMBEDDING_MODEL`, a `FAISS` vector store is created from the processed documents. This store allows for quick retrieval of relevant information based on user queries.

### 4. Prompt Templates

- **Contextualization and QA Prompts**: Two main prompt templates are defined:
  - **Contextualization Prompt**: Reformulates questions based on chat history.
  - **QA Prompt**: Guides the model in generating concise answers using retrieved context.

### 5. History-Aware Retrieval

- **Retriever Creation**: A history-aware retriever is created to ensure that responses are contextually relevant, considering previous interactions.

### 6. Chat History Management

- **Session History Handling**: The bot maintains a history of the chat for each user session, ensuring that interactions are preserved and accessible.

### 7. Interaction Logging

- **Logging Interactions**: Each interaction is logged in a CSV file, capturing details like timestamp, user input, responses, and the full chat history for future reference.

### 8. User Interaction

- **Question Input**: Users input their questions through the interface. When a question is submitted, the bot processes it, retrieves relevant information, and generates a response.

### 9. Response Display

- **Chat History Display**: After processing the user's question, the bot displays the entire chat history, showcasing both user inputs and bot responses in a clear format.

## Conclusion

The Conversational RAG Bot represents a robust solution for interactive question-answering tasks, effectively combining document retrieval with conversational AI. Through its structured data flow, it ensures that user interactions are logged, context is preserved, and responses are tailored to the user's needs.
