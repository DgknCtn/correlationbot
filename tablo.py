from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

# Veritabanı bağlantısını oluşturun
engine = create_engine('sqlite:///crypto_pairs.db')
Base = declarative_base()

# Modelinizi tanımlayın (önceden tanımladığınız CorrelatedPair modeli)
class CorrelatedPair(Base):
    __tablename__ = 'correlated_pairs'
    id = Column(Integer, primary_key=True)
    coin1 = Column(String, nullable=False)
    coin2 = Column(String, nullable=False)
    last_price1 = Column(Float, default=0)
    last_price2 = Column(Float, default=0)

# Mevcut tabloları silin ve yeniden oluşturun
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

print("Tablo başarıyla oluşturuldu!")
