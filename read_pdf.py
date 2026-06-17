import os
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer


def extract_pdf_text(pdf_path):
    """
    Reads pdf file and extracts text from each page.
    Input:
    pdf_path: path to pdf input.

    Output:
    pages_text: a list of dict, holding textual content of each page of pdf.
    
    """

    pdfReader = PdfReader(pdf_path)
    pages_text = []

    for page_num, page in enumerate(pdfReader.pages):
        text = page.extract_text()

        if text:
            pages_text.append({"page": page_num +1, "text": text})

    return pages_text



def text_to_chunk(text, chunk_size=800, overlap = 100):


    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks




if __name__ == "__main__":

    documents = []
    ids = []
    metadata = []
    
    docs = "docs"

    CHROMA_FOLDER = "chroma_db"

    COLLECTION_NAME = "pdf_documents"
    
    client = chromadb.PersistentClient(path=CHROMA_FOLDER)

    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    for file in os.listdir(docs):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(docs, file)

            print(f"Reading PDF: {file}")

            pages = extract_pdf_text(pdf_path)

            for page_data in pages:
                page_num = page_data["page"]
                page_text = page_data["text"]

                chunks = text_to_chunk(page_text)

                for chunk_index, chunk in enumerate(chunks):
                    documents.append(chunk)

                    ids.append(f"{file}_page_{page_num}_chunk_{chunk_index}")

                    metadata.append({"source": file, "page": page_num, "chunk": chunk_index})

    embeddings = embedding_model.encode(documents).tolist()
    collection.add(documents=documents,
                   embeddings=embeddings,
                   ids=ids,
                   metadatas=metadata
                   )
    print(f"Stored {len(documents)} chunks in ChromaDB.")
    # text = extract_pdf_text("docs/begonia.pdf")


    # print(text_to_chunk(text[0].get('text')))
