import discord
from discord.ext import commands, tasks
import csv
from datetime import datetime, timedelta
import pytz

# Включаем intents для чтения сообщений
intents = discord.Intents.default()
intents.message_content = True  # Важно!

# Создаём бота с префиксом "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# ID канала для вывода логов
LOG_CHANNEL_ID = 1295468599070298153  # Укажи ID нужного канала

data_file = "player_data.csv"

# Устанавливаем часовой пояс Москвы
moscow_tz = pytz.timezone("Europe/Moscow")


def load_player_data(file_path):
    """Читает CSV-файл и формирует строку с данными игроков."""
    players = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                nickname = row.get("Игрок", "Неизвестный")
                weekly_mileage = row.get("Недельный накат", "0 км")
                daily_mileage = row.get("Дневной накат", "0 км")
                players.append(f"{nickname} - {weekly_mileage} | {daily_mileage}")
    except FileNotFoundError:
        return "Ошибка: файл с данными не найден!"
    except Exception as e:
        return f"Ошибка при чтении данных: {e}"

    return "\n".join(players) if players else "Нет данных о пробеге."


@bot.command(name='статистика')
async def fetch_stats(ctx):
    """Команда для ручного вызова статистики."""
    response = load_player_data(data_file)
    await ctx.send(f"📊 **Пробег участников:**\n{response}")


@tasks.loop(minutes=1)
async def daily_stat_update():
    """Функция отправки статистики каждый день в 20:00 по МСК."""
    now = datetime.now(moscow_tz)
    if now.hour == 20 and now.minute == 0:  # Проверяем, 20:00 ли по Москве
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            response = load_player_data(data_file)
            await channel.send(f"📊 **Ежедневный отчет о пробеге участников:**\n{response}")


@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    daily_stat_update.start()

# Запуск бота с твоим токеном
TOKEN = "MTM0MjUwOTcyMDE0NTEwNTA0OQ.GySKDK.E5_rhvx4m7sdFFvtKTJ5MTNIKQBMC8QSHSb-Yo"
bot.run(TOKEN)
