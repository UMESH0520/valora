from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    brand = Column(String(100), nullable=False)
    model = Column(String(100))
    category = Column(String(100))
    last_known_price = Column(Integer)  # in paise
    urls = Column(JSON, default=dict)  # {platform: url}
    extra_data = Column(JSON, default=dict)  # additional product info (renamed from 'metadata' to avoid SQLAlchemy reserved name)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'name': self.name,
            'brand': self.brand,
            'model': self.model,
            'category': self.category,
            'last_known_price': self.last_known_price,
            'urls': self.urls,
            'extra_data': self.extra_data,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
