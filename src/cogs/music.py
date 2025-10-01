import discord
from discord.ext import commands
import yt_dlp
import asyncio

# YDL options for yt-dlp
YDL_OPTIONS = {'format': 'ba', 'noplaylist':'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.current_song = {}

    @commands.command()
    async def join(self, ctx):
        """Makes the bot join the voice channel of the user."""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")

    @commands.command()
    async def leave(self, ctx):
        """Makes the bot leave the voice channel."""
        if ctx.voice_client:
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.send("I am not in a voice channel.")

    @commands.command()
    async def play(self, ctx, *, search):
        """Plays a song from YouTube."""
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            except Exception:
                await ctx.send("Could not find the song.")
                return

        url = info['url']
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        
        guild_id = ctx.guild.id

        if guild_id not in self.song_queue:
            self.song_queue[guild_id] = []

        self.song_queue[guild_id].append({'source': source, 'title': info['title']})

        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            await self.play_next(ctx)
        else:
            await ctx.send(f"Added to queue: **{info['title']}**")

    async def play_next(self, ctx):
        guild_id = ctx.guild.id
        if self.song_queue[guild_id]:
            song = self.song_queue[guild_id].pop(0)
            self.current_song[guild_id] = song
            ctx.voice_client.play(song['source'], after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            await ctx.send(f"Now playing: **{song['title']}**")
        else:
            self.current_song.pop(guild_id, None)

    @commands.command()
    async def pause(self, ctx):
        """Pauses the current song."""
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused the song.")

    @commands.command()
    async def resume(self, ctx):
        """Resumes the paused song."""
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed the song.")

    @commands.command()
    async def skip(self, ctx):
        """Skips the current song."""
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.stop()
            await ctx.send("Skipped the current song.")

    @commands.command()
    async def queue(self, ctx):
        """Displays the song queue."""
        guild_id = ctx.guild.id
        if guild_id in self.song_queue and self.song_queue[guild_id]:
            queue_list = ""
            for i, song in enumerate(self.song_queue[guild_id]):
                queue_list += f"{i+1}. {song['title']}\n"
            
            embed = discord.Embed(title="Song Queue", description=queue_list, color=discord.Color.blue())
            await ctx.send(embed=embed)
        else:
            await ctx.send("The queue is empty.")

    @commands.command()
    async def nowplaying(self, ctx):
        """Displays the currently playing song."""
        guild_id = ctx.guild.id
        if guild_id in self.current_song:
            await ctx.send(f"Currently playing: **{self.current_song[guild_id]['title']}**")
        else:
            await ctx.send("No song is currently playing.")

# This function is required for the cog to be loaded
async def setup(bot):
    await bot.add_cog(Music(bot))
