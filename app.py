from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CorrelatedPair(Base):
    __tablename__ = 'correlated_pairs'
    
    id = Column(Integer, primary_key=True)
    coin1 = Column(String, nullable=False)
    coin2 = Column(String, nullable=False)

    def __repr__(self):
        return f"<CorrelatedPair(coin1='{self.coin1}', coin2='{self.coin2}')>"
    