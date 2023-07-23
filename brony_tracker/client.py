import discord, json

class Client(discord.Client):
    def __init__(self, data, data_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_path = data_path
        self.data = data

    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        channel_name = message.channel.name
        author = message.author.name
        message_content = message.content
        date = message.created_at.strftime("%d/%m/%Y %H:%M:%S")

        # create new entry if data for channel hasn't been stored yet
        if channel_name not in self.data["channels"]:
            self.data["channels"][channel_name] = []

        # save new data
        self.data["channels"][channel_name].append([author, date, message_content])
        with open(self.data_path, "w") as f:
            json.dump(self.data, f, indent = 2)
