from fastapi import FastAPI
import argparse, os
import pandas as pd
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

PERSIST_DIRECTORY_NAME = "./data/embeddings/chroma"
CHAT_MODEL_NAME = "gpt-3.5-turbo"
EMBEDDING_MODEL_NAME = "text-embedding-ada-002"

# setup models
chat_model = ChatOpenAI(model_name=CHAT_MODEL_NAME)
embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)

# setup database
db = Chroma(embedding_function=embedding_model, persist_directory=PERSIST_DIRECTORY_NAME)

# setup chain
def setup_chain(db, model):
    retriever = db.as_retriever()
    retriever.search_kwargs = {
        'distance_metric': 'cos',
        'fetch_k': 25,
        'maximal_marginal_relevance': True,
        'k': 5,
        'lambda_mult': 0.1
    }

    prompt_template = """Use the following examples from the LangChain documentation to write code based on the request below. If you don't know the answer, just say that you don't know, don't try to make up an answer.

    {context}

    Request: {question}
    Respond with just Python code:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    chain_type_kwargs = {"prompt": PROMPT}

    return RetrievalQA.from_chain_type(
        llm=model, 
        chain_type="stuff", 
        retriever=retriever,
        chain_type_kwargs=chain_type_kwargs, 
        return_source_documents=True)

qa_chain = setup_chain(db, model=chat_model)

# setup server
app = FastAPI()

@app.get("/predict")
async def predict(query: str):
    result = qa_chain(query)
    print(result["result"])
    return {"result": result["result"]}