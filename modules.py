#!/usr/bin/env python3

import base64
import hashlib
import json
import os
import random
import string
import urllib.request
from datetime import datetime, timedelta

import anitopy
import bencoding
from colorama import Fore, Style

import bencode
import color


def database_builder():
    list_database = []
    list_origin_database = []
    list_torrents_dir = [f for f in os.listdir('torrents') if os.path.isfile(os.path.join('torrents', f))]

    origin_database_loaded = False
    database_loaded = False
    full_loaded = False

    if os.path.isfile('anime_database.json'):
        anime_database_file = open('anime_database.json', encoding='utf-8')
        color.color_print(Fore.YELLOW, '[PROCESSING]', 'LOADING ANIME OFFLINE DATABASE\n')
        anime_database_obj = json.load(anime_database_file)
    else:
        color.color_print(Fore.CYAN, '[INFO]', 'MISSING OFFLINE DATABASE. DOWNLOADING...')
        color.color_print(Fore.CYAN, '[INFO]', 'THANK YOU FOR MANAMI PROJECT TO PROVIDE ME A OFFLINE DATABASE')
        urllib.request.urlretrieve(
            'https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database.json',
            'anime_database.json')
        color.color_print(Fore.CYAN, '[INFO]', 'DOWNLOAD COMPLETED\n')
        color.color_print(Fore.YELLOW, '[PROCESSING]', 'LOADING ANIME OFFLINE DATABASE\n')
        anime_database_file = open('anime_database.json', encoding='utf-8')
        anime_database_obj = json.load(anime_database_file)

    if os.path.isfile('output/database_original.json'):
        origin_database_json_file = open('output/database_original.json', encoding='utf-8')

        try:
            origin_database_obj = json.load(origin_database_json_file)
            origin_database_loaded = True
        except:
            origin_database_loaded = False
        database_json_file = open('output/database.json', encoding='utf-8')

        try:
            database_obj = json.load(database_json_file)
            database_loaded = True
        except:
            database_loaded = False

    if origin_database_loaded and database_loaded:
        full_loaded = True
        list_database = database_obj
        list_origin_database = origin_database_obj

    added_new_state = False

    color.color_print(Fore.LIGHTMAGENTA_EX, '[COPYRIGHT]', 'MANAMI PROJECT: ANIME OFFLINE DATABASE')
    color.color_print(Fore.LIGHTMAGENTA_EX, '[COPYRIGHT]', 'IGORCMOURA: ANITOPY')
    color.color_print(Fore.LIGHTMAGENTA_EX, '[COPYRIGHT]', 'JCUL: BENCODE\n')

    color.color_print(Fore.YELLOW, '[PROCESSING]', 'PARSE TORRENTS\n')

    for i in list_torrents_dir:
        torrent_filename = i
        torrent_full_path = 'torrents/' + i
        with open(torrent_full_path, 'rb') as fh:
            torrent_data = fh.read()

        if not search_database(list_database, i) or not full_loaded:
            torrent = bencode.decode(torrent_data)

            torrent_announces = []
            torrent_files = []
            torrent_creation_date = ''
            torrent_hash = ''
            torrent_magnet = ''
            torrent_total_length = 0

            for im in torrent:
                torrent_creation_date = (
                        datetime.utcfromtimestamp(int(im[b'creation date'])) - timedelta(hours=9)).strftime(
                    '%Y-%m-%d %H:%M:%S')
                torrent_temp_announce = []

                for imfw in im[b'announce-list']:
                    torrent_temp_announce.append(imfw[0].decode("utf-8"))
                    torrent_hash = str(hashlib.sha1(bencoding.bencode(im[b'info'])).hexdigest())
                    magnet_temp = 'magnet:?xt=urn:btih:{}'.format(torrent_hash)
                    torrent_magnet = magnet_temp

                torrent_announces = torrent_temp_announce

                if b'files' in im[b'info']:
                    for imf in im[b'info'][b'files']:
                        torrent_files.append(
                            {'name': imf[b'path'][0].decode("utf-8"), 'size': format_size_units(imf[b'length'])})
                        torrent_total_length += imf[b'length']
                else:
                    torrent_total_length = im[b'info'][b'length']
                    torrent_files.append(
                        {'name': im[b'info'][b'name'].decode("utf-8"),
                         'size': format_size_units(im[b'info'][b'length'])})

            torrent_size = format_size_units(torrent_total_length)

            info_id = random_string_digits(10)

            result_anitopy = anitopy.parse(torrent_filename)
            anime_db_result = search_anime(anime_database_obj, result_anitopy['anime_title'])

            json_data_for_add = {'id': info_id, 'file_name': torrent_filename, 'title': result_anitopy['anime_title']}

            if 'episode_number' in result_anitopy:
                json_data_for_add['episode'] = result_anitopy['episode_number']
            else:
                json_data_for_add['episode'] = None

            json_data_for_add['hash'] = torrent_hash
            json_data_for_add['size'] = torrent_size

            if 'video_resolution' in result_anitopy:
                json_data_for_add['resolution'] = result_anitopy['video_resolution']
            else:
                json_data_for_add['resolution'] = None

            if 'video_term' in result_anitopy:
                json_data_for_add['video_codec'] = result_anitopy['video_term']
            else:
                json_data_for_add['video_codec'] = None

            if 'audio_term' in result_anitopy:
                json_data_for_add['audio_codec'] = result_anitopy['audio_term']
            else:
                json_data_for_add['audio_codec'] = None

            if 'release_group' in result_anitopy:
                json_data_for_add['release_group'] = result_anitopy['release_group']
            else:
                json_data_for_add['release_group'] = None

            json_data_for_add['created_date'] = torrent_creation_date
            json_data_for_add['magnet_url'] = torrent_magnet
            json_data_for_add['torrent_url'] = 'https://anime.cryental.dev/download/' + info_id + '.torrent'
            json_data_for_add['extra'] = {'announces': torrent_announces, 'files': torrent_files}

            if not anime_db_result:
                json_data_for_add['metadata'] = None
            else:
                info_type = None
                info_episodes = None
                info_picture = None
                info_thumbnail = None
                info_status = None

                if 'type' in anime_db_result:
                    info_type = anime_db_result['type']
                if 'episodes' in anime_db_result:
                    info_episodes = anime_db_result['episodes']
                if 'picture' in anime_db_result:
                    info_picture = anime_db_result['picture']
                if 'thumbnail' in anime_db_result:
                    info_thumbnail = anime_db_result['thumbnail']
                if 'status' in anime_db_result:
                    info_status = anime_db_result['status']

                json_data_for_add['metadata'] = {'type': info_type, 'episodes': info_episodes, 'picture': info_picture,
                                                 'thumbnail': info_thumbnail, 'status': info_status}

            list_database.append(json_data_for_add)

            if not search_database(list_origin_database, i) or not full_loaded:
                json_original_data_for_add = {'id': info_id, 'file_name': torrent_filename, 'hash': torrent_hash}

                with open(torrent_full_path, "rb") as f:
                    encodedZip = base64.b64encode(f.read())
                    json_original_data_for_add['raw_data'] = encodedZip.decode()
                json_original_data_for_add['created_date'] = torrent_creation_date
                list_origin_database.append(json_original_data_for_add)

            added_new_state = True

            color.color_print(Fore.YELLOW, '[PROCESSED]', i)
        else:
            color.color_print(Fore.LIGHTRED_EX, '[SKIPPED]', i)

    print('')
    if added_new_state or not full_loaded:
        color.color_print(Fore.YELLOW, '[PROCESSING]', 'SORTING LIST')
        list_database.sort(key=sortSecond, reverse=True)

        color.color_print(Fore.YELLOW, '[PROCESSING]', 'SORTING ORIGINAL LIST')
        list_origin_database.sort(key=sortSecond, reverse=True)

        color.color_print(Fore.YELLOW, '[PROCESSING]', 'DISK ACCESSING')

        with open('output/database.json', 'w') as outfile:
            color.color_print(Fore.YELLOW, '[PROCESSING]', 'WRITING LIST')
            json.dump(list_database, outfile)

        color.color_print(Fore.YELLOW, '[PROCESSING]', 'DISK ACCESSING')
        with open('output/database_original.json', 'w') as outfile:
            color.color_print(Fore.YELLOW, '[PROCESSING]', 'WRITING LIST ORIGINAL')
            json.dump(list_origin_database, outfile)

        color.color_print(Fore.YELLOW, '[PROCESSING]', 'WRITING UPDATED DATE')
        today = datetime.now()
        new_days = open('output/updated_on.txt', 'w')
        new_days.write(today.strftime("%Y-%m-%d %H:%M:%S"))
        new_days.close()

        color.color_print(Fore.YELLOW, '[PROCESSING]', 'WRITING HASH FILES')
        database_md5 = str(md5('output/database.json'));
        origin_database_md5 = str(md5('output/database_original.json'));
        updated_md5 = str(md5('output/updated_on.txt'));

        with open('output/database.json.md5', 'w') as outfile:
            outfile.write(database_md5)
        with open('output/database_original.json.md5', 'w') as outfile:
            outfile.write(origin_database_md5)
        with open('output/updated_on.txt.md5', 'w') as outfile:
            outfile.write(updated_md5)

    color.color_print(Fore.YELLOW, '[DONE]', 'COMPLETED\n')


def sortSecond(item):
    return item['created_date']


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return str(hash_md5.hexdigest()).replace('"', '')


def format_size_units(byte_value):
    unit = ["Bytes", "KB", "MB", "GB"]
    unit_flag = 0
    while byte_value >= 1024:
        byte_value = byte_value / 1024
        unit_flag += 1
    byte_value_display = str(round(byte_value, 2)) + " " + unit[unit_flag]
    return byte_value_display


def random_string_digits(string_length=6):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(string_length)).upper()


def search_anime(json_obj, anime_name):
    for item in json_obj["data"]:
        if item["title"] == anime_name:
            return item
    return False


def search_database(json_obj, anime_name):
    for item in json_obj:
        if item["file_name"] == anime_name:
            return item
    return False
