import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import os
from dotenv import load_dotenv
import time as time_module
from datetime import datetime, timezone

# Общий UI-стиль для Embed'ов
class Ui:
    INFO_COLOR = discord.Color(0x5865F2)  # #5865F2
    SUCCESS_COLOR = discord.Color(0x57F287)  # #57F287
    WARN_COLOR = discord.Color(0xFEE75C)  # #FEE75C
    ERROR_COLOR = discord.Color(0xED4245)  # #ED4245

    @staticmethod
    # Базовый метод для создания Embed'ов
    def _base(
        title: str,
        description: str | None,
        color: discord.Color,
        prefix: str,
    ) -> discord.Embed:
        embed = discord.Embed(
            title=f"{prefix} {title}",
            description=description,
            color=color,
            timestamp=datetime.now(timezone.utc),
        )

        # Устанавливаем футер
        embed.set_footer(text="CultOfTea.bot")
        # Возвращаем созданный Embed
        return embed
    
    @staticmethod
    # Метод для информационных сообщений
    def info(title: str, description: str | None = None) -> discord.Embed:
        return Ui._base(title, description, Ui.INFO_COLOR, "ℹ️")
    
    # Метод для успешных сообщений
    @staticmethod
    def success(title: str, description: str | None = None) -> discord.Embed:
        return Ui._base(title, description, Ui.SUCCESS_COLOR, "✅")
    
    # Метод для предупреждающих сообщений
    @staticmethod
    def warn(title: str, description: str | None = None) -> discord.Embed:
        return Ui._base(title, description, Ui.WARN_COLOR, "⚠️")
    
    # Метод для сообщений об ошибках
    @staticmethod
    def error(title: str, description: str | None = None) -> discord.Embed:
        return Ui._base(title, description, Ui.ERROR_COLOR, "❌")



# Загружаем переменные из файла .env
load_dotenv()
token = os.getenv('TOKEN')
channel_id = os.getenv('CHAT_ID')

# Горячие гильдии для быстрой загрузки команд
def parse_guild_ids(raw_guild_ids: str | None) -> list[int]:
    # Если переменная окружения не задана, возвращаем пустой список
    if not raw_guild_ids:
        return []
    
    # Парсим строку с ID гильдий, поддерживаем разделение через запятую или точку с запятой
    parsed_ids: list[int] = []
    for value in raw_guild_ids.replace(";", ",").split(","):
        # Чистим значение от пробелов
        value = value.strip()
        if not value:
            continue

        # Пытаемся преобразовать значение в целое число и добавить в список, если это возможно
        try:
            parsed_ids.append(int(value))
        except ValueError:
            print(f"Пропущен некорректный GUILD_ID: {value}")

    return parsed_ids

# Получаем горячие гильдии из переменных окружения
GUILD_IDS = parse_guild_ids(os.getenv('GUILD_IDS'))

# Настройки прав (нтенты)
intents = discord.Intents.default()
intents.message_content = True 

# Создаем бота(Оставил пока что префикс пусть будет)
bot = commands.Bot(command_prefix='!', intents=intents)

# Событие: Бот готов к работе
@bot.event
async def on_ready():
    print(f'Бот запущен! Имя: {bot.user.name}')
    print(f'ID: {bot.user.id}')

    # Синхронизация команд с горячими гильдиями (быстрая регистрация)
    try:
        if GUILD_IDS:
            total_synced = 0
            for guild_id in GUILD_IDS:
                guild = discord.Object(id=guild_id)
                # Копируем глобальные команды в гильдию и синхронизируем
                bot.tree.copy_global_to(guild=guild)
                try:
                    synced = await bot.tree.sync(guild=guild)
                    total_synced += len(synced)
                    print(f'Синхронизировано команд для гильдии {guild_id}: {len(synced)}')
                # Обработка ошибки отсутствия доступа к гильдии
                except discord.Forbidden:
                    print(f'Нет доступа к гильдии {guild_id} для sync (Missing Access).')
                # Обработка других ошибок HTTP
                except discord.HTTPException as sync_error:
                    print(f'Ошибка sync для гильдии {guild_id}: {sync_error}')

            # Вывод общего количества синхронизированных команд
            if total_synced > 0:
                print(f'Всего синхронизировано команд (горячие гильдии): {total_synced}')
            #
            else:
                print('Не удалось синхронизировать горячие гильдии, пробуем глобальную sync...')
                synced = await bot.tree.sync()
                print(f'Синхронизировано команд глобально: {len(synced)}')
        else:
            # Если горячие гильдии не заданы — синхронизируем глобально
            synced = await bot.tree.sync()
            print(f'Синхронизировано команд глобально: {len(synced)}')
    # Обработка общей ошибки синхронизации
    except Exception as e:
        print(f'Ошибка синхронизации: {e}')



