import discord
from discord.ext import commands, tasks
import requests
import config

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

allowed_role_id = #the role to allow stopping the crafty server or restart
ALLOWED_MESSAGE_IDS = {0 ,0} #when bot gets turned on, it will delete every message in the channel except the ones set here

persistent_message = None
last_stats = "Stats not available"
update_counter = 0


def fetch_server_stats():
    stats_url = f"{config.CRAFTY_API_URL}/{config.MINECRAFT_SERVER_ID}/stats"
    headers = {
        "Authorization": f"Bearer {config.CRAFTY_API_KEY}",
        "User-Agent": "DiscordBot (https://ronanapis.us, v1.0)"
    }
    try:
        stats_response = requests.get(stats_url, headers=headers, verify=False)
        if stats_response.status_code == 200:
            data = stats_response.json().get("data", {})
            stats_summary = (
                f"**Server Stats:**\n"
                f"CPU Usage: {data.get('cpu', 'unknown')}%\n"
                f"RAM Usage: {data.get('mem', 'unknown')}\n"
                f"Memory Percent: {data.get('mem_percent', 'unknown')}%\n"
                f"Players Online: {data.get('online', 'unknown')} / {data.get('max', 'unknown')}\n"
                f"Version: {data.get('version', 'unknown')}\n"
                f"updating: {data.get('updating', 'unknown')}\n"
                f"crashed: {data.get('crashed', 'unknown')}\n"
                f"started: {data.get('started', 'unknown')}\n"
                f"downloading: {data.get('downloading', 'unknown')}\n"
                f"World size: {data.get('world_size', 'unknown')}\n"
                f"players: {data.get('players', 'unknown')}\n"
            )
            # Use the players array provided in the stats response.
            players = data.get("players", [])
            if players and isinstance(players, list):
                stats_summary += "**Online Players:**\n"
                for player in players:
                   
            else:
                stats_summary += "\n"
            return stats_summary
        else:
            return f"Failed to fetch stats. Status: {stats_response.status_code}"
    except Exception as e:
        return f"Error fetching stats: {str(e)}"

class ServerControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Start Server", style=discord.ButtonStyle.success, custom_id="start_server_button")
    async def start_server_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global persistent_message, last_stats, update_counter
        await interaction.response.defer(ephemeral=True)
        action_url = f"{config.CRAFTY_API_URL}/{config.MINECRAFT_SERVER_ID}/action/start_server"
        headers = {
            "Authorization": f"Bearer {config.CRAFTY_API_KEY}",
            "User-Agent": "DiscordBot (https://ronanapis.us, v1.0)"
        }
        try:
            response = requests.post(action_url, headers=headers, verify=False)
            if response.status_code == 200:
                message = "Minecraft server is starting!\n"
            else:
                message = f"Failed to start server.\nStatus: {response.status_code}\nDetails: {response.text}\n"
        except Exception as e:
            message = f"An error occurred when starting the server: {str(e)}\n"
        last_stats = fetch_server_stats()
        update_counter = 0
        final_message = message + "\n" + last_stats + "\nUpdated just now."
        if persistent_message:
            try:
                await persistent_message.edit(content=final_message, view=self)
            except Exception as e:
                print("Error editing persistent message:", e)
        else:
            new_msg = await interaction.channel.send(final_message, view=self)
            persistent_message = new_msg
        await interaction.followup.send("Action processed. Check the updated server stats below.", ephemeral=True)

    @discord.ui.button(label="Stop Server", style=discord.ButtonStyle.danger, custom_id="stop_server_button")
    async def stop_server_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if allowed_role_id not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("You don't have permission to stop the server.", ephemeral=True)
            return
        global persistent_message, last_stats, update_counter
        await interaction.response.defer(ephemeral=True)
        action_url = f"{config.CRAFTY_API_URL}/{config.MINECRAFT_SERVER_ID}/action/stop_server"
        headers = {
            "Authorization": f"Bearer {config.CRAFTY_API_KEY}",
            "User-Agent": "DiscordBot (https://ronanapis.us, v1.0)"
        }
        try:
            response = requests.post(action_url, headers=headers, verify=False)
            if response.status_code == 200:
                message = "Minecraft server is stopping!\n"
            else:
                message = f"Failed to stop server.\nStatus: {response.status_code}\nDetails: {response.text}\n"
        except Exception as e:
            message = f"An error occurred when stopping the server: {str(e)}\n"
        last_stats = fetch_server_stats()
        update_counter = 0
        final_message = message + "\n" + last_stats + "\nUpdated just now."
        try:
            await persistent_message.edit(content=final_message, view=self)
        except Exception as e:
            print("Error editing persistent message:", e)
        await interaction.followup.send("Stop action processed.", ephemeral=True)

    @discord.ui.button(label="Restart Server", style=discord.ButtonStyle.primary, custom_id="restart_server_button")
    async def restart_server_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if allowed_role_id not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("You don't have permission to restart the server.", ephemeral=True)
            return
        global persistent_message, last_stats, update_counter
        await interaction.response.defer(ephemeral=True)
        action_url = f"{config.CRAFTY_API_URL}/{config.MINECRAFT_SERVER_ID}/action/restart_server"
        headers = {
            "Authorization": f"Bearer {config.CRAFTY_API_KEY}",
            "User-Agent": "DiscordBot (https://ronanapis.us, v1.0)"
        }
        try:
            response = requests.post(action_url, headers=headers, verify=False)
            if response.status_code == 200:
                message = "Minecraft server is restarting!\n"
            else:
                message = f"Failed to restart server.\nStatus: {response.status_code}\nDetails: {response.text}\n"
        except Exception as e:
            message = f"An error occurred when restarting the server: {str(e)}\n"
        last_stats = fetch_server_stats()
        update_counter = 0
        final_message = message + "\n" + last_stats + "\nUpdated just now."
        try:
            await persistent_message.edit(content=final_message, view=self)
        except Exception as e:
            print("Error editing persistent message:", e)
        await interaction.followup.send("Restart action processed.", ephemeral=True)

@tasks.loop(seconds=5)
async def update_message():
    global persistent_message, update_counter, last_stats
    if persistent_message:
        update_counter += 5
        if update_counter >= 10:
            last_stats = fetch_server_stats()
            update_counter = 0
        updated_text = "Updated just now." if update_counter == 0 else f"Updated {update_counter} sec(s) ago."
        new_content = (
            "Press the green button below to start the Minecraft server.\n\n"
            f"{last_stats}\n"
            f"{updated_text}"
        )
        try:
            await persistent_message.edit(content=new_content)
        except Exception as e:
            print("Error updating persistent message:", e)

@bot.command(name="listusers")
async def list_users(ctx):
    """List players currently online based on the stats API players array."""
    stats_info = fetch_server_stats()
    await ctx.send(stats_info)

@bot.event
async def on_ready():
    global persistent_message, last_stats, update_counter
    print(f"Logged in as {bot.user}")
    target_channel = None
    for channel in bot.get_all_channels():
        if channel.name == "serverconfigbot": #change the channel name to your liking
            target_channel = channel
            break
    if target_channel:
        last_stats = fetch_server_stats()
        update_counter = 0
        initial_content = (
            "Press the green button below to start the Minecraft server.\n\n"
            f"{last_stats}\n"
            "Updated just now."
        )
        persistent_message = await target_channel.send(initial_content, view=ServerControlView())
        # Purge every message in the channel except allowed ones and the persistent control message.
        def check(message):
            return message.id not in ALLOWED_MESSAGE_IDS and message.id != persistent_message.id
        deleted = await target_channel.purge(check=check)
        print(f"Deleted {len(deleted)} message(s) from {target_channel.name}")
        update_message.start()
    else:
        print("Channel 'serverconfigbot' not found in any guilds.")

bot.run(config.DISCORD_TOKEN)
