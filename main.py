import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()
token = os.getenv('TOKEN')

# Настройки прав (Интенты)
intents = discord.Intents.default()
intents.message_content = True 

# Создаем бота(Оставил пока что префикс пусть будет)
bot = commands.Bot(command_prefix='!', intents=intents)

# Событие: Бот готов к работе
@bot.event
async def on_ready():
    print(f'Бот запущен! Имя: {bot.user.name}')
    print(f'ID: {bot.user.id}')

    # Синхронизация всех комманд с серверами Discord
    try:
        synced = await bot.tree.sync()
        print(f'Синхронизировано команды: {synced}')
    except Exception as e:
        print(f'Ошибка синхронизации: {e}')



# Команда: /ping
@bot.tree.command(name="ping",description="Проверка связи с ботом")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong!(Ping: {round(bot.latency*1000)}ms)")
    print(f"Пользователь:{interaction.user} использовал комманду ping")


# Команда: /status
# Переменные для хранения статуса и его текста (объявлена вне функции)
current_status_text = None
current_status = "online"

# Индексация команды и ее аргументов
@bot.tree.command(name="status", description="Управление статусом бота")
@app_commands.describe(arg="Выбери статус", status="Текст статуса")
@app_commands.choices(arg=[
    app_commands.Choice(name="В сети", value="online"),
    app_commands.Choice(name="Не беспокоить", value="dnd"),
    app_commands.Choice(name="Не активен", value="idle"),
    app_commands.Choice(name="Невидимка", value="offline"),
    app_commands.Choice(name="Установить текст", value="set")
])
# Запуск асинхронной функции
async def status(interaction: discord.Interaction, arg: app_commands.Choice[str], status: str = None):
    # Обявление функций как глобальных
    global current_status_text
    global current_status

    # Перевод аргументов из пакета Interaction в переменную для дальнейшей работы
    selected_arg = arg.value

    # Проверка наличия статуса
    if status:
        current_status_text = status
        activity_text = discord.Game(name=status)
    else:
        activity_text = discord.Game(name=current_status_text) if current_status_text else None

    # Обработка аргумента set
    if selected_arg == "set":
        if status:
            current_status_text = status # Запоминаем текст
            await bot.change_presence(status=current_status, activity=discord.Game(name=status))
            await interaction.response.send_message(f"Текст статуса сохранен: {status}")
            print(f"Текст статуса сохранен: {status}")
        else:
            # ephemeral=True означает, что ошибку увидит только ползователь вызвавший команду
            await interaction.response.send_message("Ошибка: Укажите текст в поле 'status'!", ephemeral=True)
            print("Ошибка: попытка изменить текст без аргумента")

    # Обработка аргумента dnd
    elif selected_arg == "dnd":
        current_status = discord.Status.dnd
        await bot.change_presence(status=discord.Status.do_not_disturb, activity=activity_text)
        await interaction.response.send_message("Статус изменен на: do_not_disturb (DND)")
        print("Статус изменен на: do_not_disturb (DND)")

    # Обработка аргумента online
    elif selected_arg == "online":
        current_status = discord.Status.online
        await bot.change_presence(status=discord.Status.online, activity=activity_text)
        await interaction.response.send_message("Статус изменен на: online")
        print("Статус изменен на: online")

    # Обработка аргумента idle
    elif selected_arg == "idle":
        current_status = discord.Status.idle
        await bot.change_presence(status=discord.Status.idle, activity=activity_text)
        await interaction.response.send_message("Статус изменен на: idle")
        print("Статус изменен на: idle")

    # Обработка аргумента offline
    elif selected_arg == "offline":
        await bot.change_presence(status=discord.Status.invisible)
        await interaction.response.send_message("Статус изменен на: invisible (offline)")
        print("Статус изменен на: invisible (offline)")
   
#Запуск бота
try:
    bot.run(token)
except Exception as e:
    print(f"Ошибка при запуске: {e}")