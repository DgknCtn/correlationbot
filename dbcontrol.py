from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Base, CorrelatedPair

def check_database_connection():
    try:
        engine = create_engine('sqlite:///crypto_pairs.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        
        # Basit bir sorgu deneyin
        pairs = session.query(CorrelatedPair).all()
        print(f"Veritabanı bağlantısı başarılı. {len(pairs)} çift bulundu.")
        
        session.close()
        return True
    except Exception as e:
        print(f"Veritabanı bağlantısı başarısız: {e}")
        return False

if __name__ == "__main__":
    check_database_connection()