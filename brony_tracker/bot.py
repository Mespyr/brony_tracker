import brony_tracker.client
import discord, json

class Bot:
    def __init__(self, data_path):
        # get data from data_path
        with open(data_path, "r") as f:
            data = json.load(f)
            self.token = data["token"] # get token from data
        
        # create client
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = brony_tracker.client.Client(intents = intents, data = data, data_path = data_path)

    def run(self):
        self.client.run(self.token)
