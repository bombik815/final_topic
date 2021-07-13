import json
import os
import requests
import sys
from pprint import pprint
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
    insert_token = str(input("Введите  ваш токен для VK: "))
    with open('token_test.txt', 'w') as token_vk:
        token_vk.write(insert_token)
        print(f' Токен был сохранен в файл- token _test.txt')

    """ читаем токен с файла """
    with open('token_test.txt', 'r') as file_object:
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
    print(f"Загрузка фотографий завершена в папку {image_path}")
    finish = json.dumps(result_list)
    return finish

# Клас для обработки запросов на Яндекс диск
class YaDisk:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token),
        }

    def get_f_list(self):
        file_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {"path": "/", "fields": "_embedded.items.name"}
        response = requests.get(file_url, headers=headers, params=params)
        return response.json()

    def create_new_folder(self, new_folder):
        file_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {"path": new_folder}
        response = requests.put(file_url, headers=headers, params=params)
        return response.json()

    def _get_upload_link(self, disk_file_path):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "True"}
        response = requests.get(upload_url, headers=headers, params=params)
        # pprint(response.json())
        return response.json()

    def upload_file_to_disk(self, disk_file_path, filename):
        href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")
        response = requests.put(href, data=filename)
        response.raise_for_status()
        if response.status_code == 201:
            print("OK")


def put_photos_in_YaDisk(owner_ids):
    ''' Функция для загрузки фото на Я. Диск '''
    ya = YaDisk(token=owner_ids)
    new_folder = 'template_photos'
    #     '''Выводит содержимое Я.Диска '''
    list_dir = ya.get_f_list()

    folder = []
    result_list_dir = []
    path_dir = os.getcwd()
    ''' Записываем в список все фото из папки '''
    for i in os.walk(path_dir + '\\' + str(new_folder)):
        folder.append(i)
    ''' Записываем в список все имя папок на Я.Диске для проверки '''
    for elem in list_dir['_embedded']['items']:
        result_list_dir.append(elem)
    flag = 0
    for address, dirs, files in folder:
        for file in tqdm(files):
            time.sleep(1)
            ''' Проверяю на наличие папки на Я.Диске'''
            if str(new_folder) not in result_list_dir:
                if flag == 0:
                    '''Создаёт новую папку на Я.Диск'''
                    ya.create_new_folder(f'/{new_folder}')
                    flag = 1
                    pprint(f'Файл {file} загружен')
                    ''' Загружает фото из локальной папки в папку на  Я.Диск '''
                    ya.upload_file_to_disk(disk_file_path=f"template_photos/{file}", filename=f'{file}')

                else:
                    try:
                        ''' Загружает фото из локальной папки в папку на  Я.Диск '''
                        ya.upload_file_to_disk(disk_file_path=f"template_photos/{file}", filename=f'{file}')
                        pprint(f"Файл {file} загружен")
                    except:
                        pprint(f"Файл {file}  уже загружен на Я. Диск. ")


if __name__ == '__main__':
    ''' Входящие данные для VK API: 
            owner_ids = '552934290' 
            count = 5 '''
pprint(get_photos_from_VK_API(owner_ids=int(input("Введите ID пользователя: ")), count=5))
pprint(put_photos_in_YaDisk(owner_ids=str(input("Введите  ваш токен для Yandex: "))))
