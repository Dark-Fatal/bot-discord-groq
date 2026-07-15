import discord
from discord.ext import commands
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

conversations = {}

def get_history(user_id):
    if user_id not in conversations:
        conversations[user_id] = [
            {"role": "system", "content": "Tu es un assistant utile et amical sur Discord. Réponds de manière concise."}
        ]
    return conversations[user_id]

async def generate_response(user_id, message_content):
    history = get_history(user_id)
    history.append({"role": "user", "content": message_content})

    if len(history) > 21:
        history = [history[0]] + history[-20:]
        conversations[user_id] = history

    completion = client.chat.completions.create(
        model=MODEL,
        messages=history,
        temperature=0.7,
        max_tokens=1024,
    )

    reply = completion.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

@bot.command(name="ask")
async def ask(ctx, *, question: str):
    async with ctx.typing():
        try:
            reply = await generate_response(ctx.author.id, question)
            for i in range(0, len(reply), 2000):
                await ctx.send(reply[i:i+2000])
        except Exception as e:
            await ctx.send(f"⚠️ Erreur : {e}")

@bot.command(name="reset")
async def reset(ctx):
    conversations.pop(ctx.author.id, None)
    await ctx.send("🔄 Conversation réinitialisée !")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        question = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if question:
            async with message.channel.typing():
                try:
                    reply = await generate_response(message.author.id, question)
                    for i in range(0, len(reply), 2000):
                        await message.channel.send(reply[i:i+2000])
                except Exception as e:
                    await message.channel.send(f"⚠️ Erreur : {e}")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)