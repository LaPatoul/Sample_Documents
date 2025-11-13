from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from datetime import datetime
from . import Base

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    document_type = Column(String(50), nullable=False)  # invoice, purchase_order, receipt
    document_number = Column(String(100), nullable=False, unique=True)
    template_style = Column(String(50))  # modern, classic, minimal
    language = Column(String(10))  # fr, de
    company_id = Column(Integer, ForeignKey('companies.id'))
    customer_name = Column(String(200))
    total_amount = Column(Float)
    currency = Column(String(10), default='EUR')
    file_path = Column(Text)
    file_format = Column(String(10))  # pdf, html
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(Text)  # Additional metadata as JSON string

    def to_dict(self):
        return {
            'id': self.id,
            'document_type': self.document_type,
            'document_number': self.document_number,
            'template_style': self.template_style,
            'language': self.language,
            'company_id': self.company_id,
            'customer_name': self.customer_name,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'file_path': self.file_path,
            'file_format': self.file_format,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
