import discord 
from discord.app_commands.translator import CommandNameTranslationContext
from discord.ext import commands
import requests
from yt_dlp.extractor.extractors import NOSNLArticleIE
import asyncio
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("token")
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

# @bot.command()
#
# async def test(ctx, *args):
#     respuesta = ' '.join(args) # Primera prueba del bot
#     await ctx.send(respuesta)
#




@bot.command()
async def abrazo(ctx, arg=None):
    usuario1 = ctx.author
    usuario2 =  arg
    if arg is None:
        print(f"{usuario1} se ha dado un auto-abrazo")
        await ctx.send(f"{usuario1} se ha dado un auto-abrazo")
        return

    respuesta = f"{usuario2}, {usuario1.mention} te envia un abrazo virtual"
    print(f"{usuario1.name} le ha enviado un abrazo a {usuario2}")
    await ctx.send(respuesta)    
    # await ctx.message.delete() # Linea de codigo por si quiero que el mensaje que envie el usuario se elimine
    

@bot.command()
async def delete(ctx):
    print(f"{ctx.author} ha solicitado borrar los mensajes del canal, {ctx.channel.name}")
    await ctx.channel.purge()
    await ctx.send("Se han eliminado todos los mensajes", delete_after=3)




@bot.command()
async def info(ctx, arg= None):
    if arg is None: 
        member = ctx.author if isinstance(ctx.author, discord.Member) else ctx.guild.get_member(ctx.author.id)
    else:
        converter = commands.MemberConverter()
        # Intento convertir el arg en un miembro usando MemberConvert()
        try:
            member = await converter.convert(ctx, arg)
        except commands.BadArgument:
            member = None

            # A continuacion pongo un codigo por si la conversion no funciona, pues usamos el nombre directamente
        if member is None:
            member = discord.utils.get(ctx.guild.members, name=arg)

        # Y ya si no encuentra por el nombre, pues buscamos por el ID
        if member is None:
            try:
                user_id = int(arg)
                member = ctx.guild.get_member(user_id)
            except ValueError:
                pass

        if member is None:
            await ctx.send("No hay ningun usuario llamado asi")
            print(f"{ctx.author} ha solicitado la informacion de un usuario que no existe {arg}")
            return

    ficha = discord.Embed(title=f"Informacion de {member}", color=discord.Color.magenta())
    ficha.set_thumbnail(url=member.display_avatar.url)
    ficha.add_field(name="Nombre", value=member.name, inline=False)
    ficha.add_field(name="Apodo", value=member.nick or "No tiene", inline=False)
    ficha.add_field(name="ID", value=member.id, inline=False)
    ficha.add_field(name="Estado", value=member.status, inline=False)
    fecha_ingreso = member.joined_at.strftime("%d-%m-%Y") if member.joined_at else "No disponible"
    ficha.add_field(name="Fecha de ingreso", value=fecha_ingreso, inline=False)
    await ctx.message.delete() # Elimino el mensaje que ha pasado el usuario 
    print(f"{ctx.author} ha solicitado la informacion del usuario {member.name}")
    await ctx.send(embed=ficha)



@bot.command()
async def server(ctx):
    nombre_server = ctx.guild.name
    numero_miembros = ctx.guild.member_count
    admin = ctx.guild.owner
    if admin is None:
        try:
            admin = await ctx.guild.fetch_member(ctx.guild.owner_id)
        except discord.NotFound:
            admin = "No disponible"

    ficha = discord.Embed(title=f"Informacion de {nombre_server}", description="Esto es una prueba", color=discord.Color.yellow())
    
    if ctx.guild.icon is not None:
        icono = ctx.guild.icon.url
    else:
        icono = None

    if icono:
        ficha.set_image(url=icono)
    ficha.add_field(name="Admin", value=admin, inline=False)
    ficha.add_field(name="Numero de miembros", value=numero_miembros, inline=False)

    await ctx.send(embed=ficha)
    print(f"{ctx.author} ha solicitado la informacion del servidor")


@bot.command()
async def avatar(ctx, arg=None):
    if arg is None: 
        member = ctx.author if isinstance(ctx.author, discord.Member) else ctx.guild.get_member(ctx.author.id)
    else:
        converter = commands.MemberConverter()
        # Intento convertir el arg en un miembro usando MemberConvert()
        try:
            member = await converter.convert(ctx, arg)
        except commands.BadArgument:
            member = None

            # A continuacion pongo un codigo por si la mencion no funciona, pues usamos el nombre directament
        if member is None:
            member = discord.utils.get(ctx.guild.members, name=arg)

        # Y ya si no encuentra por el nombre, pues buscamos por el ID
        if member is None:
            try:
                user_id = int(arg)
                member = ctx.guild.get_member(user_id)
            except ValueError:
                pass

        if member is None:
            await ctx.send("No hay ningun usuario llamado asi")
            print(f"{ctx.author} ha solicitado el avatar de alguien que no existe {arg}")
            return

    ficha = discord.Embed(title=f"Avatar {member}")
    ficha.set_image(url=member.avatar)
    await ctx.send(embed=ficha)
    print(f"{ctx.author} ha solicitado el avatar de {member.name}")


