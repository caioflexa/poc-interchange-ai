from sqlalchemy.orm import Session
from app.persistence.models import DocumentModel, InterchangeRuleModel
from typing import List, Optional


class DocumentRepository:
    # Repositório para operações de dados em documentos
    def __init__(self, db: Session):
        self.db = db

    def save(self, doc: DocumentModel):
        # Persiste um novo documento no banco
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def list_all(self) -> List[DocumentModel]:
        # Lista todos os documentos registrados
        return self.db.query(DocumentModel).all()

    def get_by_id(self, doc_id: str) -> Optional[DocumentModel]:
        # Busca um documento específico pelo ID
        return self.db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()


class RuleRepository:
    # Repositório para operações de dados em regras de intercâmbio
    def __init__(self, db: Session):
        self.db = db

    def save(self, rule: InterchangeRuleModel):
        # Persiste uma nova regra estruturada no banco
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def list_all(self, brand: Optional[str] = None) -> List[InterchangeRuleModel]:
        # Lista as regras, permitindo filtro opcional por bandeira
        query = self.db.query(InterchangeRuleModel)
        if brand:
            query = query.filter(InterchangeRuleModel.brand == brand)
        return query.all()
