"""
Gerenciador de banco de dados NoSQL usando TinyDB.
Armazena extrações, páginas e metadados.
"""

from datetime import datetime
from typing import Optional

from tinydb import TinyDB, Query

from src.config import DB_PATH


class DatabaseManager:
    """Gerencia todas as operações do banco de dados local."""

    def __init__(self, db_path: str = DB_PATH):
        self.db = TinyDB(db_path, indent=4, ensure_ascii=False)
        self.extractions = self.db.table("extractions")
        self.pages = self.db.table("pages")

    # ─── Extrações ─────────────────────────────────────────────────────────

    def create_extraction(self, name: str, version: str, doc_type: str) -> int:
        """
        Cria uma nova extração. A combinação (name + version + type) deve ser única.
        Retorna o doc_id da extração criada.
        """
        Extraction = Query()
        existing = self.extractions.search(
            (Extraction.name == name)
            & (Extraction.version == version)
            & (Extraction.doc_type == doc_type)
        )
        if existing:
            raise ValueError(
                f"Já existe uma extração com nome '{name}', "
                f"versão '{version}' e tipo '{doc_type}'."
            )

        doc_id = self.extractions.insert(
            {
                "name": name,
                "version": version,
                "doc_type": doc_type,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "page_count": 0,
            }
        )
        return doc_id

    def get_all_extractions(self) -> list[dict]:
        """Retorna todas as extrações ordenadas por data de criação."""
        items = self.extractions.all()
        for item in items:
            item["id"] = item.doc_id
        return sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)

    def get_extraction(self, doc_id: int) -> Optional[dict]:
        """Retorna uma extração pelo ID."""
        doc = self.extractions.get(doc_id=doc_id)
        if doc:
            doc["id"] = doc.doc_id
        return doc

    def update_extraction(self, doc_id: int, **kwargs) -> None:
        """Atualiza campos de uma extração."""
        kwargs["updated_at"] = datetime.now().isoformat()
        self.extractions.update(kwargs, doc_ids=[doc_id])

    def delete_extraction(self, doc_id: int) -> None:
        """Remove uma extração e todas as suas páginas."""
        # Remove páginas associadas
        Page = Query()
        self.pages.remove(Page.extraction_id == doc_id)
        # Remove a extração
        self.extractions.remove(doc_ids=[doc_id])

    def extraction_exists(self, name: str, version: str, doc_type: str) -> bool:
        """Verifica se uma extração com a combinação já existe."""
        Extraction = Query()
        result = self.extractions.search(
            (Extraction.name == name)
            & (Extraction.version == version)
            & (Extraction.doc_type == doc_type)
        )
        return len(result) > 0

    # ─── Páginas ───────────────────────────────────────────────────────────

    def add_page(
        self,
        extraction_id: int,
        page_number: int,
        original_text: str,
        translated_text: str = "",
    ) -> int:
        """Adiciona uma nova página a uma extração."""
        doc_id = self.pages.insert(
            {
                "extraction_id": extraction_id,
                "page_number": page_number,
                "original_text": original_text,
                "translated_text": translated_text,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        )
        # Atualiza contagem de páginas na extração
        extraction = self.get_extraction(extraction_id)
        if extraction:
            self.update_extraction(
                extraction_id, page_count=extraction.get("page_count", 0) + 1
            )
        return doc_id

    def get_pages(self, extraction_id: int) -> list[dict]:
        """Retorna todas as páginas de uma extração ordenadas por número."""
        Page = Query()
        pages = self.pages.search(Page.extraction_id == extraction_id)
        for page in pages:
            page["id"] = page.doc_id
        return sorted(pages, key=lambda x: x.get("page_number", 0))

    def get_page(self, page_doc_id: int) -> Optional[dict]:
        """Retorna uma página pelo ID do documento."""
        doc = self.pages.get(doc_id=page_doc_id)
        if doc:
            doc["id"] = doc.doc_id
        return doc

    def update_page(self, page_doc_id: int, **kwargs) -> None:
        """Atualiza campos de uma página."""
        kwargs["updated_at"] = datetime.now().isoformat()
        self.pages.update(kwargs, doc_ids=[page_doc_id])

    def delete_page(self, page_doc_id: int) -> None:
        """Remove uma página."""
        page = self.get_page(page_doc_id)
        if page:
            extraction_id = page["extraction_id"]
            self.pages.remove(doc_ids=[page_doc_id])
            # Atualiza contagem
            extraction = self.get_extraction(extraction_id)
            if extraction:
                count = max(0, extraction.get("page_count", 1) - 1)
                self.update_extraction(extraction_id, page_count=count)

    def reorder_pages(self, extraction_id: int, page_order: list[int]) -> None:
        """
        Reordena as páginas de uma extração.
        page_order: lista de doc_ids na nova ordem.
        """
        for new_number, page_doc_id in enumerate(page_order, start=1):
            self.pages.update(
                {"page_number": new_number, "updated_at": datetime.now().isoformat()},
                doc_ids=[page_doc_id],
            )

    def get_next_page_number(self, extraction_id: int) -> int:
        """Retorna o próximo número de página disponível."""
        pages = self.get_pages(extraction_id)
        if not pages:
            return 1
        return max(p.get("page_number", 0) for p in pages) + 1

    def close(self) -> None:
        """Fecha a conexão com o banco."""
        self.db.close()
