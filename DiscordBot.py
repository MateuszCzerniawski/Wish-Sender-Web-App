import asyncio
import threading
import discord
import DataLoader


class DiscordBot:
    def __init__(self):
        self.send_status = None
        self.receiver_id = None
        self.message = None
        self.intents = discord.Intents.default()
        self.client = discord.Client(intents=self.intents)
        self.token = DataLoader.load_discord_bot_config()['token']
        self.trigger = threading.Event()
        self.keepGoing = True
        self.client.event(self.on_ready)
        self.bot = threading.Thread(target=lambda: self.client.run(self.token))
        self.bot.start()
        while not self.client.is_ready():
            pass

    # noinspection PyAsyncCall
    async def on_ready(self):
        print('Discord Bot logged in')
        asyncio.create_task(self.listener()) #lack of await is intentional because we want it to run similarly to new Thread

    async def listener(self):
        while self.keepGoing:
            self.trigger.wait()
            self.trigger.clear()
            try:
                try:
                    destination = await self.client.fetch_user(self.receiver_id)
                except discord.errors.NotFound:
                    destination = await self.client.fetch_channel(self.receiver_id)
                await destination.send(str(self.message))
                self.send_status = 'sent'
            except Exception as e:
                print(str(e))
                self.send_status = 'error'
            self.receiver_id = False
            self.message = False

    def send(self, id, message):
        self.send_status = None
        self.receiver_id = id
        self.message = message
        self.trigger.set()
        while self.send_status is None:
            pass
        return self.send_status

    def shutdown(self):
        self.keepGoing = False
        self.client.close()
