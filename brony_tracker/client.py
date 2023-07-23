import discord, json

class Client(discord.Client):
    def __init__(self, data, data_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_path = data_path
        self.data = data

    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        # don't track messages sen't by the bot
        if message.author == self.user: return

        channel_name = f'<#{message.channel.id}>'
        author = f'<@{message.author.id}>'
        message_content = message.content
        date = message.created_at.strftime("%d/%m/%y %H:%M")
        attachment_count = len(message.attachments)

        # create new entry if data for channel hasn't been stored yet
        if channel_name not in self.data["channels"]:
            self.data["channels"][channel_name] = []

        # save new data
        self.data["channels"][channel_name].append([author, date, message_content, attachment_count])
        with open(self.data_path, "w") as f:
            json.dump(self.data, f, indent = 2)

        # if message is not a command, end the function
        if not message.content.startswith("!"): return

        command = message.content.split()
        if command[0] == "!fetch":
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
            await message.channel.send(f"Fetching messages sent in `{channel}` by `{user}`.")
            channel_messages = self.data["channels"][channel]
            msg_str = ""
            for msg in channel_messages:
                if msg[0] == user:
                    msg_str += f'[{msg[3]} files | {msg[1]}] {msg[2]}\n'

            if msg_str == "":
                await message.channel.send(f"No messages found sent by `{user}`")
                return
            await message.channel.send(f"```{msg_str}```")

        elif command[0] == "!help":
            await message.channel.send(f"""```
!help               - display help message
!fetch USER CHANNEL - fetch user's messages
```""")

        else:
            await message.channel.send(f"Command `{command[0]}` does not exist.")
