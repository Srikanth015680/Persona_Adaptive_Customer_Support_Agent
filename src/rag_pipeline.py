import logging
from pathlib import Path
from typing import List, Dict, Any

import chromadb

from . import config
from .document_loader import load_documents, chunk_documents, Chunk
from .offline_embedder import OfflineEmbedder
from . import llm_providers

logger = logging.getLogger(__name__)

OFFLINE_EMBEDDER_PATH = config.CHROMA_DIR / "offline_embedder.pkl"


class RAGPipeline:
    def __init__(self, persist_dir: Path = None):
        self.persist_dir = Path(persist_dir or config.CHROMA_DIR)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.chroma_client = chromadb.PersistentClient(
            path=str(self.persist_dir)
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        self.offline_embedder = None

        if OFFLINE_EMBEDDER_PATH.exists():
            try:
                self.offline_embedder = OfflineEmbedder.load(
                    OFFLINE_EMBEDDER_PATH
                )
            except Exception:
                self.offline_embedder = None

    def _embed(self, text: str) -> List[float]:
        vector = llm_providers.embed(text)

        if vector is not None:
            return vector

        if self.offline_embedder is None:
            raise RuntimeError(
                "No embedding model available. Run ingest.py first."
            )

        return self.offline_embedder.transform(text)

    def ingest(
        self,
        data_dir: Path = None,
        rebuild: bool = True,
    ) -> int:

        docs = load_documents(data_dir)

        if not docs:
            raise RuntimeError(
                f"No documents found in {data_dir or config.DATA_DIR}"
            )

        chunks: List[Chunk] = chunk_documents(docs)

        logger.info(
            "Loaded %d documents -> %d chunks",
            len(docs),
            len(chunks),
        )

        if rebuild:
            try:
                self.chroma_client.delete_collection(
                    config.COLLECTION_NAME
                )
            except Exception:
                pass

            self.collection = (
                self.chroma_client.get_or_create_collection(
                    name=config.COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"},
                )
            )

        self.offline_embedder = OfflineEmbedder()
        self.offline_embedder.fit([c.text for c in chunks])
        self.offline_embedder.save(OFFLINE_EMBEDDER_PATH)

        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for chunk in chunks:
            ids.append(
                f"{chunk.source}::chunk_{chunk.chunk_index}"
            )

            embeddings.append(
                self._embed(chunk.text)
            )

            metadatas.append(
                {
                    "source": chunk.source,
                    "chunk_index": chunk.chunk_index,
                    "section": chunk.section,
                }
            )

            documents.append(chunk.text)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )

        return len(chunks)

    def retrieve(
        self,
        query: str,
        top_k: int = None,
    ) -> List[Dict[str, Any]]:

        top_k = top_k or config.TOP_K

        if self.collection.count() == 0:
            return []

        query_vector = self._embed(query)

        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
        )

        retrieved = []

        if results and results.get("documents"):
            docs0 = results["documents"][0]
            metas0 = results["metadatas"][0]

            dists0 = (
                results["distances"][0]
                if results.get("distances")
                else [None] * len(docs0)
            )

            for text, meta, dist in zip(
                docs0,
                metas0,
                dists0,
            ):
                score = (
                    1.0 - dist
                    if dist is not None
                    else None
                )

                retrieved.append(
                    {
                        "text": text,
                        "source": meta.get("source"),
                        "section": meta.get(
                            "section",
                            "General",
                        ),
                        "chunk_index": meta.get(
                            "chunk_index"
                        ),
                        "score": (
                            round(float(score), 4)
                            if score is not None
                            else None
                        ),
                    }
                )

        return retrieved

    def is_ready(self) -> bool:
        try:
            return self.collection.count() > 0
        except Exception:
            return False