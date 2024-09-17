import discord
from discord.ext import commands, tasks
import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import matplotlib.pyplot as plt
import io
import logging
from datetime import datetime

# Logging konfigürasyonu
logging.basicConfig(filename='bot.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

# Bot configuration
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

# Database setup
Base = declarative_base()
engine = create_engine('sqlite:///crypto_pairs.db')
Session = sessionmaker(bind=engine)

class CorrelatedPair(Base):
    __tablename__ = 'correlated_pairs'
    id = Column(Integer, primary_key=True)
    coin1 = Column(String, nullable=False)
    coin2 = Column(String, nullable=False)

Base.metadata.create_all(engine)

bot = commands.Bot(command_prefix='!', intents=intents)

# Asenkron olarak fiyat değişimi almak
async def get_price_change(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=60) as response:  # Zaman aşımı ayarı
                data = await response.json()
                price_change_percentage_1h = data['market_data']['price_change_percentage_1h_in_currency']['usd']
                return price_change_percentage_1h
    except Exception as e:
        logging.error(f"Error getting price change for {coin_id}: {e}")
        return 0

# Asenkron olarak grafik verilerini almak
async def get_chart_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=60) as response:  # Zaman aşımı ayarı
                data = await response.json()
                prices = data['prices']
                dates = [datetime.fromtimestamp(price[0]/1000) for price in prices]
                values = [price[1] for price in prices]
                return dates, values
    except Exception as e:
        logging.error(f"Error getting chart data for {coin_id}: {e}")
        return [], []

# Asenkron olarak grafik görselini oluşturmak
async def get_chart_image(coin_id):
    dates, values = await get_chart_data(coin_id)
    
    if not dates or not values:
        return None
    
    plt.figure(figsize=(10, 5))
    plt.plot(dates, values)
    plt.title(f"{coin_id.upper()} Son 24 Saat")
    plt.xlabel("Tarih")
    plt.ylabel("Fiyat (USD)")
    plt.xticks(rotation=45)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    return buf

@tasks.loop(minutes=3)
async def check_prices():
    session = Session()
    pairs = session.query(CorrelatedPair).all()
    
    for pair in pairs:
        try:
            change1 = await get_price_change(pair.coin1.lower())
            if abs(change1) >= 0.25:
                change2 = await get_price_change(pair.coin2.lower())
                
                chart1 = await get_chart_image(pair.coin1.lower())
                chart2 = await get_chart_image(pair.coin2.lower())
                
                channel = bot.get_channel(CHANNEL_ID)
                files = []
                if chart1:
                    files.append(discord.File(chart1, filename=f"{pair.coin1}_chart.png"))
                if chart2:
                    files.append(discord.File(chart2, filename=f"{pair.coin2}_chart.png"))
                
                await channel.send(
                    f"{pair.coin1} {change1:.2f}% değişti. Korele coin: {pair.coin2} ({change2:.2f}% değişim)",
                    files=files
                )
                logging.info(f"Bildirim gönderildi: {pair.coin1} - {pair.coin2}")
        except Exception as e:
            logging.error(f"Hata: {pair.coin1}-{pair.coin2} çifti kontrol edilirken: {e}")
    
    session.close()

@bot.event
async def on_ready():
    logging.info(f'{bot.user} olarak giriş yapıldı!')
    check_prices.start()

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def list_pairs(ctx):
    session = Session()
    pairs = session.query(CorrelatedPair).all()
    if pairs:
        pair_list = "\n".join([f"{pair.coin1} - {pair.coin2}" for pair in pairs])
        await ctx.send(f"Korele coin çiftleri:\n{pair_list}")
    else:
        await ctx.send("Henüz eklenmiş bir coin çifti bulunmuyor.")
    session.close()

if __name__ == '__main__':
    try:
        bot.run(TOKEN)
    except Exception as e:
        logging.critical(f"Bot başlatılamadı: {e}")
