import logging
import requests
import json
import datetime
import os
import re
import shutil
import config

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.types import InputFile
from deezloader.deezloader import DeeLogin
from deezloader.exceptions import InvalidLink
from states import UploadState

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

download = DeeLogin(arl = config.deezer_arl)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("*🔥 Привет! Я бот для скачивания треков с Deezer\n🤖 Вот что я умею:\n/isrc* - _скачивание трека по ISRC за 9 часов до релиза_\n*/upc* - _скачивание альбома по UPC за 9 часов до релиза_\n\n*🧑‍💻 Разработчик: @uzkwphq*", parse_mode="markdown")


@dp.message_handler(commands=['upc'], state=None)
async def album_download(message: types.Message):
    await message.reply("Введите UPC:")
    await UploadState.sending_upc.set()

@dp.message_handler(commands=['isrc'], state=None)
async def album_download(message: types.Message):
    await message.reply("Введите ISRC:")
    await UploadState.sending_isrc.set()

@dp.message_handler(state=UploadState.sending_upc)
async def process_upc(message: types.Message, state: FSMContext):
    upc = message.text
    link = f"https://api.deezer.com/album/upc:" + upc
    response = requests.get(link).text
    data = json.loads(response)
    if 'error' in data:
        await message.reply("К сожалению по этому треку нет информации\nUPC: " + upc)
        await state.finish()
    else:
        album_link = data["link"]
        artist = data["artist"]["name"]
        title = data["title"]
        date = data["release_date"]	
        track_link = data["link"]
        cover = data["cover_xl"]
        nb_tracks = data["nb_tracks"]
        if nb_tracks == 1:
            duration = data["duration"]
            explicit_lyrics = data["explicit_lyrics"]
            dur = str(datetime.timedelta(seconds=duration))
            if explicit_lyrics == False:
                exp = "Нет"
            else:
                exp = "Да"
        os.makedirs("tracks", exist_ok=True)
        output_dir = f"tracks/{artist} - {title}"
        if nb_tracks > 1:
            await bot.send_photo(message.chat.id, cover, f"*{artist} - {title}*\n\n*UPC:* _{upc}_\n*Дата релиза:* _{date}_\n*Количество треков:* _{nb_tracks}_\n\n[Слушать на Deezer]({track_link})", parse_mode="markdown")
        elif nb_tracks == 1:
            await bot.send_photo(message.chat.id, cover, f"*{artist} - {title}*\n\n*Длительность:* _{dur}_\n*Ненормативная лексика:* _{exp}_\n*Дата релиза:* _{date}_\n*UPC:* _{upc}_\n\n[Слушать на Deezer]({track_link})", parse_mode="markdown")
        await bot.send_message(message.from_user.id, "*Начинаю скачивание!*", parse_mode="markdown")
        download.download_albumdee(f"{album_link}",output_dir=output_dir,quality_download="MP3_128",recursive_quality=False,recursive_download=True,not_interface=False,method_save=0)

        aye = f"tracks/{artist} - {title}"
        xd = os.listdir(aye)
        funnymoment = f"{aye}/{xd[0]}"
        kolvotracks = os.listdir(funnymoment)
        for x in kolvotracks:
            f = open(f"{funnymoment}/{x}","rb")
            await bot.send_audio(message.from_user.id, f, caption='[DeezRobot](t.me/deez_robot)', parse_mode="markdown")
        await bot.send_message(message.from_user.id, "*Готово!*", parse_mode="markdown")
        await state.finish()
        shutil.rmtree(aye, ignore_errors=True)
        

@dp.message_handler(state=UploadState.sending_isrc)
async def process_isrc(message: types.Message, state: FSMContext):
    isrc = message.text
    link = f"https://api.deezer.com/track/isrc:" + isrc
    response = requests.get(link).text
    data = json.loads(response)
    if 'error' in data:
        await message.reply("К сожалению по этому треку нет информации")
        await state.finish()
    else:
        track_link = data["link"]
        artist = data["artist"]["name"]
        title = data["title"]
        album = data["album"]["title"]
        date = data["release_date"]	
        track_link = data["link"]
        duration = data["duration"]
        cover = data["album"]["cover_xl"]
        explicit_lyrics = data["explicit_lyrics"]
        track_position = data["track_position"]
        dur = str(datetime.timedelta(seconds=duration))
        if explicit_lyrics == False:
            exp = "Нет"
        else:
            exp = "Да"

        os.makedirs("tracks", exist_ok=True)
        output_dir = f"tracks/{artist} - {album}"
        download.download_trackdee(f"{track_link}",output_dir=output_dir,quality_download="MP3_128",recursive_quality=False,recursive_download=True,not_interface=False,method_save=0)

        aye = f"tracks/{artist} - {album}"
        xd = os.listdir(aye)
        funnymoment = f"{aye}/{xd[0]}"
        kolvotracks = os.listdir(funnymoment)
        upc = re.findall(r'\b\d+\b', xd[0])
        await bot.send_photo(message.chat.id, cover, f"*{artist} - {title}*\n\n*Альбом:* _{album}_\n*Длительность:* _{dur}_\n*Ненормативная лексика:* _{exp}_\n*Дата релиза:* _{date}_\n*Позиция в альбоме:* _{track_position}_\n*ISRC:* _{isrc}_\n*UPC:* _{upc[0]}_\n\n[Слушать на Deezer]({track_link})", parse_mode="markdown")
        await bot.send_message(message.from_user.id, "*Отправляю трек!*", parse_mode="markdown")
        f = open(f"{funnymoment}/{album} CD 1 TRACK {track_position} (128).mp3","rb")
        await bot.send_audio(message.from_user.id, f, caption='[DeezRobot](t.me/deez_robot)', parse_mode="markdown")
        await bot.send_message(message.from_user.id, "*Готово!*", parse_mode="markdown")
        await state.finish()
        shutil.rmtree(aye, ignore_errors=True)


if __name__ == '__main__':
    executor.start_polling(dp)

