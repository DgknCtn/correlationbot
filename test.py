import discord
from discord.ext import commands, tasks
import asyncio
import aiohttp
from tradingview_ta import TA_Handler, Interval
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import CorrelatedPair
from io import BytesIO
import base64
import logging

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
CHART_SERVER_URL = 'http://localhost:5001/get_chart'  # Port 5001

# Database setup
engine = create_engine('sqlite:///crypto_pairs.db')
Session = sessionmaker(bind=engine)

bot = commands.Bot(command_prefix='!', intents=intents)

async def get_price_change(symbol):
    handler = TA_Handler(
        symbol=symbol,
        screener="crypto",
        exchange="BINANCE",
        interval=Interval.INTERVAL_3_MINUTE
    )
    analysis = handler.get_analysis()
    return analysis.indicators["change"]

async def get_chart_image(symbol):
    async with aiohttp.ClientSession() as session:
        async with session.post(CHART_SERVER_URL, json={'symbol': symbol}) as response:
            response_json = await response.json()
            if 'image' in response_json:
                image_data = response_json['image']
                image_binary = base64.b64decode(image_data)
                return BytesIO(image_binary)
            else:
                raise KeyError("Yanıt JSON'unda 'image' anahtarı bulunamadı.")

@tasks.loop(minutes=3)  # 5 dakika aralıklarla kontrol
async def check_prices():
    session = Session()
    pairs = session.query(CorrelatedPair).all()
    
    for pair in pairs:
        try:
            change1 = await get_price_change(pair.coin1)
            if abs(change1) >= 0.25:  # %0.25 değişim
                change2 = await get_price_change(pair.coin2)
                
                chart1 = await get_chart_image(pair.coin1)
                chart2 = await get_chart_image(pair.coin2)
                
                channel = bot.get_channel(CHANNEL_ID)
                files = [
                    discord.File(chart1, filename=f"{pair.coin1}_chart.png"),
                    discord.File(chart2, filename=f"{pair.coin2}_chart.png")
                ]
                
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
