from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Base, CorrelatedPair

def add_test_data():
    engine = create_engine('sqlite:///crypto_pairs.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    # Test verisi ekleme
    new_pair = CorrelatedPair(coin1='BTC', coin2='ETH')
    session.add(new_pair)
    session.commit()

    # Veriyi kontrol etme
    pairs = session.query(CorrelatedPair).all()
    for pair in pairs:
        print(f"Çift: {pair.coin1} - {pair.coin2}")

    session.close()
    print(f"Toplam {len(pairs)} çift bulundu.")

if __name__ == "__main__":
    add_test_data()