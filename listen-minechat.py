import argparse
from dotenv import dotenv_values

import datetime

import asyncio
import aiofiles

from config import HOST, READ_PORT, HISTORY_FILE

import logging

logger = logging.getLogger(__name__)


def get_current_time_str():
    return datetime.datetime.now().strftime('[%d.%m.%y %H:%M:%S]')


def handle_text(text):
    return '{} {}\n'.format(get_current_time_str(), text)


async def write_file(path, text, mode='w'):
    async with aiofiles.open(path, mode=mode) as fd:
        await fd.write(text)


async def read_chat(host, port, filename):
    reader, writer = await asyncio.open_connection(host, port)

    message = handle_text('Установлено соединение.')
    await write_file(filename, message, 'a')

    delay = 0
    error_count = 0

    while True:
        try:
            data = await reader.readline()

            message = data.decode()
            print(message.strip())

            message_with_datetime = handle_text(message)
            await write_file(filename, message_with_datetime, 'a')

            if error_count > 0:
                message = handle_text('Установлено соединение.')
                await write_file(filename, message, 'a')

            error_count = 0
            delay = 0


        except asyncio.CancelledError:
            error_count += 1

            message = handle_text('Нет соединения. Повторная попытка.')

            if error_count > 2:
                delay = 3
                message = handle_text('Нет соединения. Повторная попытка через 3 сек.')

            await write_file(filename, message, 'a')

            await asyncio.sleep(delay)


def parse_args(host, port, history):
    parser = argparse.ArgumentParser(description='Слушаем чат.')

    parser.add_argument('--host', default=host)
    parser.add_argument('--port', default=port)
    parser.add_argument('--history', default=history, help='history file')

    return parser.parse_args()


def main():
    values_dict = dotenv_values()

    host = values_dict.get('HOST', HOST)
    port = values_dict.get('READ_PORT', READ_PORT)
    history = values_dict.get('HISTORY_FILE', HISTORY_FILE)

    args = parse_args(host, port, history)

    asyncio.run(
        read_chat(args.host, args.port, args.history)
    )


if __name__ == '__main__':
    main()
