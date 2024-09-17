from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Base, CorrelatedPair

def add_coin_pairs(pairs):
    engine = create_engine('sqlite:///crypto_pairs.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    for pair in pairs:
        if isinstance(pair, tuple) and len(pair) == 2:
            coin1, coin2 = pair
        elif isinstance(pair, str):
            parts = pair.split('-')
            if len(parts) != 2:
                print(f"Geçersiz çift formatı: {pair}. Atlanıyor.")
                continue
            coin1, coin2 = parts
        else:
            print(f"Geçersiz çift formatı: {pair}. Atlanıyor.")
            continue
        
        new_pair = CorrelatedPair(coin1=coin1.strip().upper(), coin2=coin2.strip().upper())
        session.add(new_pair)
    
    session.commit()
    print(f"{len(pairs)} çift başarıyla eklendi.")

    all_pairs = session.query(CorrelatedPair).all()
    print("Mevcut tüm çiftler:")
    for pair in all_pairs:
        print(f"{pair.coin1} - {pair.coin2}")

    session.close()

if __name__ == "__main__":

    pairs_to_add = [
        ("FLOKI", "PEPE"),
        ("DOGE", "SHIB"),
        ("LOKA", "VOXEL"),
        ("BAR", "JUV"),
        ("ASR", "OG"),
        ("CITY", "PSG"),
        ("PORTO", "LAZIO"),
        ("AXS", "SLP"),
        ("NEO", "ONT"),
        ("KEY", "LINA"),
        ("WING", "BOND"),
        ("SFP", "C98"),  
        ("ONE", "CELR"),
        ("NEO", "EOS"),
        ("XRP", "XLM"),
        ("MANA", "SAND"),
        ("RARE", "SUPER"),
        ("PEPE", "FLOKI"),
        ("SHIB", "DOGE"),
        ("VOXEL", "LOKA"),
        ("JUV", "BAR"),
        ("OG", "ASR"),
        ("PSG", "CITY"),
        ("LAZIO", "PORTO"),
        ("SLP", "AXS"),
        ("ONT", "NEO"),
        ("LINA", "KEY"),
        ("BOND", "WING"),
        ("C98", "SFP"),
        ("CELR", "ONE"),
        ("EOS", "NEO"),
        ("XLM", "XRP"),
        ("SAND", "MANA"),
        ("SUPER", "RARE"),
    ]
    add_coin_pairs(pairs_to_add)
