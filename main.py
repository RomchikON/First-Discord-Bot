import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
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



# Команда: /help
@bot.tree.command(name="help", description="Показать все команды")
async def help(interaction: discord.Interaction):

    # Создаем embed
    embed = discord.Embed(
        title="Все команды",
        description="Вот список того, что я умею\n",
        color=discord.Color.from_rgb(36, 36, 41)
    )

    # Получаем все команды как обекты
    commands_list = bot.tree.get_commands()

    # Перебор каждой команды
    for command in commands_list:
        if command.name == "help":
            continue
        
        # Довавляем / названию
        command_name = f"/{command.name}"

        # Добавляем форматирование тексту
        command_description = f"```{command.description}```" or "```Описание отсутствует```"

        # Добавляем поле с текстом
        embed.add_field(name=command_name, value=f"{command_description}", inline=False)

    embed.set_footer(text=f"Всего команд: {len(commands_list)-1}")
    
    # Отправка сформированого embed'а
    await interaction.response.send_message(embed=embed)



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



# Команда: /randomteams
@bot.tree.command(name="randomteams", description="Разделение людей на случайные команды")
@app_commands.describe(
    teams_count="Сколько команд нужно создать?",
    voice_channel="[Режим 1] Выберите голосовой канал",
    exclude="[Режим 1] Кого исключить (упомяните @User через пробел)",
    items_text="[Режим 2] Список имен или слов через пробел/запятую"
)
async def randomteams(
    interaction: discord.Interaction, 
    teams_count: int, 
    voice_channel: discord.VoiceChannel = None, 
    exclude: str = None,
    items_text: str = None
):
    # Предохранитель 1: Отсутствие участников распределения
    if not voice_channel and not items_text:
        await interaction.response.send_message("Ошибка, вы не предоставили учасников, укажите *список участников* либо **голосовой канал**!", ephemeral=True)
        return
    
    # Предохранитель 2: Указано два метода распределения
    if voice_channel and items_text:
        await interaction.response.send_message("Ошибка, вы указали два метода одновременно, допустим лишь **один**", ephemeral=True)
        return
    
    # Создем пул людей
    people = []

    # Если как аргемент указан войс
    if voice_channel:
        members = voice_channel.members

        # Проверка есть ли люди в войсе
        if not members:
            await interaction.response.send_message(f"В канале {voice_channel.mention} пусто!", ephemeral=True)
            return

        # Проверка совпадает ли человек со списком исключений, или является ботом, если нет то добавить в пул
        for member in members:
            if exclude and (member.mention in exclude or str(member.id) in exclude):
                continue
            if not member.bot:
                people.append(member.mention)

    # Если как аргумент указан список людей    
    elif items_text:
        # Меняем запятые на пробелы для корректной последующей обработки
        clean_text = items_text.replace(',',' ')
        # Создаем список слов роздяляя их по пробелам
        raw_words = clean_text.split(' ')
        # Чистим список от пробелов
        for word in raw_words:
            if word:
                people.append(word)

    # Предохранитель 3: Людей меньше чем команд    
    if len(people) < teams_count:
        await interaction.response.send_message("Вы указали больше команд чем людей", ephemeral=True)
        return
    
    # Главная часть, перемешиваем участников
    random.shuffle(people)
    # Создаем список команд
    teams = []
    # Добавляем списки в список команд
    for i in range(teams_count):
        teams.append([])
    
    # Распределяем людей по командам
    count = 0
    for name in people:
        team_index = count % teams_count
        teams[team_index].append(name)
        count+=1
    
    # Начинаем собирать embed
    embed = discord.Embed(
        title="🎲 Случайные команды", 
        description=f"Всего участников: **{len(people)}** | Команд: **{teams_count}**",
        color=discord.Color.blue()
    )

    # Добавляем форматирование никнеймам
    for i, team in enumerate(teams):
        formatted_names = []
        for name in team:
            new_name=f"- {name}"
            formatted_names.append(new_name)

        team_list = "\n".join(formatted_names)

        # Проверка на всякий случай, если вдруг список списков участников окажется пустым
        if not team_list:
            team_list = "—"
        
        # Добавляем команду в embed
        embed.add_field(name=f"🏆 Команда {i + 1}", value=team_list, inline=False)

    # Отправляем собранный embed
    await interaction.response.send_message(embed=embed)



#Запуск бота
try:
    bot.run(token)
except Exception as e:
    print(f"Ошибка при запуске: {e}")