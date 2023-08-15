import discord, json, io

HELP_MESSAGE = """```
!help               - display help message
!purge PURGE_LIMIT  - delete X messages
!fetch USER CHANNEL - fetch user's messages
```"""

class Client(discord.Client):
    def __init__(self, data, datapath, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.datapath = datapath
        self.data = data

    async def on_ready(self):
        print(f'Logged on as {self.user}')

    def save_data(self):
        with open(self.datapath, "w") as f:
            json.dump(self.data, f, indent = 2)

    def superuser_check(self, author):
        return author.id == self.data["superuser"]

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
        self.data["channels"][channel_id].append({
            "author": author_id,
            "msg_id": message_id,
            "date": date,
            "content": message_content,
            "attachments": attachment_count,
            "edits": []
        })
        self.save_data()

        # if message is a command, handle the command 
        if message.content.startswith("!"):
            await self.run_command(message)

    async def on_message_edit(self, before, after):
        channel_id = f'<#{before.channel.id}>'
        message_id = before.id
        edited_msg_content = after.content
        channel_messages = self.data["channels"][channel_id]
        for idx in range(len(channel_messages)):
            if channel_messages[idx]["msg_id"] == message_id:
                self.data["channels"][channel_id][idx]["edits"].append(edited_msg_content)
                self.save_data()
                break
            
    async def run_command(self, message):
        command = message.content.split()
        if command[0] == "!fetch":
            await self.fetch(command, message)
        elif command[0] == "!purge":
            await self.purge(command, message)
        elif command[0] == "!help":
            await self.help(message)
        else:
            await message.channel.send(f"Command `{command[0]}` does not exist.")
            
    async def help(self, message):
        await message.channel.send(HELP_MESSAGE)

    async def purge(self, command, message):
        if not self.superuser_check(message.author):
            await message.channel.send(f"You don't have permission to run `{command[0]}`.")
            return
        # not enough arguments were passed into the command
        if len(command) < 2:
            await message.channel.send(f"Not enough arguments for `{command[0]}`.")
            return

        # try to grab purge limit
        try: purge_limit = int(command[1])
        except:
            await message.channel.send(f"`{command[1]}` has to be an integer.")
            return

        # purge content
        await message.channel.purge(limit = purge_limit)
        
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
            if msg["author"] == user:
                data_str = f'[{msg["attachments"]} files | {msg["date"]}] {msg["content"]}\n' + data_str
                for e in msg["edits"]: data_str += f'EDITED TO: {e}\n'

        # if there is nothing found
        if data_str == "":
            await message.channel.send(f"No messages found sent by `{user}`")
            return

        byte_io = io.BytesIO(bytes(data_str, 'utf-8'))
        f = discord.File(byte_io, filename = user + channel + ".txt")
        
        await message.channel.send(f"Fetched messages sent in `{channel}` by `{user}`.", file = f)
