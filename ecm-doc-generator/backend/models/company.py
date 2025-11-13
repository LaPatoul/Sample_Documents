from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from . import Base

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    address = Column(Text)
    city = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    phone = Column(String(50))
    email = Column(String(100))
    tax_id = Column(String(50))
    website = Column(String(200))
    is_preset = Column(Integer, default=0)  # 1 for Peters Engineering, 0 for generated
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'country': self.country,
            'phone': self.phone,
            'email': self.email,
            'tax_id': self.tax_id,
            'website': self.website,
            'is_preset': self.is_preset
        }