# Команда: /help
@bot.tree.command(name="help", description="Показать все команды")
async def help(interaction: discord.Interaction):

    # Создаем embed
    embed = Ui.info(
        "Все команды",
        "Вот список того, что я умею\n",
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

    embed.add_field(name="Всего команд", value=str(len(commands_list)-1), inline=False)
    
    # Отправка сформированого embed'а
    await interaction.response.send_message(embed=embed)



# Command: /cult
@bot.tree.command(name="cult", description="Основные ресурсы и информация о Культе Чая")
@app_commands.describe(
    hide="Сделать ответ видимым только вам"
)
async def cult(interaction: discord.Interaction, hide: bool = False):
    resources = [
        {"label": "🌐Сайт", "url": "https://www.cultoftea.pp.ua/"},
        {"label": "📣Телеграмм", "url": "https://t.me/+szwXPoF0_PcwOWYy"},
        {"label": "⬇️Предложить функционал", "url": "https://github.com/RomchikON/First-Discord-Bot/issues"},
        {"label": "💰Поддержать проект", "url": "https://patreon.com/CultOfTea"},
    ]

    # Создаем View для кнопок
    view = discord.ui.View(timeout=None)
    for resource in resources:
        view.add_item(
            discord.ui.Button(
                # Тип кнопки - ссылка
                style=discord.ButtonStyle.link,
                label=resource["label"],
                url=resource["url"],
            )
        )

    # Создаем Embed через общий UI-стиль
    embed = Ui.info(
        "Cult of Tea • Навигация",
        "Официальные ресурсы проекта в одном месте.",
    )

    # Отправляем сообщение с embed и кнопками
    await interaction.response.send_message(embed=embed, view=view, ephemeral=hide)
    print(f"Пользователь:{interaction.user} использовал комманду cult")



# Команда: /ping
@bot.tree.command(name="ping",description="Проверка связи с ботом")
async def ping(interaction: discord.Interaction):
    embed = Ui.info(
        "Сосибля",
        f"Пинг: **{round(bot.latency*1000)}ms**",
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
    print(f"Пользователь:{interaction.user} использовал комманду ping")



# Команда: /status
# Переменные для хранения статуса и его текста (объявлена вне функции)
current_status_text = None
current_status = "online"
# ндексация команды и ее аргументов
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
    embed = Ui.info(
        "Случайные команды",
        f"Всего участников: **{len(people)}** | Команд: **{teams_count}**",
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



# Команда: /rgif
@bot.tree.command(name="rgif", description="Рандомная гифка/изображение с чата Культа Чая за определённый период")
@app_commands.describe(
    period="Период из которого брать гифки",
    channel="Канал для поиска (если не указан, то базовый)",
    images="Включить изображения",
    hide="Сделать ответ видимым только вам"
)
@app_commands.choices(period=[
    app_commands.Choice(name="День", value="день"),
    app_commands.Choice(name="Неделя", value="неделя"),
    app_commands.Choice(name="Месяц", value="месяц"),
    app_commands.Choice(name="Всё время", value="всё")
])
async def rgif(
    interaction: discord.Interaction, 
    period: str, 
    channel: discord.TextChannel | None = None,
    images: bool = False,
    hide: bool = False
):
    # Берем канал из параметра команды или из CHAT_ID
    target_channel = channel
    if target_channel is None and channel_id:
        target_channel = bot.get_channel(int(channel_id))

    # Проверка существования канала
    if not target_channel:
        await interaction.response.send_message("❌: Не удалось найти канал!", ephemeral=True)
        return
    
    # Проверка что канал является текстовым
    if not isinstance(target_channel, discord.TextChannel):
        await interaction.response.send_message("❌: Канал должен быть текстовым!", ephemeral=True)
        return
    
    # Словарь с периодами в секундах
    periods = {
        "день": 86400,
        "неделя": 604800,
        "месяц": 2592000,
        "всё": None
    }

    # Получаем лимит времени для выбранного периода
    time_limit = periods[period]
    period_label = period
    # Получаем текущее время в UTC
    current_time = discord.utils.utcnow()
    # Список для хранения найденных гифок и их сообщений
    gifs = []
    gif_messages = []
    # Счетчик обработанных сообщений
    message_count = 0
    # Время начала поиска
    start_time = time_module.time()

    # Создаем начальный embed для статуса поиска
    status_embed = Ui.warn(
        "Поиск медиа...",
        "дет сканирование истории сообщений",
    )
    # Откладываем ответ на взаимодействие (defer) для долгой обработки
    await interaction.response.defer()
    status_message: discord.Message | None = None
    try:
        status_message = await interaction.followup.send(embed=status_embed)
    except:
        status_message = None

    # Получаем всю историю канала с лимитом None (все сообщения)
    async for message in target_channel.history(limit=None):
        # Проверяем не превышен ли временной лимит
        if time_limit:
            if (current_time - message.created_at).total_seconds() > time_limit:
                break
        
        # Увеличиваем счетчик обработанных сообщений
        message_count += 1
        
        # Обновляем статус каждые 50 сообщений
        if message_count % 50 == 0:
            # Получаем прошедшее время
            elapsed = time_module.time() - start_time
            
            # Создаем обновленный embed со статусом
            status_embed = Ui.warn(
                "Поиск медиа...",
                f"Обработано: **{message_count}** сообщений\nНайдено: **{len(gifs)}** медиа\nВремя: **{elapsed:.1f}с**",
            )
            try:
                # Редактируем сообщение статуса если оно существует
                if status_message:
                    await status_message.edit(embed=status_embed)
            except:
                pass
        
        # Перебираем все вложения в сообщении
        for attachment in message.attachments:
            # Получаем имя файла в нижнем регистре
            filename = attachment.filename.lower()
            # Проверяем расширение файла (gif или изображение если включено)
            if filename.endswith('.gif') or (images and filename.endswith(('.png', '.jpg', '.jpeg'))):
                gifs.append(attachment.url)
                gif_messages.append(message)
        
        # Проверяем ссылки в контенте сообщения
        if message.content:
            # Разбиваем контент на слова
            words = message.content.split()
            for word in words:
                # Проверяем начинается ли слово с http (URL)
                if word.startswith('http'):
                    # Проверяем расширение файла в конце URL
                    if word.lower().endswith(('.gif', '.png', '.jpg', '.jpeg')):
                        gifs.append(word)
                        gif_messages.append(message)
        
        # Небольшая задержка для избежания rate limit от Discord
        await asyncio.sleep(0.01)

    # Получаем итоговое время поиска
    elapsed = time_module.time() - start_time

    # Если медиа не найдено
    if not gifs:
        try:
            # Удаляем сообщение статуса
            if status_message:
                await status_message.delete()
        except:
            pass
        # Отправляем сообщение об ошибке с учетом эфимерности
        await interaction.followup.send(f"⚠️За период '{period_label}' медиа не найдено.", ephemeral=hide)
        return
    
    # Выбираем случайную гифку из найденных
    random_index = random.randint(0, len(gifs) - 1)
    selected_gif = gifs[random_index]
    selected_message = gif_messages[random_index]

    # Создаем финальный embed с результатами поиска
    result_embed = Ui.success(
        "Поиск завершен",
        f"Всего медиа найдено: **{len(gifs)}**\nОбработано сообщений: **{message_count}**\nВремя поиска: **{elapsed:.2f}с**\nАвтор: {selected_message.author.mention}\n[Ссылка на сообщение]({selected_message.jump_url})",
    )
    # Устанавливаем изображение в embed
    result_embed.set_image(url=selected_gif)
    
    # Пытаемся удалить сообщение статуса
    try:
        # Удаляем сообщение статуса если оно существует
        if status_message:
            await status_message.delete()
    except:
        pass
    
    # Отправляем финальный результат с учетом параметра эфимерности
    await interaction.followup.send(embed=result_embed, ephemeral=hide)
    print(f"Пользователь:{interaction.user} использовал комманду rgif с параметром период: {period_label}, канал: {target_channel.id}, включить изображения: {images}, ссылки: включены, эфимерность: {hide}")



#Запуск бота
try:
    bot.run(token)
except Exception as e:
    print(f"Ошибка при запуске: {e}")
