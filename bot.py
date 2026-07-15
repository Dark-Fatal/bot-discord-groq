import discord
from discord import app_commands
from discord.ext import commands
import os
from groq import Groq

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} commande(s) slash synchronisée(s)")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")

@bot.tree.command(name="ask", description="Pose une question à l'IA")
@app_commands.describe(question="Ta question pour l'IA")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()  # évite le timeout si la réponse est longue

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Tu es un assistant utile et amical sur Discord."},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
        await interaction.followup.send(answer)

    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {e}")

bot.run(DISCORD_TOKEN)