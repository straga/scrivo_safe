import asyncio


class Core:
    def __init__(self, name="root"):
        self.name = name

    async def run(self):
        while True:
            await asyncio.sleep(5)
            print("RUN", self.name)
