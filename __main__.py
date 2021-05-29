#!/usr/bin/env python3

# -*- coding:utf-8 -*-

import html.parser
import json
import os
import sys
import time
import asyncio
import aiohttp
import aiofiles

from colorama import init, Fore

import color
import modules


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


async def main():
    init()

    crawl_new_torrent_only = True
    cron_job = True
    cron_job_interval = 2

    cls()
    while True:
        print('Ohys-Raws Crawler Engine 4.17\nPython Version\n\nDeveloped By Cryental\n')

        if not os.path.exists('torrents'):
            os.makedirs('torrents')

        if not os.path.exists('output'):
            os.makedirs('output')

        if crawl_new_torrent_only and cron_job:
            color.color_print(Fore.YELLOW, '[!]', 'CRONJOB SET: INTERVAL TO {} SEC'.format(cron_job_interval) + '\n')
            time.sleep(cron_job_interval)

        color.color_print(Fore.YELLOW, '[DONE]', 'READING HEADERS')
        color.color_print(Fore.YELLOW, '[DONE]', 'WEBCLIENT INIT')
        color.color_print(Fore.YELLOW, '[DONE]', 'SET NORMAL HEADERS\n')

        color.color_print(Fore.YELLOW, '[RUNNING]', 'TORRENT LIST LOADING\n')

        if crawl_new_torrent_only:
            color.color_print(Fore.YELLOW, '[DONE]', 'MODE SELECTED - NEW TORRENT ONLY MODE\n')
        else:
            color.color_print(Fore.YELLOW, '[DONE]', 'MODE SELECTED - FULL DUMP MODE\n')

        if not crawl_new_torrent_only:
            color.color_print(Fore.YELLOW, '[RUNNING]', 'ALL TORRENT LIST LOADING\n')
        else:
            color.color_print(Fore.YELLOW, '[RUNNING]', 'NEW TORRENT LIST LOADING\n')

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/80.0.3987.132 Safari/537.36"}

        cancel_crawling_state = False
        new_torrent_state = False

        try:
            for i in range(0, 150):
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://ohys.nl/tt/json.php?dir=disk&p={}'.format(str(i)),headers=headers) as req:
                        contents_array = json.loads(await req.text())

                        if len(contents_array) == 0:
                            break
                        for item in contents_array:
                            decoded_file_name = html.unescape(item['t'])
                            if not os.path.isfile('torrents/' + decoded_file_name) or os.stat(
                                    'torrents/' + decoded_file_name).st_size == 0:
                                async with session.get('https://ohys.nl/tt/' + item['a']) as file_req:
                                    file = await aiofiles.open('torrents/' + decoded_file_name, mode='wb')
                                    await file.write(await file_req.read())
                                    await file.close()
                                color.color_print(Fore.LIGHTGREEN_EX, '[DOWNLOADED]', decoded_file_name)
                                new_torrent_state = True
                            elif crawl_new_torrent_only:
                                cancel_crawling_state = True
                            else:
                                color.color_print(Fore.LIGHTRED_EX, '[SKIPPED]', decoded_file_name)
                        if cancel_crawling_state:
                            break
        except:
            pass

        print('')
        color.color_print(Fore.YELLOW, '[DONE]', 'TORRENT LOADED\n')

        if new_torrent_state:
            color.color_print(Fore.YELLOW, '[PROCESSING]', 'OUTPUT TO JSON TYPE\n')
            time.sleep(2)
            modules.database_builder()
            color.color_print(Fore.YELLOW, '[DONE]', 'OUTPUT TO JSON TYPE')
        if not cron_job:
            sys.exit(0)
        cls()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
