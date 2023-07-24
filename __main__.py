import brony_tracker
import discord, json

DATAPATH = "data.json"

with open(DATAPATH, "r") as f:
    # get token from data
    data = json.load(f)
    token = data["token"] 

    # create client
    intents = discord.Intents.default()
    intents.message_content = True
    client = brony_tracker.client.Client(intents = intents, data = data, datapath = DATAPATH)

    # run client
    client.run(token)
