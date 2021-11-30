from aiohttp.helpers import proxies_from_env
import discord
from discord.ext import tasks
import aiohttp
import configparser
import logging
import os

CURDIR = os.path.dirname(os.path.abspath(__file__))

class MyBot(discord.Client):
    def __init__(self, channel, **kargs) -> None:
        self.channel = channel
        super().__init__(**kargs)
        self.counter = 0
        self.my_background_task.start()

    @tasks.loop(seconds=60)
    async def my_background_task(self):
        print(self.channel)
        channel = self.get_channel(id=int(self.channel)) # replace with channel_id
        print(channel)
        self.counter += 1
        await channel.send(self.counter)


    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready() 
    

def main():
    cfg = configparser.ConfigParser()
    cfg.read('config.ini')
    proxy = cfg['DEFAULT']['proxy']
    token = cfg['DISCORD']['token']
    channel = cfg['DISCORD']['channel']

    conn = aiohttp.TCPConnector(ssl =False)
    
    client :discord.Client = MyBot(channel)
    if proxy:
        client :discord.Client = MyBot(channel, conn=conn, proxy="http://127.0.0.1:1080")
    client.run(token)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(funcName)s %(lineno)s %(filename)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    main()