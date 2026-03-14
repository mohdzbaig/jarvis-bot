import discord
import requests
from gtts import gTTS
import os
from wakeonlan import send_magic_packet

# ===== CONFIG =====
import os
TOKEN = os.getenv("MTQ4MTgwNDIzMjIwMDgxNDYyMg.GehfLX.OwNNL8Dwwv0SoncJGV6YVIUybEjU3ZEYvl-Kjg")
MAC_ADDRESS = "70:08:94:5C:5B:17"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

conversation = []

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

voice_client = None


@client.event
async def on_ready():
    print(f"Jarvis connected as {client.user}")


@client.event
async def on_message(message):
    global voice_client

    if message.author == client.user:
        return

    text = message.content.lower()

    try:

        # ===== JOIN VOICE CHANNEL =====
        if text == "!join":
            if message.author.voice is None:
                await message.channel.send("Join a voice channel first.")
                return

            channel = message.author.voice.channel
            voice_client = await channel.connect()
            await message.channel.send("Jarvis joined the voice channel.")
            return

        # ===== COMPUTER COMMANDS =====

        if "open chrome" in text:
            reply = "Opening Chrome"
            os.system("start https://www.google.com")

        elif "open notepad" in text:
            reply = "Opening Notepad"
            os.system("start notepad")

        elif "shutdown laptop" in text or "shutdown computer" in text:
            reply = "Shutting down the computer"
            os.system("shutdown /s /t 10")

        elif "wake laptop" in text or "turn on laptop" in text:
            reply = "Sending wake signal"
            send_magic_packet(MAC_ADDRESS)

        # ===== AI CHAT =====

        else:

            conversation.append(f"User: {text}")

            prompt = "You are Jarvis, Tony Stark's AI assistant. Always address the user as 'Sir' and speak politely and intelligently. Keep answers concise.\n"
            prompt += "\n".join(conversation[-6:])
            prompt += "\nJarvis:"

            data = {
                "model": "phi3:mini",
                "prompt": prompt,
                "stream": False
            }

            r = requests.post(OLLAMA_URL, json=data)

            result = r.json()

            reply = result.get("response", "Sorry, I couldn't generate a reply.")
            reply = reply.strip().split("\n")[0]

            conversation.append(f"Jarvis: {reply}")

        await message.channel.send(reply)

        # ===== VOICE RESPONSE =====

        tts = gTTS(reply)
        tts.save("jarvis_reply.mp3")

        if voice_client and not voice_client.is_playing():
            voice_client.play(discord.FFmpegPCMAudio("jarvis_reply.mp3"))

    except Exception as e:
        print("Error:", e)


client.run(TOKEN, reconnect=True)
