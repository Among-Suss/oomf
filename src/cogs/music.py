import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

# YDL options for yt-dlp
YDL_OPTIONS = {'format': 'ba/b', 'noplaylist':'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.current_song = {}

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.send("I am not in a voice channel.")

    @commands.hybrid_command(name="play", description="Search YouTube or play a URL.", aliases=['p'])
    @app_commands.describe(search="The name or URL of the song to play.")
    async def play(self, ctx, *, search):        
        if not ctx.author.voice:
            await ctx.send("You are not connected to a voice channel.", ephemeral=True)
            return
        elif not ctx.voice_client:
            await ctx.invoke(self.join)
        elif ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.send(f"I am already in the voice channel: **{ctx.voice_client.channel.name}**.")
            return
        
        # Defer the response for slash commands to avoid "interaction failed" errors
        if ctx.interaction:
            await ctx.defer()

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                if search.startswith("https://"):
                    query = search
                    info = ydl.extract_info(query, download=False)
                else:
                    query = f"ytsearch:{search}"
                    info = ydl.extract_info(query, download=False)['entries'][0]
            except Exception as e:
                print(e)
                await ctx.send("Error getting video info from yt-dlp.")
                return
        
        guild_id = ctx.guild.id
        if guild_id not in self.song_queue:
            self.song_queue[guild_id] = []

        self.song_queue[guild_id].append({'url': info['url'], 'title': info['title']})

        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            await self.play_next(ctx)
        else:
            await ctx.send(f"Added to queue: **{info['title']}**")

    async def play_next(self, ctx):
        guild_id = ctx.guild.id
        if self.song_queue[guild_id]:
            song = self.song_queue[guild_id].pop(0)
            self.current_song[guild_id] = song
            source = await discord.FFmpegOpusAudio.from_probe(song['url'], **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            await ctx.send(f"Now playing: **{song['title']}**")
        else:
            self.current_song.pop(guild_id, None)

    # broken - corrupts the playback
    # @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused the song.")

    # broken - corrupts the playback
    # @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed the song.")

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.stop()
            await ctx.send("Skipped the current song.")

    @commands.command()
    async def queue(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.song_queue and self.song_queue[guild_id]:
            queue_list = ""
            for i, song in enumerate(self.song_queue[guild_id]):
                queue_list += f"{i+1}. {song['title']}\n"
            
            embed = discord.Embed(title="Song Queue", description=queue_list, color=discord.Color.blue())
            await ctx.send(embed=embed)
        else:
            await ctx.send("The queue is empty.")

    @commands.hybrid_command(name="nowplaying", description="Show current song.", aliases=['np'])
    async def nowplaying(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.current_song:
            await ctx.send(f"Currently playing: **{self.current_song[guild_id]['title']}**")
        else:
            await ctx.send("No song is currently playing.")

# This function is required for the cog to be loaded
async def setup(bot):
    await bot.add_cog(Music(bot))
