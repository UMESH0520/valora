from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Price(Base):
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(String(50), ForeignKey('products.product_id'), nullable=False)
    lowest_paise = Column(Integer, nullable=False)
    display_paise = Column(Integer, nullable=False)
    margin_percent = Column(Float, default=3.0)
    supporting_adapters = Column(JSON, default=list)
    all_sources = Column(JSON, default=list)
    blockchain_tx_id = Column(String(255))  # Algorand transaction ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_product_created', 'product_id', 'created_at'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'lowest_paise': self.lowest_paise,
            'display_paise': self.display_paise,
            'display_price_readable': f'₹{self.display_paise/100:.2f}',
            'margin_percent': self.margin_percent,
            'supporting_adapters': self.supporting_adapters,
            'all_sources': self.all_sources,
            'blockchain_tx_id': self.blockchain_tx_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class PriceHistory(Base):
    __tablename__ = 'price_history'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(String(50), ForeignKey('products.product_id'), nullable=False)
    adapter_name = Column(String(50), nullable=False)
    price_paise = Column(Integer, nullable=False)
    confidence = Column(Float, default=0.8)
    raw_data = Column(JSON, default=dict)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_history_product_adapter', 'product_id', 'adapter_name', 'scraped_at'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'adapter_name': self.adapter_name,
            'price_paise': self.price_paise,
            'price_readable': f'₹{self.price_paise/100:.2f}',
            'confidence': self.confidence,
            'raw_data': self.raw_data,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
        }
