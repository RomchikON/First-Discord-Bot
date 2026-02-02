import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()
token = os.getenv('TOKEN')

# Настройки прав (Интенты)
intents = discord.Intents.default()
intents.message_content = True 

# Создаем бота
bot = commands.Bot(command_prefix='!', intents=intents)

# Событие: Бот готов к работе
@bot.event
async def on_ready():
    print(f'------------------------------------')
    print(f'Бот запущен! Имя: {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print(f'------------------------------------')

# Команда: !ping
@bot.command()
async def ping(ctx):
    await ctx.send('Pong! 🏓 Я работаю с твоего сервера!')

@bot.command(name='h')
async def commands_list(ctx):
    embed = discord.Embed(title="Справка по командам", description="Список доступных команд:", color=discord.Color.blue())
    embed.add_field(name="!ping", value="Проверка работы бота", inline=False)
    embed.add_field(name="!check [текст]", value="Вывести информацию о сообщении в консоль", inline=False)
    embed.add_field(name="!status [dnd/online/idle/offline]", value="Изменить статус бота", inline=False)
    embed.add_field(name="!команды", value="Показать эту справку", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def check(ctx, arg):
    print(ctx.message)  # Выведет информацию о сообщении внутри ctx
    await ctx.send(f"Посмотри в консоль! Сообщение: {arg}")

# Переменная для хранения текста статуса (объявлена вне функции)
current_status_text = None



current_status_text = None

@bot.command()
async def status(ctx, arg, *, status: str = None):
    """
    Меняет статус бота.
    
    Аргументы:
    arg    -- Режим (set, online, dnd, idle, offline)
    status -- Текст статуса (только для режима set)
    
    Примеры:
    !status set Minecraft
    !status dnd
    !status online
    """
    global current_status_text

    # Если текст был сохранен ранее, используем его
    activity_text = discord.Game(name=current_status_text) if current_status_text else None

    # Приводим аргумент к нижнему регистру для удобства
    arg = arg.lower()

    if arg == "set":
        if status:
            current_status_text = status 
            await bot.change_presence(activity=discord.Game(name=status))
            await ctx.send(f"Текст статуса сохранен: {status}")
            print(f"Текст статуса сохранен: {status}")
        else:
            await ctx.send("Укажите текст для статуса")
            print("Ошибка: попытка изменить текст без аргумента")

    elif arg == "dnd":
        await bot.change_presence(status=discord.Status.do_not_disturb, activity=activity_text)
        await ctx.send("Статус изменен на: do_not_disturb (DND)")
        print("Статус изменен на: do_not_disturb (DND)")

    elif arg == "online":
        await bot.change_presence(status=discord.Status.online, activity=activity_text)
        await ctx.send("Статус изменен на: online")
        print("Статус изменен на: online")

    elif arg == "idle":
        await bot.change_presence(status=discord.Status.idle, activity=activity_text)
        await ctx.send("Статус изменен на: idle")
        print("Статус изменен на: idle")

    elif arg == "offline":
        await bot.change_presence(status=discord.Status.invisible)
        await ctx.send("Статус изменен на: invisible (offline)")
        print("Статус изменен на: invisible (offline)")

    else:
        await ctx.send("Неверный статус! Используйте: dnd, online, idle, offline или set")
        print(f"Ошибка: введен неверный аргумент '{arg}'")

#Запуск бота
try:
    bot.run(token)
except Exception as e:
    print(f"Ошибка при запуске: {e}")