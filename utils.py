import aiofiles


async def write_file(path, text, mode='a'):
    async with aiofiles.open(path, mode=mode, encoding='utf-8') as fd:
        await fd.write(text)
