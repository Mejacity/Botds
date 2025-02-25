import discord
from discord.ext import commands
from datetime import datetime
import csv

# Включаем intents для чтения сообщений
intents = discord.Intents.default()
intents.message_content = True  # Важно!

# Создаём бота с префиксом "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# ID канала для вывода логов
LOG_CHANNEL_ID = 1295468599745450137  # ID канала, куда будет выводиться информация о пробеге

log_file = "message_log.txt"
data_file = "player_data.csv"


# Читаем сообщения
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Игнорируем сообщения бота

    # Получаем текущее время и форматируем его
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Выводим сообщение в консоль с датой
    if message.content:  # Если текстовое содержимое
        print(f"[{current_time}] Сообщение от {message.author}: {message.content}")
    elif message.embeds:  # Если сообщение с Embed
        print(f"[{current_time}] Сообщение от {message.author} с Embed:")
        for embed in message.embeds:
            print(f"  Заголовок Embed: {embed.title}")
            print(f"  Описание Embed: {embed.description}")
            if embed.author:
                print(f"  Автор Embed: {embed.author.name}")
            if embed.footer:
                print(f"  Footer Embed: {embed.footer.text}")
            if embed.fields:
                for field in embed.fields:
                    print(f"  Поле Embed: {field.name} - {field.value}")
    elif message.attachments:  # Если есть вложения
        print(f"[{current_time}] Сообщение от {message.author} с вложением: ")
        for attachment in message.attachments:
            print(f"  Вложение: {attachment.url}")  # Выводим ссылку на вложение

    # Запись в лог-файл
    with open(log_file, "a", encoding="utf-8") as f:
        if message.content:  # Если текстовое содержимое
            f.write(f"[{current_time}] Сообщение от {message.author}: {message.content}\n")
        elif message.embeds:  # Если сообщение с Embed
            f.write(f"[{current_time}] Сообщение от {message.author} с Embed:\n")
            for embed in message.embeds:
                f.write(f"  Заголовок Embed: {embed.title}\n")
                f.write(f"  Описание Embed: {embed.description}\n")
                if embed.author:
                    f.write(f"  Автор Embed: {embed.author.name}\n")
                if embed.footer:
                    f.write(f"  Footer Embed: {embed.footer.text}\n")
                if embed.fields:
                    for field in embed.fields:
                        f.write(f"  Поле Embed: {field.name} - {field.value}\n")
        elif message.attachments:  # Если есть вложения
            f.write(f"[{current_time}] Сообщение от {message.author} с вложением:\n")
            for attachment in message.attachments:
                f.write(f"  Вложение: {attachment.url}\n")

    # Важно: После того как обработали сообщение, нужно вызвать функцию обработки логов
    process_log(log_file, data_file)


# Обработка логов и сохранение данных
def process_log(log_file, data_file):
    player_data = {}
    current_author = ""
    current_distance = 0
    current_day = datetime.now().strftime("%Y-%m-%d")

    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if "Автор Embed:" in line:
                current_author = line.split(":", 1)[1].strip()
            elif "Поле Embed: Distance" in line:
                current_distance = int(''.join(filter(str.isdigit, line)))  # Извлекаем число из строки

            if current_author and current_distance:
                if current_author not in player_data:
                    player_data[current_author] = {"week_total": 0, "day_total": 0, "days": {}}

                player_data[current_author]["week_total"] += current_distance
                player_data[current_author]["day_total"] += current_distance
                if current_day not in player_data[current_author]["days"]:
                    player_data[current_author]["days"][current_day] = []
                player_data[current_author]["days"][current_day].append(f"Distance: {current_distance}km")

                current_author = ""
                current_distance = 0

    save_data(data_file, player_data)


def save_data(data_file, player_data):
    with open(data_file, "w+", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = ["Игрок", "Недельный накат", "Дневной накат"] + sorted(set(day for p in player_data.values() for day in p["days"]))
        writer.writerow(header)

        for player, stats in player_data.items():
            row = [player, stats["week_total"], stats["day_total"]]
            for day in header[3:]:
                row.append(" | ".join(stats["days"].get(day, [])))
            writer.writerow(row)


# Чтение данных из CSV-файла
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


# Команда для отправки статистики вручную
@bot.command(name='статистика')
async def fetch_stats(ctx):
    """Команда для ручного вызова статистики."""
    response = load_player_data(data_file)
    await ctx.send(f"📊 **Пробег участников:**\n{response}")


# Запуск бота с твоим токеном
TOKEN = "MTM0MjUwOTcyMDE0NTEwNTA0OQ.GySKDK.E5_rhvx4m7sdFFvtKTJ5MTNIKQBMC8QSHSb-Yo"  # Не забывайте заменить на ваш реальный токен
@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")

bot.run(TOKEN)
