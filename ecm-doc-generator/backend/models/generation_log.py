from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from . import Base

class GenerationLog(Base):
    __tablename__ = 'generation_logs'

    id = Column(Integer, primary_key=True)
    document_type = Column(String(50), nullable=False)
    quantity = Column(Integer, default=1)
    language = Column(String(10))
    template_style = Column(String(50))
    status = Column(String(20))  # success, failed
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    duration_seconds = Column(Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'document_type': self.document_type,
            'quantity': self.quantity,
            'language': self.language,
            'template_style': self.template_style,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'duration_seconds': self.duration_seconds
        }
