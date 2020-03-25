import argparse
from dotenv import dotenv_values

import datetime

import asyncio

from heandler import handle_text
from utils import write_file
from config import HOST, READ_PORT, HISTORY_FILE

import logging

logger = logging.getLogger(__name__)


async def read_chat(host, port, filename):
    reader, writer = await asyncio.open_connection(host, port)

    await write_file(filename, handle_text('Установлено соединение.'))

    delay = 0
    error_count = 0

    while True:
        try:
            data = await reader.readline()

            message = data.decode()
            print(message.strip())

            await write_file(filename, handle_text(message))

            if error_count > 0:
                await write_file(filename, handle_text('Установлено соединение.'))

            error_count = 0
            delay = 0


        except asyncio.CancelledError:
            error_count += 1

            message = handle_text('Нет соединения. Повторная попытка.')

            if error_count > 2:
                delay = 3
                message = handle_text('Нет соединения. Повторная попытка через 3 сек.')

            await write_file(filename, message)

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
