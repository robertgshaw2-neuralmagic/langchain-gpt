import pandas as pd
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

DOCUMENT_PATH = "./data/langchain_docs_modules.csv"
EMBEDDING_MODEL_NAME = "text-embedding-ada-002"
PERSIST_DIRECTORY_NAME = "./data/embeddings/chroma"

def create_database(document_path, embedding_model, persist_directory):
    documents = []
    for _, row in pd.read_csv(document_path).iterrows():
        documents.append(Document(page_content=row["text"], metadata={"source": row["source"]}))
        
    return Chroma.from_documents(documents=documents, embedding=embedding_model, persist_directory=persist_directory)

if __name__ == "__main__":

    db = create_database(
        document_path=DOCUMENT_PATH,
        embedding_model=OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME), 
        persist_directory=PERSIST_DIRECTORY_NAME)
    
    db.persist()