@bot.command()

async def aviso(ctx, *args):
    respuesta = ' '.join(args)
    ficha = discord.Embed(title="AVISO", color=discord.Color.yellow())
    ficha.add_field(name="", value=respuesta, inline=False)
    await ctx.send(embed=ficha)
    print(f"{ctx.author} ha enviado el siguiente aviso: {respuesta}")

# Comandos para la musica 

listaC = []
ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 7','options': '-vn -filter:a "volume=0.25"'}
ydl_options = {'format': 'bestaudio/best'}
ytdl = yt_dlp.YoutubeDL(ydl_options)

clientes = {} # Controlamos que el bot se pueda usar en diferentes chat de voz

@bot.command()
async def play(ctx, *arg:str):
    # voz = ctx.voice_client
    # if not voz:
    #     if ctx.author.voice():
    #         canal = ctx.author.voice.
    try:
        cliente = await ctx.author.voice.channel.connect()
        clientes[cliente.guild.id] = cliente
    except Exception as e:
        print(e)

    try:
        url = ' '.join(arg)
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        cancion = data['url']
        player = discord.FFmpegOpusAudio(cancion, **ffmpeg_options)
        clientes[ctx.guild.id].play(player)

    except Exception as e:
        print(e)




@bot.command()
async def pausa(ctx):
    voz = ctx.voice_client
    if not voz or not voz.is_connected():
        await ctx.send(f"{ctx.author},  tienes que estar en canal de voz para usar este comando, tontito")
        return 
    
    if voz.is_playing():
        voz.pause()
        await ctx.send("Musica pausada")
        print(f"{ctx.author} ha pausado la musica")
    else:
        await ctx.send("No hay nada reproduciendose", delete_after=3)




@bot.command()
async def seguir(ctx):
    voz = ctx.voice_client
    if not voz or not voz.is_connected():
        await ctx.send(f"{ctx.author}, tienes que estar en un canal de voz para usar este comando, tontito")
        return

    if voz.is_paused():
        voz.resume()
        await ctx.send("Reproduciendose musica")

    else:
        await ctx.send("La musica ya se esta reproduciendose", delete_after=3)
    print(f"{ctx.author} ha reanudado la musica")


@bot.command()
async def stop(ctx):
    voz = ctx.voice_client
    if not voz or not voz.is_connected():
        await ctx.send("Tienes que estar en un canal de voz para usar este comando")
        return
    
    #voz.stop()
    voz.disconnect()
    await ctx.send("Fuera musica", delete_after=1)
    print(f"{ctx.author} ha sacado a Puchi, y no hay mas musica")



@bot.command()
async def next(ctx):
    voz = ctx.voice_client
    if not voz or not voz.is_connected():
        await ctx.send(f"{ctx.author}, tienes que estar en un canal de voz para poder usar este comando tontito")
        return
    if voz.is_paused() or voz.is_playing():
        voz.stop()
        print(f"{ctx.author} ha saltado a la siguiente cancion") 
    else:
        await ctx.send("No hay ninguna reproduciendose ahora")



@bot.command()
async def lista(ctx):
    if lista:
        ficha = discord.Embed(title="Las siguientes 10 canciones", color=discord.Color.green())
        for lugar, cancion in enumerate(listaC, start=1):
            if lugar is not 11:
                ficha.add_field(name="", value=f"{lugar}. {cancion}", inline=False)
            else: 
                return
        
        await ctx.send(embed=ficha)
    else:
        await ctx.send("No hay mas canciones en la lista")
    
    print(f"{ctx.author} ha solicitado todas las canciones de la lista")
  

@bot.command()
async def listaAll(ctx):
    if lista:
        ficha = discord.Embed(title="Lista de canciones", color=discord.Color.green())
        for lugar, cancion in enumerate(listaC, start=1):
            ficha.add_field(name="", value=f"{lugar}. {cancion}", inline=False)
        await ctx.send(embed=ficha)
    else:
        await ctx.send("No hay canciones en la lista")
    
    print(f"{ctx.author} ha solicitado todas las canciones de la lista")




@bot.event
async def on_ready():
    print(f"{bot.user} se acaba de despertar")


bot.run(token)



