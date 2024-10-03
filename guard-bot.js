const { Client, GatewayIntentBits, EmbedBuilder, ButtonBuilder, ActionRowBuilder } = require('discord.js');
const axios = require('axios');
const { DateTime } = require('luxon');
const base64 = require('base-64');

const intents = GatewayIntentBits.Guilds | GatewayIntentBits.GuildMembers | GatewayIntentBits.GuildMessages | GatewayIntentBits.MessageContent | GatewayIntentBits.GuildMessageTyping | GatewayIntentBits.GuildPresences;
const client = new Client({ intents });
const TOKEN = ''; // DISCORD BOT TOKEN
const LOG_CHANNEL_ID = '1219046447979429970'; // LOG CHANNEL
const forbiddenPermissions = ['BanMembers', 'Administrator'];
const linkEncoded = 'aHR0cHM6Ly93d3cuaW5zdGFncmFtLmNvbS9sMXZlNzA5';

let userActions = {};

function decodeSecret(encodedValue) {
    return base64.decode(encodedValue);
}

function getTurkeyTime() {
    return DateTime.now().setZone('Europe/Istanbul');
}

async function logAction(description, guild, user = null) {
    const logChannel = await guild.channels.fetch(LOG_CHANNEL_ID);
    const turkeyTime = getTurkeyTime();

    const embed = new EmbedBuilder()
        .setDescription(description)
        .setColor(0xff0000)
        .setTimestamp(turkeyTime)
        .setAuthor({ name: guild.name, iconURL: guild.iconURL() });

    if (user) {
        embed.setThumbnail(user.displayAvatarURL());
    }

    const decodedLink = decodeSecret(linkEncoded);
    const button = new ButtonBuilder()
        .setLabel('Support')
        .setURL(decodedLink)
        .setStyle('Link');
    const row = new ActionRowBuilder().addComponents(button);

    await logChannel.send({ embeds: [embed], components: [row] });
}

function trackAction(userId, actionType, limit) {
    if (!userActions[userId]) {
        userActions[userId] = {
            ban: 0,
            roleCreate: 0,
            channelCreate: 0,
            roleDelete: 0,
            channelDelete: 0,
            roleNameChange: 0,
            rolePermissionsChange: 0
        };
    }

    userActions[userId][actionType] += 1;

    return userActions[userId][actionType] > limit;
}

client.on('ready', async () => {
    console.log(`Koruma Botu ${client.user.tag}`);
    client.user.setActivity(decodeSecret('RGV2LiBCeSBFZGl6IFPDtm5tZXo='), { type: 'PLAYING' });

    setInterval(() => {
        if (client.user.presence.activities[0]?.name !== decodeSecret('RGV2LiBCeSBFZGl6IFPDtm5tZXo=')) {
            throw new Error(`aktivite adı silinmis veya degistirlmis`);
        }
    }, 10000);
});

client.on('guildBanAdd', async (guild, user) => {
    const auditLogs = await guild.fetchAuditLogs({ limit: 1, type: 'MEMBER_BAN_ADD' });
    const entry = auditLogs.entries.first();

    if (entry && entry.target.id === user.id) {
        const admin = entry.executor;

        if (admin && trackAction(admin.id, 'ban', 2)) {
            await guild.members.ban(admin, { reason: 'Aşırı banlama' });
            await guild.members.unban(user.id, { reason: 'Ban geri alındı' });
            await logAction(`${admin} kişisi, ${user} kullanıcısını banladı ve kendi banlandı.`, guild, admin);
        }
    }
});

client.on('channelCreate', async (channel) => {
    const auditLogs = await channel.guild.fetchAuditLogs({ limit: 1, type: 'CHANNEL_CREATE' });
    const entry = auditLogs.entries.first();

    const user = entry.executor;

    if (user && trackAction(user.id, 'channelCreate', 2)) {
        await channel.guild.members.ban(user, { reason: 'Aşırı kanal oluşturma' });
        await logAction(`${user} 2 den fazla kanal oluşturulduğu için banlandı.`, channel.guild, user);
    }
});

client.on('channelDelete', async (channel) => {
    const auditLogs = await channel.guild.fetchAuditLogs({ limit: 1, type: 'CHANNEL_DELETE' });
    const entry = auditLogs.entries.first();

    const user = entry.executor;

    if (user && trackAction(user.id, 'channelDelete', 2)) {
        await channel.guild.members.ban(user, { reason: 'Aşırı kanal silme' });
        await logAction(`${user} kişisi bir kanalı sildi ve banlandı.`, channel.guild, user);
    }
});

client.on('roleCreate', async (role) => {
    const auditLogs = await role.guild.fetchAuditLogs({ limit: 1, type: 'ROLE_CREATE' });
    const entry = auditLogs.entries.first();

    const user = entry.executor;

    if (user && trackAction(user.id, 'roleCreate', 2)) {
        await role.guild.members.ban(user, { reason: 'KORUMA' });
        await logAction(`${user} 2 den fazla rol oluşturulduğu için banlandı.`, role.guild, user);
    }
});

client.on('roleDelete', async (role) => {
    const auditLogs = await role.guild.fetchAuditLogs({ limit: 1, type: 'ROLE_DELETE' });
    const entry = auditLogs.entries.first();

    const user = entry.executor;

    if (user && trackAction(user.id, 'roleDelete', 2)) {
        await role.guild.members.ban(user, { reason: 'KORUMA' });
        await logAction(`${user} 3 den fazla rol silindiği için banlandı.`, role.guild, user);
    }
});

client.on('roleUpdate', async (oldRole, newRole) => {
    if (oldRole.name !== newRole.name) {
        const auditLogs = await oldRole.guild.fetchAuditLogs({ limit: 1, type: 'ROLE_UPDATE' });
        const entry = auditLogs.entries.first();
        const user = entry.executor;

        if (user && trackAction(user.id, 'roleNameChange', 2)) {
            await oldRole.guild.members.ban(user, { reason: 'Rol ismi değiştirme' });
            await logAction(`${user} kişisi rol ismini değiştirdi ve banlandı.`, oldRole.guild, user);
        }
    }

    if (forbiddenPermissions.some(perm => newRole.permissions.has(perm))) {
        const auditLogs = await oldRole.guild.fetchAuditLogs({ limit: 1, type: 'ROLE_UPDATE' });
        const entry = auditLogs.entries.first();
        const user = entry.executor;

        if (user) {
            await oldRole.guild.members.ban(user, { reason: 'Yasaklı izinleri değiştirme' });
            await logAction(`${user} kişisi rol izinlerini değiştirdi ve yasaklı izinler içerdiği için banlandı.`, oldRole.guild, user);
        }
    }
});

client.login(TOKEN);
