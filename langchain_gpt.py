import argparse, os
import pandas as pd
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

parser = argparse.ArgumentParser(
                    prog='langchain_gpt',
                    description='Code generation for the Langchain framework',
                    epilog='Contact robertgshaw2@gmail.com for more help')

parser.add_argument('--document_path', type=str, default="./data/langchain_docs_modules.csv")
parser.add_argument('--persist_directory', type=str, default="./data/embeddings/chroma")
parser.add_argument('--do_embeddings', action='store_true')

def load_database(embedding_model, persist_directory):
    return Chroma(embedding_function=embedding_model, persist_directory=persist_directory)

def create_database(document_path, embedding_model, persist_directory):
    documents = []
    for _, row in pd.read_csv(document_path).iterrows():    
        documents.append(Document(page_content=row["text"],metadata={"source": row["source"]}))
        
    return Chroma.from_documents(documents=documents, embedding=embedding_model, persist_directory=persist_directory)

def setup_chain(db, model):
    retriever = db.as_retriever()
    retriever.search_kwargs['distance_metric'] = 'cos'
    retriever.search_kwargs['fetch_k'] = 25
    retriever.search_kwargs['maximal_marginal_relevance'] = True
    retriever.search_kwargs['k'] = 5
    retriever.search_kwargs['lambda_mult'] = 0.1

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

def main(document_path="./data/langchain_docs_modules.csv",
         persist_directory="./data/embeddings/chroma",
         do_embeddings=False,
         embedding_model_name="text-embedding-ada-002",
         chat_model_name="gpt-3.5-turbo"):
    
    embedding_model = OpenAIEmbeddings(model=embedding_model_name)
    chat_model = ChatOpenAI(model_name=chat_model_name, streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0)
    # chat_model = ChatOpenAI(model_name=chat_model_name)

    if do_embeddings:
        print("Generating database...")
        db = create_database(document_path, embedding_model=embedding_model, persist_directory=persist_directory)
    else:
        print("Loading database...")
        db = load_database(embedding_model=embedding_model, persist_directory=persist_directory)
    db.persist()

    print("Setting up chain...")
    qa_chain = setup_chain(db, model=chat_model)

    while True:
        query = input("Describe what you want to do in Langchain (type 'q' to quit): ")
        if query == 'q':
            break
        
        result = qa_chain(query)
        print("\n")

if __name__ == "__main__":
    args = parser.parse_args()
    main(
        document_path=args.document_path,
        persist_directory=args.persist_directory,
        do_embeddings=args.do_embeddings,
    )