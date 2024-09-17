import discord
from discord.ext import commands, tasks
import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import mplfinance as mpf
import matplotlib.pyplot as plt
import io
import logging
from datetime import datetime, timedelta
from pycoingecko import CoinGeckoAPI
import pandas as pd

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
    last_price1 = Column(Float, default=0)
    last_price2 = Column(Float, default=0)

Base.metadata.create_all(engine)

bot = commands.Bot(command_prefix='!', intents=intents)
cg = CoinGeckoAPI()

async def get_price_change(coin_id):
    try:
        data = cg.get_coin_by_id(coin_id, localization=False, tickers=False, market_data=True, community_data=False, developer_data=False, sparkline=False)
        price_change_percentage_1h = data['market_data']['price_change_percentage_1h_in_currency']['usd']
        return price_change_percentage_1h
    except Exception as e:
        logging.error(f"Error getting price change for {coin_id}: {e}")
        return 0

async def get_current_price(coin_id):
    try:
        data = cg.get_price(ids=coin_id, vs_currencies='usd')
        return data[coin_id]['usd']
    except Exception as e:
        logging.error(f"Error getting current price for {coin_id}: {e}")
        return 0

async def get_chart_data(coin_id):
    try:
        data = cg.get_coin_market_chart_range_range_by_id(coin_id, vs_currency='usd', from_timestamp=(datetime.now() - timedelta(hours=1)).timestamp(), to_timestamp=datetime.now().timestamp())
        prices = data['prices']
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df_resampled = df.resample('1T').ohlc()  # 1 dakika aralıklarla
        return df_resampled
    except Exception as e:
        logging.error(f"Error getting chart data for {coin_id}: {e}")
        return pd.DataFrame()

async def get_chart_image(coin_id):
    df_resampled = await get_chart_data(coin_id)
    
    if df_resampled.empty:
        return None
    
    buf = io.BytesIO()
    mpf.plot(df_resampled, type='candle', style='charles', title=f"{coin_id.upper()} Son 1 Saat", ylabel='Fiyat (USD)', savefig=buf)
    buf.seek(0)
    
    return buf

@tasks.loop(minutes=3)
async def check_prices():
    session = Session()
    pairs = session.query(CorrelatedPair).all()
    
    for pair in pairs:
        try:
            # Get the current price for both coins
            current_price1 = await get_current_price(pair.coin1.lower())
            current_price2 = await get_current_price(pair.coin2.lower())
            
            # Calculate the percentage change from the last check
            last_price1 = pair.last_price1
            last_price2 = pair.last_price2
            
            change1 = ((current_price1 - last_price1) / last_price1) * 100 if last_price1 > 0 else 0
            change2 = ((current_price2 - last_price2) / last_price2) * 100 if last_price2 > 0 else 0
            
            if abs(change1) >= 0.25 or abs(change2) >= 0.25:
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

            # Update last prices
            pair.last_price1 = current_price1
            pair.last_price2 = current_price2
            session.commit()
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
