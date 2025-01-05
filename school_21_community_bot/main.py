import asyncio


async def run_script(path):
    proc = await asyncio.create_subprocess_exec('python', path)
    await proc.communicate()


async def main():
    await asyncio.gather(
        run_script('user_bot.py'), run_script('admin_bot.py')
    )


if __name__ == '__main__':
    asyncio.run(main())
