import os
import json
import time
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Load series configuration
with open("series.json", "r", encoding="utf-8") as f:
    series = json.load(f)

cooldowns = {}
COOLDOWN = 10

# DarkloidsOnly spam trap
DARKLOID_CHANNEL_ID = 1523940096942936208

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # DarkloidsOnly spam trap
    if message.channel.id == DARKLOID_CHANNEL_ID:

        # Don't ban administrators or the server owner
        if (
            message.author.guild_permissions.administrator
            or message.author == message.guild.owner
        ):
            return

        await message.guild.ban(
            message.author,
            reason="Posted in DarkloidsOnly spam trap.",
            delete_message_seconds=604800
        )

        return

    content = message.content.strip().upper()

    if content.startswith("#"):

        user_id = message.author.id
        current_time = time.time()

        # Cooldown
        if user_id in cooldowns:
            time_left = COOLDOWN - (current_time - cooldowns[user_id])

            if time_left > 0:
                await message.channel.send(
                    f"⏳ Please wait **{int(time_left)+1}** more second(s) before requesting another BattleChip.",
                    delete_after=15
                )
                return

        cooldowns[user_id] = current_time

        chip_id = content[1:]

        if len(chip_id) < 2:
            return

        prefix = chip_id[0]

        if prefix not in series:
            await message.channel.send(
                f"❌ Unknown BattleChip series '{prefix}'.",
                delete_after=15
            )
            return

        database_file = series[prefix]["database"]
        with open(database_file, "r", encoding="utf-8") as f:
            chips = json.load(f)

        if chip_id not in chips:
            await message.channel.send(
                f"❌ BattleChip **{chip_id}** was not found.",
                delete_after=15
            )
            return

        chip = chips[chip_id]

        embed = discord.Embed(
            title=f"{series[prefix]['name']} {chip['number']} - {chip['name']}",
            description=chip["description"],
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Power",
            value=chip["power"],
            inline=True
        )

        embed.add_field(
            name="Element",
            value=chip["element"],
            inline=True
        )

        embed.add_field(
            name="Class",
            value=chip["class"],
            inline=True
        )

        embed.add_field(
            name="Games",
            value=chip["game"],
            inline=False
        )

        embed.add_field(
            name="Compatible PETs",
            value=chip["toy"],
            inline=False
        )

        # Use the chip image if it exists, otherwise use the placeholder image
        image_path = chip["image"]

        if not os.path.exists(image_path):
            image_path = "images/missing.png"

        file = discord.File(image_path, filename="chip.png")
        embed.set_image(url="attachment://chip.png")

        await message.channel.send(embed=embed, file=file)

    await bot.process_commands(message)

bot.run(TOKEN)