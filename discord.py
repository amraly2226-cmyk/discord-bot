import os, discord, httpx
from dotenv import load_dotenv
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
client = discord.Client(intents=intents)
async def ask_groq(prompt):
    async with httpx.AsyncClient() as http:
        r = await http.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama-3.1-8b-instant","messages": [{"role": "user", "content": prompt}],"max_tokens": 500},
            timeout=30
        )
        return r.json()["choices"][0]["message"]["content"]
@client.event
async def on_ready():
    print(f"BOT ONLINE: {client.user}")
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    c = message.content.strip()
    if "اقفل الروم" in c:
        if message.channel.permissions_for(message.guild.me).manage_channels:
            await message.channel.edit(archived=True, locked=True)
            await message.channel.send("الروم اتقفل")
        else:
            await message.channel.send("معنديش صلاحية")
        return
    if client.user.mentioned_in(message) or c.startswith("!اسال"):
        q = c.replace(f"<@{client.user.id}>", "").replace("!اسال", "").strip()
        if not q:
            await message.reply("اسألني اي حاجة!")
            return
        async with message.channel.typing():
            try:
                a = await ask_groq(q)
                await message.reply(a[:2000])
            except Exception as e:
                await message.reply(f"ايرور: {e}")
client.run(DISCORD_TOKEN)
