from langchain_community.vectorstores import Chroma


def get_vector_store(embeddings):

    vector_db = Chroma(
        persist_directory="vector_db",
        embedding_function=embeddings
    )

    return vector_db