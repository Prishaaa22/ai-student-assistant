from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def load_documents():
    loader = TextLoader("college_info.txt", encoding="utf-8")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    print("Chunks created:", len(chunks))

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vector_db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory="college_db"
    )

    vector_db.persist()
    print("Data loaded successfully!")


if __name__ == "__main__":
    load_documents()
