import discord, json, io

HELP_MESSAGE = """```
!help               - display help message
!fetch USER CHANNEL - fetch user's messages
```"""

class Client(discord.Client):
    def __init__(self, data, datapath, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.datapath = datapath
        self.data = data

    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        # don't track messages sen't by the bot
        if message.author == self.user: return

        # get all data
        channel_id = f'<#{message.channel.id}>'
        author_id = f'<@{message.author.id}>'
        message_id = message.id
        message_content = message.content
        date = message.created_at.strftime("%d/%m/%y %H:%M")
        attachment_count = len(message.attachments)

        # create new entry if data for channel hasn't been stored yet
        if channel_id not in self.data["channels"]:
            self.data["channels"][channel_id] = []

        # save new data
        self.data["channels"][channel_id].append([author_id, message_id, date, message_content, attachment_count])
        with open(self.datapath, "w") as f:
            json.dump(self.data, f, indent = 2)

        # if message is a command, handle the command 
        if message.content.startswith("!"):
            await self.command(message)

    async def command(self, message):
        command = message.content.split()
        if command[0] == "!fetch":
            await self.fetch(command, message)
        elif command[0] == "!help":
            await self.help(message)
        else:
            await message.channel.send(f"Command `{command[0]}` does not exist.")
            
    async def help(self, message):
        await message.channel.send(HELP_MESSAGE)

    async def fetch(self, command, message):
        # not enough arguments were passed into command
        if len(command) < 3:
            await message.channel.send(f"Not enough arguments for `{command[0]}`.")
            return
        user = command[1]
        channel = command[2]

        # if the channel either doesn't exist or doesn't have any messages saved from it yet
        if channel not in self.data["channels"]:
            await message.channel.send(f"Channel `{channel}` either doesn't exist or doesn't have any messages saved yet.")
            return

        # fetch messages
        channel_messages = self.data["channels"][channel]
        data_str = ""
        for msg in channel_messages:
            if msg[0] == user:
                data_str += f'[{msg[3]} files | {msg[1]}] {msg[2]}\n'

        # if there is nothing found
        if data_str == "":
            await message.channel.send(f"No messages found sent by `{user}`")
            return

        byte_io = io.BytesIO(bytes(data_str, 'utf-8'))
        f = discord.File(byte_io, filename = user + channel + ".txt")
        
        await message.channel.send(f"Fetched messages sent in `{channel}` by `{user}`.", file = f)
