# FINETUNE GPT ON LEGAL DATA SET

### Overview
The project aims to develop a legal question-answering system using a fine-tuned GPT-2 model. The system is designed to assist users by providing accurate answers to legal questions based on a dataset derived from the Open Australian Legal QA dataset. 

### Components
1. **Dataset**: The primary source of information for the model, containing questions and answers related to legal cases.
2. **Data Cleaning**: A preprocessing step to ensure the data is in a suitable format for training the model.
3. **Model Training**: Fine-tuning the GPT-2 model on the cleaned dataset to improve its ability to generate relevant answers.
4. **Inference**: Using the trained model to generate answers to user queries.

## Data Flow within the Application

### 1. Data Loading
- The application starts by loading the legal QA dataset, typically in JSON format.
- The dataset contains columns for questions and answers, alongside other metadata.

### 2. Data Cleaning
- **Text Processing**: Unwanted elements (URLs, numbers, punctuation) are removed to standardize the text.
- **Lowercasing**: All text is converted to lowercase to maintain consistency.
- **Whitespace Handling**: Extra spaces are trimmed, ensuring clean input for the model.

### 3. Data Formatting
- The cleaned questions and answers are formatted into a specific prompt template:
  ```
  You are a legal assistant. Read the question and provide a clear and accurate answer.
  
  Question: {question}
  Answer: {answer}
  ```
- This structured format helps the model understand the context and expected output during training and inference.

### 4. Dataset Conversion
- The cleaned and formatted data is converted into a Hugging Face Dataset, which facilitates easy manipulation for model training and evaluation.

### 5. Model Tokenization
- The text data is tokenized using the GPT-2 tokenizer. This process converts the text into input IDs that the model can process.
- Padding and truncation ensure that all input sequences are of uniform length.

### 6. Model Training
- The tokenized dataset is split into training and testing sets.
- The GPT-2 model is trained using the training dataset, adjusting weights based on the input-output pairs.
- Training parameters (batch size, epochs, etc.) can be configured to optimize performance.

### 7. Evaluation
- After training, the model is evaluated using metrics like BLEU score and perplexity to assess its performance.
- Sample outputs are generated and compared against the expected answers to gauge accuracy.

### 8. Inference
- For user queries, the application generates answers using the trained model:
  - The user question is formatted into the prompt template.
  - The prompt is tokenized and passed to the model.
  - The model generates a response, which is then decoded back into human-readable text.

### 9. Output
- The final output is presented to the user, providing a clear and concise answer to their legal question.

## Conclusion
The application efficiently transforms raw legal data into a useful tool for answering legal inquiries. By utilizing advanced NLP techniques and a structured data flow, it aims to provide accurate and contextually relevant answers to users.
