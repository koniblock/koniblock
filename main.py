import discord
from discord.ext import commands
import asyncio
import random
import json
import time
import os
from datetime import datetime, timedelta

# Konfiguracja bota
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Plik do przechowywania danych użytkowników
DATA_FILE = "user_data.json"

# ID roli admina
ADMIN_ROLE_ID = 1429512100958703906

# Struktura danych użytkownika
user_data = {}

# Ceny Lucky Blocków
SHOP_ITEMS = {
    "Basic Lucky Block": 1000,
    "Rare Lucky Block": 2500,
    "Epic Lucky Block": 10000,
    "Legendary Lucky Block": 50000,
    "Secret Lucky Block": 125000,
    "Extinct Lucky Block": 500000
}

# Nagrody dla Lucky Blocków
LUCKY_BLOCK_REWARDS = {
    "Basic Lucky Block": [
        ("❌ Strata", -500, -250, 25),
        ("💵 Mały zysk", 400, 1000, 35),
        ("💰 Średni zysk", 1000, 2000, 20),
        ("💎 Duży zysk", 2500, 4000, 10),
        ("☘️ 4-listna koniczynka", "clover_4", None, 6),
        ("🍀 5-listna koniczynka", "clover_5", None, 3),
        ("🌈 7-listna koniczynka", "clover_7", None, 1)
    ],
    "Rare Lucky Block": [
        ("❌ Strata", -500, -250, 25),
        ("💵 Mały zysk", 400, 1000, 35),
        ("💰 Średni zysk", 1000, 2000, 20),
        ("💎 Duży zysk", 2500, 4000, 10),
        ("☘️ 4-listna koniczynka", "clover_4", None, 6),
        ("🍀 5-listna koniczynka", "clover_5", None, 3),
        ("🌈 7-listna koniczynka", "clover_7", None, 1)
    ],
    "Epic Lucky Block": [
        ("❌ Strata", -2000, -1000, 30),
        ("💵 Zysk", 2000, 5000, 30),
        ("💰 Duży zysk", 6000, 9000, 20),
        ("💎 Ogromny zysk", 10000, 15000, 10),
        ("☘️ 4-listna koniczynka", "clover_4", None, 4),
        ("🍀 5-listna koniczynka", "clover_5", None, 3),
        ("🌈 7-listna koniczynka", "clover_7", None, 2),
        ("🌟 9-listna koniczynka", "clover_9", None, 1)
    ],
    "Legendary Lucky Block": [
        ("💀 Wielka strata", -20000, -10000, 25),
        ("💵 Średni zysk", 20000, 40000, 25),
        ("💰 Duży zysk", 50000, 75000, 15),
        ("💎 Jackpot", 100000, 250000, 10),
        ("☘️ 4-listna koniczynka", "clover_4", None, 8),
        ("🍀 5-listna koniczynka", "clover_5", None, 5),
        ("🌈 7-listna koniczynka", "clover_7", None, 2),
        ("🌟 9-listna koniczynka", "clover_9", None, 0.5)
    ],
    "Secret Lucky Block": [
        ("💀 Katastrofa", -75000, -50000, 20),
        ("💵 Zysk", 50000, 100000, 25),
        ("💰 Duży zysk", 150000, 300000, 20),
        ("💎 Jackpot", 400000, 600000, 10),
        ("☘️ 4-listna koniczynka", "clover_4", None, 6),
        ("🍀 5-listna koniczynka", "clover_5", None, 5),
        ("🌈 7-listna koniczynka", "clover_7", None, 3),
        ("🌟 9-listna koniczynka", "clover_9", None, 1)
    ],
    "Extinct Lucky Block": [
        ("💀 Katastrofalna strata", -300000, -200000, 25),
        ("💵 Zysk", 200000, 400000, 25),
        ("💰 Duży zysk", 500000, 800000, 15),
        ("💎 Jackpot", 1000000, 2000000, 5),
        ("☘️ 4-listna koniczynka", "clover_4", None, 10),
        ("🍀 5-listna koniczynka", "clover_5", None, 8),
        ("🌈 7-listna koniczynka", "clover_7", None, 4),
        ("🌟 9-listna koniczynka", "clover_9", None, 3)
    ]
}

