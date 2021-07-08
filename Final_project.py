import json
import os
import requests
import sys
from pprint import pprint
import yadisk
from tqdm import tqdm
import time

result_list = []
"""
Данная функция выполняет соедение через API запрос в соц сеть VK и
скачивает фото профиля на диск в папку
:param owner_ids: - идентификатор владельца альбома.
:param count: - количество записей, которое будет получено.
"""


def get_photos_from_VK_API(owner_ids, count):
    """ читаем токен с файла """
    with open('token _test.txt', 'r') as file_object:
        token_vk = file_object.read().strip()

    '''создаем директорию и проверяем на наличие папки'''
    image_path = os.path.join(sys.path[0], 'template_photos')
    if not os.path.exists(image_path):
        os.makedirs(image_path)

    _URL_link = 'https://api.vk.com/method/photos.get'
    params = {
        'owner_id': owner_ids,
        'access_token': token_vk,
        'v': '5.131',
        'album_id': 'profile',
        'count': count,
        'photo_sizes': '1',
        'extended': 'likes'
    }
    res = requests.get(_URL_link, params=params).json()

    counter = 0

    '''Ввыодим список фотографий профиля VK'''
    for item in res['response']['items']:
        type_photo = ''
        result_dict = {}
        '''берём ссылку на максимальный размер фотографии'''
        file_url = item['sizes'][-1]['url']
        filename = str(item['likes']['count']) + '.jpeg'
        type_photo = item['sizes'][counter]['type']
        '''скачиваю картинки по ссылкам'''
        res = requests.get(file_url)
        '''Сохраняю фото в директорию'''
        with open(image_path + '/' + filename, 'wb') as file:
            file.write(res.content)

        result_dict["file_name"] = filename
        result_dict["size"] = type_photo
        result_list.append(result_dict)
        counter += 1
    file.close()
    finish = json.dumps(result_list)
    return finish


""" Данная функция выполняет сохранение фотографий на Я.Диске из локальной папки """


def put_photos_in_YaDisk():
    """ читаем токен с файла """
    with open('token.txt', 'r') as file_object:
        token_ya = file_object.read().strip()

    y = yadisk.YaDisk(token=token_ya)
    new_folder = 'template_photos'
    '''Выводит содержимое Я.Диска '''
    list_dir = list(y.listdir("/"))

    folder = []
    result_list_dir = []
    path_dir = os.getcwd()
    ''' Записываем в список все фото из папки '''
    for i in os.walk(path_dir + '\\' + str(new_folder)):
        folder.append(i)
    ''' Записываем в список все имя папок на Я.Диске для проверки '''
    for elem in list_dir:
        result_list_dir.append(elem.FIELDS['name'])
    flag = 0
    for address, dirs, files in folder:
        for file in tqdm(files):
            time.sleep(1)
            ''' Проверяю на наличие папки на Я.Диске'''
            if str(new_folder) not in result_list_dir:
                if flag == 0:
                    '''Создаёт новую папку на Я.Диск'''
                    y.mkdir(f'/{new_folder}')
                    flag = 1
                pprint(f'Файл {file} загружен')
                ''' Загружает фото из локальной папки в папку на  Я.Диск '''
                y.upload(f'{address}/{file}', f'/{new_folder}/{file}')
            else:
                try:
                    ''' Загружает фото из локальной папки в папку на  Я.Диск '''
                    y.upload(f'{address}/{file}', f'/{new_folder}/{file}')
                    pprint(f"Файл {file} загружен")
                except:
                    pprint(f"Файл {file}  уже загружен на Я. Диск. ")


if __name__ == '__main__':

    ''' Входящие данные для VK API: 
            owner_ids = '552934290' 
            count = 5 '''
pprint(get_photos_from_VK_API(owner_ids='552934290', count=5))

''' Функция для загрузки фото на Я. Диск '''
pprint(put_photos_in_YaDisk())
