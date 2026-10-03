import discord
import os
import tempfile
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

client = discord.Client(intents=discord.Intents.all())
groq = Groq(api_key=GROQ_KEY)

SYSTEM_PROMPT = """
أنت محلل أوامر ديسكورد ذكي. تفهم كل اللهجات العربية: مصرية، خليجية، شامية، مغربية، وفصحى.
ارجع JSON فقط.
الأوامر:
- lock: اقفل الروم، سكر الروم
- unlock: افتح الروم
- rename: غير اسم الروم
- create_text: اعمل روم كتابية
- create_voice: اعمل روم صوتية
- send_image: حط صورة، ابعت صورة
- clear: امسح الشات
حلل: "{USER_TEXT}"
"""

def smart_understand(text: str):
    try:
        prompt = SYSTEM_PROMPT.replace("{USER_TEXT}", text)
        res = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":"ارجع JSON فقط"},{"role":"user","content":prompt}],
            temperature=0.1
        )
        content = res.choices[0].message.content.strip()
        start = content.find('{')
        end = content.rfind('}')+1
        if start!= -1:
            return json.loads(content[start:end])
    except: pass
    t = text.lower()
    if any(x in t for x in ["اقفل","قفل","سكر"]): return {"action":"lock"}
    if "افتح" in t: return {"action":"unlock"}
    if "صورة" in t: return {"action":"send_image"}
    return {"action":"none"}

@client.event
async def on_ready():
    print(f"✅ البوت شغال: {client.user}")

@client.event
async def on_message(message):
    if message.author.bot: return
    text = None
    if message.attachments and message.attachments[0].filename.endswith(('.ogg','.mp3','.wav','.m4a')):
        await message.channel.send("🎧 سمعتك...")
        try:
            att = message.attachments[0]
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
                await att.save(tmp.name)
                tmp_path = tmp.name
            with open(tmp_path, "rb") as f:
                tr = groq.audio.transcriptions.create(file=(tmp_path, f.read()), model="whisper-large-v3-turbo", language="ar", response_format="text")
            os.unlink(tmp_path)
            text = str(tr)
            await message.channel.send(f"قلت: {text}")
        except Exception as e:
            await message.channel.send(f"خطأ: {e}")
            return
    else:
        text = message.content[1:] if message.content.startswith("!") else message.content
    if not text or len(text)<2: return
    cmd = smart_understand(text)
    ch = message.channel
    g = message.guild
    try:
        if cmd["action"]=="lock":
            await ch.set_permissions(g.default_role, send_messages=False)
            if not ch.name.startswith("🔒-"): await ch.edit(name=f"🔒-{ch.name}")
            await ch.send(f"🔒 قفلت #{ch.name}")
        elif cmd["action"]=="unlock":
            await ch.set_permissions(g.default_role, send_messages=True)
            await ch.edit(name=ch.name.replace("🔒-","").replace("🔒",""))
            await ch.send(f"🔓 فتحت #{ch.name}")
        elif cmd["action"]=="send_image":
            if os.path.exists("image.jpg"): await ch.send(file=discord.File("image.jpg"))
            else: await ch.send("مش لاقي image.jpg")
    except Exception as e:
        await ch.send(f"خطأ: {e}")

client.run(TOKEN)