# Czas trwania koniczynek (w sekundach)
CLOVER_DURATION = {
    "clover_4": 600,    # 10 minut
    "clover_5": 600,    # 10 minut
    "clover_7": 900,    # 15 minut
    "clover_9": 1800    # 30 minut
}

# Mnożniki koniczynek
CLOVER_MULTIPLIERS = {
    "clover_4": {"earnings": 1.5, "luck": 2},
    "clover_5": {"earnings": 2.0, "luck": 4},
    "clover_7": {"earnings": 3.0, "luck": 8},
    "clover_9": {"earnings": 4.0, "luck": 12}
}

def load_data():
    """Ładuje dane użytkowników z pliku"""
    global user_data
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                user_data = json.load(f)
    except Exception as e:
        print(f"Błąd przy ładowaniu danych: {e}")
        user_data = {}

def save_data():
    """Zapisuje dane użytkowników do pliku"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(user_data, f, indent=4)
    except Exception as e:
        print(f"Błąd przy zapisywaniu danych: {e}")

def get_user_data(user_id):
    """Pobiera dane użytkownika, tworząc nowy profil jeśli nie istnieje"""
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "balance": 0,
            "inventory": {},
            "active_clovers": {},
            "cooldowns": {
                "work1": 0,
                "work2": 0,
                "work3": 0
            }
        }
    return user_data[str(user_id)]

def get_active_multipliers(user_id):
    """Zwraca aktualne mnożniki użytkownika"""
    user = get_user_data(user_id)
    earnings_multiplier = 1.0
    luck_multiplier = 1.0
    
    current_time = time.time()
    expired_clovers = []
    
    for clover_type, expiry in user["active_clovers"].items():
        if current_time < expiry:
            earnings_multiplier *= CLOVER_MULTIPLIERS[clover_type]["earnings"]
            luck_multiplier *= CLOVER_MULTIPLIERS[clover_type]["luck"]
        else:
            expired_clovers.append(clover_type)
    
    # Usuń wygasłe koniczynki
    for clover in expired_clovers:
        del user["active_clovers"][clover]
    
    return earnings_multiplier, luck_multiplier

def has_admin_role(member):
    """Sprawdza czy użytkownik ma rolę admina"""
    return any(role.id == ADMIN_ROLE_ID for role in member.roles)

@bot.event
async def on_ready():
    """Event gdy bot jest gotowy"""
    load_data()
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

@bot.command(name='work1')
async def work1(ctx):
    """Praca poziom 1 - mały zarobek, krótki cooldown"""
    user_id = ctx.author.id
    user = get_user_data(user_id)
    
    current_time = time.time()
    cooldown_time = user["cooldowns"]["work1"]
    
    if current_time < cooldown_time:
        remaining = int(cooldown_time - current_time)
        await ctx.send(f"⏰ Musisz poczekać jeszcze {remaining} sekund przed ponownym użyciem !work1")
        return
    
    # Oblicz zarobki z uwzględnieniem mnożników
    earnings_multiplier, _ = get_active_multipliers(user_id)
    base_earnings = random.randint(1, 250)
    actual_earnings = int(base_earnings * earnings_multiplier)
    
    user["balance"] += actual_earnings
    user["cooldowns"]["work1"] = current_time + 300  # 5 minut cooldown
    
    save_data()
    
    embed = discord.Embed(
        title="🍀 Praca Poziom 1",
        description=f"Zarobiłeś **{actual_earnings}** koniczynek!",
        color=0x00ff00
    )
    if earnings_multiplier > 1.0:
        embed.add_field(name="Mnożnik", value=f"×{earnings_multiplier:.1f}", inline=True)
    embed.add_field(name="Nowy balans", value=f"{user['balance']} 🍀", inline=True)
    embed.add_field(name="Cooldown", value="5 minut", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='work2')
async def work2(ctx):
    """Praca poziom 2 - średni zarobek, ryzyko straty, średni cooldown"""
    user_id = ctx.author.id
    user = get_user_data(user_id)
    
    current_time = time.time()
    cooldown_time = user["cooldowns"]["work2"]
    
    if current_time < cooldown_time:
        remaining = int(cooldown_time - current_time)
        await ctx.send(f"⏰ Musisz poczekać jeszcze {remaining} sekund przed ponownym użyciem !work2")
        return
    
    # Oblicz zarobki z uwzględnieniem mnożników
    earnings_multiplier, _ = get_active_multipliers(user_id)
    base_earnings = random.randint(251, 750)
    actual_earnings = int(base_earnings * earnings_multiplier)
    
    # 30% szansy na stratę
    if random.random() < 0.3:
        loss = random.randint(0, 250)
        user["balance"] -= loss
        result_message = f"❌ Niestety, straciłeś **{loss}** koniczynek!\nZarabiasz **{actual_earnings}** koniczynek."
    else:
        loss = 0
        result_message = f"✅ Zarabiasz **{actual_earnings}** koniczynek!"
    
    user["balance"] += actual_earnings
    user["cooldowns"]["work2"] = current_time + 900  # 15 minut cooldown
    
    save_data()
    
    embed = discord.Embed(
        title="🍀 Praca Poziom 2",
        description=result_message,
        color=0xffa500 if loss == 0 else 0xff0000
    )
    if earnings_multiplier > 1.0:
        embed.add_field(name="Mnożnik", value=f"×{earnings_multiplier:.1f}", inline=True)
    embed.add_field(name="Nowy balans", value=f"{user['balance']} 🍀", inline=True)
    embed.add_field(name="Cooldown", value="15 minut", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='work3')
async def work3(ctx):
    """Praca poziom 3 - duży zarobek, wysokie ryzyko, długi cooldown"""
    user_id = ctx.author.id
    user = get_user_data(user_id)
    
    current_time = time.time()
    cooldown_time = user["cooldowns"]["work3"]
    
    if current_time < cooldown_time:
        remaining = int(cooldown_time - current_time)
        await ctx.send(f"⏰ Musisz poczekać jeszcze {remaining} sekund przed ponownym użyciem !work3")
        return
    
    # Oblicz zarobki z uwzględnieniem mnożników
    earnings_multiplier, _ = get_active_multipliers(user_id)
    base_earnings = random.randint(500, 1000)
    actual_earnings = int(base_earnings * earnings_multiplier)
    
    # 50% szansy na stratę
    if random.random() < 0.5:
        loss = random.randint(250, 500)
        user["balance"] -= loss
        result_message = f"💀 Niestety, straciłeś **{loss}** koniczynek!\nZarabiasz **{actual_earnings}** koniczynek."
    else:
        loss = 0
        result_message = f"🎉 Zarabiasz **{actual_earnings}** koniczynek!"
    
    user["balance"] += actual_earnings
    user["cooldowns"]["work3"] = current_time + 1800  # 30 minut cooldown
    
    save_data()
    
    embed = discord.Embed(
        title="🍀 Praca Poziom 3",
        description=result_message,
        color=0x00ff00 if loss == 0 else 0xff0000
    )
    if earnings_multiplier > 1.0:
        embed.add_field(name="Mnożnik", value=f"×{earnings_multiplier:.1f}", inline=True)
    embed.add_field(name="Nowy balans", value=f"{user['balance']} 🍀", inline=True)
    embed.add_field(name="Cooldown", value="30 minut", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='balance')
async def balance(ctx):
    """Sprawdza balans koniczynek użytkownika"""
    user_id = ctx.author.id
    user = get_user_data(user_id)
    
    earnings_multiplier, luck_multiplier = get_active_multipliers(user_id)
    
    embed = discord.Embed(
        title=f"💰 Balans {ctx.author.display_name}",
        color=0x00ff00
    )
    embed.add_field(name="Koniczynki", value=f"{user['balance']} 🍀", inline=False)
    
    # Aktywne koniczynki
    active_clovers_info = []
    current_time = time.time()
    for clover_type, expiry in user["active_clovers"].items():
        if current_time < expiry:
            remaining = int(expiry - current_time)
            minutes = remaining // 60
            seconds = remaining % 60
            clover_name = {
                "clover_4": "☘️ 4-listna",
                "clover_5": "🍀 5-listna", 
                "clover_7": "🌈 7-listna",
                "clover_9": "🌟 9-listna"
            }.get(clover_type, clover_type)
            active_clovers_info.append(f"{clover_name} ({minutes}m {seconds}s)")
    
    if active_clovers_info:
        embed.add_field(name="Aktywne koniczynki", value="\n".join(active_clovers_info), inline=False)
    else:
        embed.add_field(name="Aktywne koniczynki", value="Brak", inline=False)
    
    # Mnożniki
    if earnings_multiplier > 1.0 or luck_multiplier > 1.0:
        embed.add_field(name="Aktywne mnożniki", 
                       value=f"Zarobki: ×{earnings_multiplier:.1f}\nSzczęście: ×{luck_multiplier:.1f}", 
                       inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='shop')
async def shop(ctx):
    """Wyświetla sklep z Lucky Blockami"""
    embed = discord.Embed(
        title="🛍️ Sklep KoniBlock",
        description="Kup Lucky Blocki i wygraj nagrody!",
        color=0x9b59b6
    )
    
    for item, price in SHOP_ITEMS.items():
        embed.add_field(name=item, value=f"{price:,} 🍀", inline=True)
    
    embed.set_footer(text="Użyj !buy [nazwa] aby kupić przedmiot")
    await ctx.send(embed=embed)

@bot.command(name='buy')
async def buy(ctx, *, item_name: str):
    """Kupuje przedmiot ze sklepu"""
    user_id = ctx.author.id
    user = get_user_data(user_id)
    
    # Znajdź pasujący przedmiot (case insensitive)
    matching_items = [name for name in SHOP_ITEMS.keys() if item_name.lower() in name.lower()]
    
    if not matching_items:
        await ctx.send("❌ Nie znaleziono takiego przedmiotu w sklepie! Sprawdź !shop")
        return
    
    item = matching_items[0]
    price = SHOP_ITEMS[item]
    
    if user["balance"] < price:
        await ctx.send(f"❌ Nie masz wystarczająco koniczynek! Potrzebujesz {price:,} 🍀, masz {user['balance']:,} 🍀")
        return
    
    # Kup przedmiot
    user["balance"] -= price
    if item in user["inventory"]:
        user["inventory"][item] += 1
    else:
        user["inventory"][item] = 1
    
    save_data()
    
    embed = discord.Embed(
        title="🛍️ Zakup udany!",
        description=f"Kupiłeś **{item}** za **{price:,}** 🍀",
        color=0x00ff00
    )
    embed.add_field(name="Pozostałe koniczynki", value=f"{user['balance']:,} 🍀", inline=True)
    embed.add_field(name="Posiadane", value=f"{user['inventory'][item]}x", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='inventory')
async def inventory(ctx):
    """Pokazuje ekwipunek użytkownika"""
    user_id = ctx.author.id
    user = get_user_data(user_id)
    
    embed = discord.Embed(
        title=f"🎒 Ekwipunek {ctx.author.display_name}",
        color=0x3498db
    )
    
    if not user["inventory"]:
        embed.description = "Twój ekwipunek jest pusty! Odwiedź !shop"
    else:
        for item, quantity in user["inventory"].items():
            embed.add_field(name=item, value=f"Posiadane: {quantity}x", inline=True)
    
    embed.set_footer(text="Użyj !open [nazwa] aby otworzyć Lucky Block")
    await ctx.send(embed=embed)

@bot.command(name='open')
async def open_lucky_block(ctx, *, item_name: str):
    """Otwiera Lucky Block"""
    user_id = ctx.author.id
    user = get_user_data(user_id)
    
    # Znajdź pasujący przedmiot
    matching_items = [name for name in user["inventory"].keys() if item_name.lower() in name.lower()]
    
    if not matching_items:
        await ctx.send("❌ Nie masz takiego Lucky Blocka w ekwipunku! Sprawdź !inventory")
        return
    
    item = matching_items[0]
    
    if user["inventory"][item] <= 0:
        await ctx.send("❌ Nie masz takiego Lucky Blocka w ekwipunku!")
        return
    
    # Użyj Lucky Blocka
    user["inventory"][item] -= 1
    if user["inventory"][item] == 0:
        del user["inventory"][item]
    
    # Pobierz szczęście użytkownika
    _, luck_multiplier = get_active_multipliers(user_id)
    
    # Losuj nagrodę
    rewards = LUCKY_BLOCK_REWARDS[item]
    
    # Tworzymy listę nagród z uwzględnieniem szans (ważona lista)
    weighted_rewards = []
    for reward in rewards:
        name, min_val, max_val, chance = reward
        # Zwiększ szansę na koniczynki dzięki mnożnikowi szczęścia
        actual_chance = chance * luck_multiplier if isinstance(min_val, str) and "clover" in min_val else chance
        weighted_rewards.extend([reward] * int(actual_chance * 10))
    
    # Losujemy nagrodę
    selected_reward = random.choice(weighted_rewards)
    reward_name, min_val, max_val, chance = selected_reward
    
    # Obsługa nagrody
    if isinstance(min_val, str) and "clover" in min_val:
        # Nagroda to koniczynka
        clover_type = min_val
        current_time = time.time()
        expiry_time = current_time + CLOVER_DURATION[clover_type]
        user["active_clovers"][clover_type] = expiry_time
        
        clover_display_name = {
            "clover_4": "☘️ 4-listna koniczynka",
            "clover_5": "🍀 5-listna koniczynka",
            "clover_7": "🌈 7-listna koniczynka", 
            "clover_9": "🌟 9-listna koniczynka"
        }.get(clover_type, clover_type)
        
        duration_minutes = CLOVER_DURATION[clover_type] // 60
        
        result_message = f"🎉 Wygrywasz **{clover_display_name}**!\n"
        result_message += f"Czas trwania: {duration_minutes} minut\n"
        result_message += f"Efekt: ×{CLOVER_MULTIPLIERS[clover_type]['earnings']:.1f} zarobków, ×{CLOVER_MULTIPLIERS[clover_type]['luck']:.1f} szczęścia"
        color = 0x00ff00
        
    else:
        # Nagroda to koniczynki (zarobek/strata)
        amount = random.randint(min_val, max_val)
        user["balance"] += amount
        
        if amount < 0:
            result_message = f"💀 {reward_name}: **{abs(amount):,}** 🍀"
            color = 0xff0000
        else:
            result_message = f"🎉 {reward_name}: **{amount:,}** 🍀"
            color = 0x00ff00
    
    save_data()
    
    embed = discord.Embed(
        title=f"🎁 Otwierasz {item}",
        description=result_message,
        color=color
    )
    
    if luck_multiplier > 1.0 and "clover" in str(min_val):
        embed.add_field(name="Bonus szczęścia", value=f"×{luck_multiplier:.1f}", inline=True)
    
    embed.add_field(name="Nowy balans", value=f"{user['balance']:,} 🍀", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='clovers')
async def clovers_info(ctx):
    """Pokazuje informacje o koniczynkach bonusowych"""
    embed = discord.Embed(
        title="🍀 Koniczynki Bonusowe",
        description="Mnożniki zwiększające twoje zarobki i szczęście!",
        color=0x00ff00
    )
    
    for clover_type, duration in CLOVER_DURATION.items():
        clover_name = {
            "clover_4": "☘️ 4-listna",
            "clover_5": "🍀 5-listna",
            "clover_7": "🌈 7-listna",
            "clover_9": "🌟 9-listna"
        }.get(clover_type, clover_type)
        
        multipliers = CLOVER_MULTIPLIERS[clover_type]
        duration_minutes = duration // 60
        
        embed.add_field(
            name=clover_name,
            value=f"Zarobki: ×{multipliers['earnings']:.1f}\nSzczęście: ×{multipliers['luck']:.1f}\nCzas: {duration_minutes} min",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command(name='give')
async def give(ctx, member: discord.Member, amount: int):
    """Daje koniczynki innemu użytkownikowi"""
    if amount <= 0:
        await ctx.send("❌ Kwota musi być większa niż 0!")
        return
    
    giver_id = ctx.author.id
    receiver_id = member.id
    
    # Nie można dać samemu sobie
    if giver_id == receiver_id:
        await ctx.send("❌ Nie możesz dać koniczynek samemu sobie!")
        return
    
    giver = get_user_data(giver_id)
    receiver = get_user_data(receiver_id)
    
    # Sprawdź czy dający ma wystarczająco koniczynek
    if giver["balance"] < amount:
        await ctx.send(f"❌ Nie masz wystarczająco koniczynek! Masz {giver['balance']} 🍀, chcesz dać {amount} 🍀")
        return
    
    # Wykonaj transfer
    giver["balance"] -= amount
    receiver["balance"] += amount
    
    save_data()
    
    embed = discord.Embed(
        title="🎁 Przekazano koniczynki!",
        description=f"{ctx.author.mention} dał {member.mention} **{amount:,}** koniczynek!",
        color=0x00ff00
    )
    embed.add_field(name="Twój nowy balans", value=f"{giver['balance']:,} 🍀", inline=True)
    embed.add_field(name=f"Balans {member.display_name}", value=f"{receiver['balance']:,} 🍀", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='admin-give')
async def admin_give(ctx, member: discord.Member, amount: int):
    """Admin command: daje koniczynki bez sprawdzania balansu"""
    if not has_admin_role(ctx.author):
        await ctx.send("❌ Nie masz uprawnień do użycia tej komendy!")
        return
    
    if amount <= 0:
        await ctx.send("❌ Kwota musi być większa niż 0!")
        return
    
    receiver_id = member.id
    receiver = get_user_data(receiver_id)
    
    # Dodaj koniczynki
    receiver["balance"] += amount
    
    save_data()
    
    embed = discord.Embed(
        title="⚡ Admin - Przekazano koniczynki!",
        description=f"Administrator {ctx.author.mention} dał {member.mention} **{amount:,}** koniczynek!",
        color=0xff0000
    )
    embed.add_field(name=f"Nowy balans {member.display_name}", value=f"{receiver['balance']:,} 🍀", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='admin-abuse')
async def admin_abuse(ctx):
    """Admin command: daje wszystkim 4x lucka na 30 minut"""
    if not has_admin_role(ctx.author):
        await ctx.send("❌ Nie masz uprawnień do użycia tej komendy!")
        return
    
    # Pobierz wszystkich członków serwera
    guild = ctx.guild
    members = [member for member in guild.members if not member.bot]
    
    current_time = time.time()
    expiry_time = current_time + 1800  # 30 minut
    
    # Daj każdemu 4-listną koniczynkę
    for member in members:
        user = get_user_data(member.id)
        user["active_clovers"]["clover_4"] = expiry_time
    
    save_data()
    
    embed = discord.Embed(
        title="⚡ Admin Abuse Aktywowany!",
        description=f"Administrator {ctx.author.mention} aktywował **4-listną koniczynkę** dla wszystkich użytkowników!",
        color=0xff0000
    )
    embed.add_field(name="Efekt", value="×1.5 zarobków, ×2 szczęścia", inline=True)
    embed.add_field(name="Czas trwania", value="30 minut", inline=True)
    embed.add_field(name="Liczba użytkowników", value=f"{len(members)}", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='help_eco')
async def help_eco(ctx):
    """Pokazuje wszystkie komendy gry ekonomicznej"""
    embed = discord.Embed(
        title="🆘 Pomoc - KoniBlock 🍀",
        description="Komendy gry ekonomicznej",
        color=0x3498db
    )
    
    commands_list = [
        ("!work1", "+1-250 🍀, cooldown 5min"),
        ("!work2", "+251-750 🍀, 30% szansy straty, cooldown 15min"),
        ("!work3", "+500-1000 🍀, 50% szansy straty, cooldown 30min"),
        ("!balance", "Sprawdź swoje koniczynki"),
        ("!shop", "Zobacz sklep z Lucky Blockami"),
        ("!buy [nazwa]", "Kup Lucky Blocka"),
        ("!inventory", "Sprawdź swój ekwipunek"),
        ("!open [nazwa]", "Otwórz Lucky Blocka"),
        ("!clovers", "Informacje o koniczynkach bonusowych"),
        ("!give @użytkownik kwota", "Daj koniczynki innemu graczowi"),
        ("!admin-give @użytkownik kwota", "ADMIN: Daj koniczynki bez limitu"),
        ("!admin-abuse", "ADMIN: Daj wszystkim 4x lucka na 30min")
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    await ctx.send(embed=embed)

# Uruchom bota
if __name__ == "__main__":
    load_data()
    bot.run(os.environ['DISCORD_TOKEN'])
