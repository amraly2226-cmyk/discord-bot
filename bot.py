import discord, os, requests
from dotenv import load_dotenv

load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY")
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def ask_groq(question):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "انت مساعد ذكي بتتكلم عامية مصرية بسيطة وخفيفة."},
            {"role": "user", "content": question}
        ]
    }
    r = requests.post(url, headers=headers, json=data, timeout=30)
    j = r.json()
    if "choices" not in j:
        return f"ايرور من Groq: {j}"
    return j["choices"][0]["message"]["content"]

@client.event
async def on_ready():
    print(f'BOT ONLINE: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    content = message.content
    if not (content.startswith('!اسال') or client.user.mentioned_in(message)):
        return

    q = content.replace('!اسال','',1).strip()
    q = q.replace(f'<@{client.user.id}>','').replace(f'<@!{client.user.id}>','').strip()
    if not q:
        q = "ازيك"

    async with message.channel.typing():
        try:
            ans = ask_groq(q)
            await message.reply(ans[:1900])
        except Exception as e:
            print(f"ERROR: {e}")
            await message.reply(f"حصل ايرور: {e}")

client.run(TOKEN)
