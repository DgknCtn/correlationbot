import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import io
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pycoingecko import CoinGeckoAPI

# Ortam değişkenlerini yükleyin
load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_ID = 1283749840018346005

# Bot ve CoinGeckoAPI ayarları
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
cg = CoinGeckoAPI()

async def get_chart_data(coin_id):
    try:
        data = cg.get_coin_market_chart_range_by_id_range(coin_id, vs_currency='usd', from_timestamp=int((datetime.utcnow() - timedelta(hours=1)).timestamp()), to_timestamp=int(datetime.utcnow().timestamp()))
        prices = data['prices']
        dates = [datetime.fromtimestamp(price[0] / 1000) for price in prices]
        values = [price[1] for price in prices]
        return dates, values
    except Exception as e:
        print(f"Error getting chart data for {coin_id}: {e}")
        return [], []

async def get_chart_image(coin_id):
    dates, values = await get_chart_data(coin_id)
    
    if not dates or not values:
        return None
    
    plt.figure(figsize=(10, 5))
    plt.plot(dates, values, color='blue')
    plt.title(f"{coin_id.upper()} Son 1 Saat")
    plt.xlabel("Tarih")
    plt.ylabel("Fiyat (USD)")
    plt.xticks(rotation=45)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    return buf

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı!')

@bot.command()
async def test(ctx):
    # Örnek olarak Floki için veri al
    coin_id = 'floki-inu'
    chart_image = await get_chart_image(coin_id)
    
    if chart_image:
        await ctx.send(f"{coin_id.upper()} grafik", file=discord.File(chart_image, filename=f"{coin_id}_chart.png"))
    else:
        await ctx.send(f"{coin_id.upper()} grafik verisi alınamadı")

if __name__ == '__main__':
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Bot başlatılamadı: {e}")
