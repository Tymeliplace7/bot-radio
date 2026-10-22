import asyncio
import os
import discord
from discord.ext import commands, tasks
from flask import Flask
import threading

# --- 1. SERVIDOR FLASK EN HILO INDEPENDIENTE ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Radio Online 24/7"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    # Desactivamos el reloader para evitar duplicar procesos
    app.run(host='0.0.0.0', port=port, use_reloader=False)

# Arrancar Flask
threading.Thread(target=run_flask, daemon=True).start()

# --- 2. CONFIGURACIÓN DEL BOT ---
ESTACION_DEFAULT = 'exa'

RADIOS = {
    'exa': 'https://stream.zeno.fm/f3wvbbqmdg8uv',
    'rock': 'https://stream.zeno.fm/cdey4pbw2ehvv',
    'romantica': 'https://stream.zeno.fm/edzcac2suy8uv',
    'classic_rock': 'https://stream.radioparadise.com/rock-128',
    'mellow_mix': 'https://stream.radioparadise.com/mellow-128',
    'main_mix': 'https://stream.radioparadise.com/mp3-128',
    'world_etc': 'https://stream.radioparadise.com/world-128',
    'groove_salad': 'https://ice1.somafm.com/groovesalad-128-mp3',
    'indie_pop': 'https://ice1.somafm.com/indiepop-128-mp3',
    'smooth_jazz': 'https://ice1.somafm.com/secretagent-128-mp3',
}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

FFMPEG_BEFORE_OPTIONS = (
    '-reconnect 1 '
    '-reconnect_streamed 1 '
    '-reconnect_delay_max 5 '
    '-headers "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\r\n"'
)

canal_activo_id = None
estacion_actual = ESTACION_DEFAULT

async def reproducir_stream(cliente_voz, estacion_nombre):
    global estacion_actual
    if estacion_nombre not in RADIOS:
        return False

    if cliente_voz.is_playing():
        cliente_voz.stop()

    url = RADIOS[estacion_nombre]
    fuente_raw = discord.FFmpegPCMAudio(url, before_options=FFMPEG_BEFORE_OPTIONS, options='-vn -loglevel quiet')
    fuente_audio = discord.PCMVolumeTransformer(fuente_raw, volume=1.0)
    cliente_voz.play(fuente_audio)
    estacion_actual = estacion_nombre
    return True

@bot.event
async def on_ready():
    print(f'✅ Bot listo y operando 24/7 como: {bot.user.name}')
    if not guardian_247.is_running():
        guardian_247.start()

@tasks.loop(seconds=15)
async def guardian_247():
    global canal_activo_id
    if not canal_activo_id:
        return

    canal = bot.get_channel(canal_activo_id)
    if not canal:
        return

    try:
        if not bot.voice_clients:
            cliente_voz = await canal.connect(reconnect=True, timeout=20.0)
            await reproducir_stream(cliente_voz, estacion_actual)
            print(f'Guardián: Conexión recuperada en {canal.name}')
            return

        cliente_voz = bot.voice_clients[0]

        if not cliente_voz.is_playing():
            await reproducir_stream(cliente_voz, estacion_actual)
            print(f'Guardián: Transmisión reiniciada en {canal.name}')

    except Exception as e:
        print(f'Error en guardián 24/7: {e}')

@bot.command(name='poner')
async def poner_radio(ctx, *, estacion: str):
    global canal_activo_id
    estacion = estacion.lower().strip()

    if estacion not in RADIOS:
        await ctx.send(f'❌ La emisora `{estacion}` no existe. Usa `!radios`.')
        return

    if not ctx.author.voice:
        await ctx.send('❌ Debes entrar primero a un canal de voz para llamarme.')
        return

    canal_usuario = ctx.author.voice.channel

    try:
        if ctx.voice_client is None:
            cliente_voz = await canal_usuario.connect(reconnect=True, timeout=20.0)
        else:
            cliente_voz = ctx.voice_client
            if cliente_voz.channel != canal_usuario:
                await cliente_voz.move_to(canal_usuario)

        canal_activo_id = canal_usuario.id

        await reproducir_stream(cliente_voz, estacion)
        await ctx.send(f'📻 Sintonizando **{estacion.upper()}** 24/7 en **{canal_usuario.name}**')

    except Exception as e:
        print(f'Error en poner: {e}')
        await ctx.send(f'❌ Error al conectar: `{e}`')

@bot.command(name='apagar')
async def apagar_radio(ctx):
    global canal_activo_id
    canal_activo_id = None

    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.voice_client.disconnect()
        await ctx.send('🔇 Radio apagada.')

@bot.command(name='radios')
async def listar_radios(ctx):
    lista = '\n'.join([f'• **{nombre}**' for nombre in RADIOS.keys()])
    await ctx.send(f'📻 **Emisoras estables disponibles:**\n{lista}\n\nUsa `!poner <nombre>` para cambiar.')

# --- 3. INICIO EN EL HILO PRINCIPAL ---
token = os.environ.get('DISCORD_TOKEN')

if token:
    print('Conectando bot a Discord...')
    bot.run(token)
else:
    print('❌ ERROR: Variable DISCORD_TOKEN no encontrada.')
