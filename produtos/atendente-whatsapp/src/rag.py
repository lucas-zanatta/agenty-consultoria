import logging
import sys
from io import BytesIO
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent))
import config
import db

log = logging.getLogger("agenty.rag")

_VOYAGE_URL = "https://api.voyageai.com/v1/embeddings"
_VOYAGE_MODEL = "voyage-2"
_CHUNK_SIZE = 500      # tokens aproximados por chunk
_CHUNK_OVERLAP = 50    # tokens de sobreposição entre chunks


def _split_text(text: str, chunk_size: int = _CHUNK_SIZE,
                overlap: int = _CHUNK_OVERLAP) -> list[str]:
    """Divide texto em chunks por palavras (aproximação de tokens)."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap
    return [c for c in chunks if c.strip()]


def embed_texts(texts: list[str], input_type: str = "document") -> list[list[float]]:
    """Gera embeddings via Voyage AI. input_type: 'document' ou 'query'."""
    headers = {
        "Authorization": f"Bearer {config.VOYAGE_API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":      _VOYAGE_MODEL,
        "input":      texts,
        "input_type": input_type,
    }
    with httpx.Client(timeout=60) as client:
        resp = client.post(_VOYAGE_URL, json=payload, headers=headers)
    resp.raise_for_status()
    return [item["embedding"] for item in resp.json()["data"]]


def embed_query(text: str) -> list[float]:
    return embed_texts([text], input_type="query")[0]


def process_pdf(client_id: str, filename: str,
                file_bytes: bytes, storage_path: str = "") -> int:
    """Extrai texto do PDF, chunka, embeda e salva no Supabase. Retorna nº de chunks."""
    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader

    reader = PdfReader(BytesIO(file_bytes))
    full_text = "\n".join(
        page.extract_text() or "" for page in reader.pages
    ).strip()

    if not full_text:
        log.warning(f"PDF '{filename}' não contém texto extraível")
        return 0

    chunks = _split_text(full_text)
    log.info(f"PDF '{filename}': {len(chunks)} chunks gerados")

    # Embed em lote (Voyage AI aceita até 128 textos por request)
    batch_size = 64
    all_embeddings: list[list[float]] = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        embeddings = embed_texts(batch, input_type="document")
        all_embeddings.extend(embeddings)

    chunk_records = [
        {"content": c, "embedding": e}
        for c, e in zip(chunks, all_embeddings)
    ]
    db.save_document_chunks(client_id, filename, storage_path, chunk_records)
    log.info(f"PDF '{filename}': {len(chunk_records)} chunks salvos no Supabase")
    return len(chunk_records)


def get_relevant_context(client_id: str, query: str, top_k: int = 3) -> str:
    """Busca trechos relevantes dos documentos do cliente para injetar no prompt."""
    if not config.VOYAGE_API_KEY:
        return ""
    try:
        embedding = embed_query(query)
        chunks = db.similarity_search(client_id, embedding, top_k=top_k)
        if not chunks:
            return ""
        return "\n\n".join(f"[Documento]\n{c}" for c in chunks)
    except Exception as e:
        log.error(f"Erro no RAG: {e}")
        return ""
