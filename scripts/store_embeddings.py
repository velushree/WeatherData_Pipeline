import os
import logging
from typing import List
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

weather_data_dir = "/opt/airflow/data"
database_dir = "/opt/airflow/db/faiss_index"

def load_text_files(data_dir: str) -> List[Document]:
    docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    for filename in os.listdir(data_dir):
        if filename.lower().endswith(".txt"):
            file_path = os.path.join(data_dir, filename)
            logger.info(f"Loading: {file_path}")
            try:
                loader = TextLoader(file_path, encoding="utf-8")
                raw_docs = loader.load()
                split_docs = splitter.split_documents(raw_docs)

                for idx, doc in enumerate(split_docs):
                    doc.metadata["source_file"] = filename
                    doc.metadata["chunk_index"] = idx

                docs.extend(split_docs)
            except Exception as e:
                logger.warning(f"Failed to load {file_path}: {e}")
    return docs

def embed_and_store_documents(docs: List[Document], db_dir: str):
    if not docs:
        logger.warning("No documents to embed.")
        return

    logger.info(f"Using embedding model: BAAI/bge-base-en-v1.5")
    embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")

    logger.info(f"Embedding {len(docs)} chunks and storing in FAISS at: {db_dir}")
    vectorstore = FAISS.from_documents(docs, embedder)

    os.makedirs(db_dir, exist_ok=True)
    vectorstore.save_local(db_dir)
    logger.info("FAISS index saved successfully.")

def embed_pipeline():
    try:
        documents = load_text_files(weather_data_dir)
        embed_and_store_documents(documents, database_dir)
    except Exception as e:
        logger.error(f"Embedding pipeline failed: {e}")