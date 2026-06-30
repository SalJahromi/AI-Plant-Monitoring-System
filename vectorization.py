import chromadb


def connect_chromaDB(chroma_folder, collection_name):

    #connecting to chroma
    client = chromadb.PersistentClient(path=chroma_folder)
    collection = client.get_collection(name=collection_name)
    
    return collection



def pdf_context_retrieval(question, embeddingModel, collection, n_results=3):
    """
    
    """

    # question to vector conversion

    question_embedding = embeddingModel.encode([question]).tolist()[0]

    # find similar chunks in chroma
    results = collection.query(query_embeddings=[question_embedding], n_results=n_results)

    chunks = results["documents"][0]
    # metadatas = results["metadatas"][0]

    context_blocks = []


    for chunk in chunks:
        context_blocks.append(chunk)

    return "\n\n--\n\n".join(context_blocks)

