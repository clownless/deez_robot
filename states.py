from aiogram.dispatcher.filters.state import State, StatesGroup


class UploadState(StatesGroup):
    sending_upc = State()
    sending_isrc = State()
    sending_link = State()
    sending_spotify_link = State()
    sending_sber_link = State()
