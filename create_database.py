from sqlalchemy import create_engine
from app import Base, CorrelatedPair

def create_database():
    engine = create_engine('sqlite:///crypto_pairs.db')
    Base.metadata.create_all(engine)
    print("Veritabanı ve tablolar başarıyla oluşturuldu.")

if __name__ == "__main__":
    create_database()