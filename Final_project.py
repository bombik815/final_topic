import json
import os
import requests
import sys
from pprint import pprint
from tqdm import tqdm
import time

result_list = []
url_photos = {}
"""
Данная функция выполняет соедение через API запрос в соц сеть VK и
скачивает фото профиля на диск в папку
:param owner_ids: - идентификатор владельца альбома.
:param count: - количество записей, которое будет получено.
"""


def get_photos_from_VK_API(owner_ids, count):
    insert_token = "958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008"  # str(input("Введите  ваш токен для VK: "))
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
    res = requests.get(_URL_link, params=params).json().get('response').get('items')

    counter = 0

    '''Ввыодим список фотографий профиля VK'''
    for item in res:
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
        url_photos[filename] = file_url
        result_dict["file_name"] = filename
        result_dict["size"] = type_photo
        result_list.append(result_dict)
        counter += 1
        finish = json.dumps(result_list)
    file.close()
    print(f"Загрузка фотографий завершена в папку {image_path}")
    return res


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
        params = {"path": "/",
                  "fields": "_embedded.items.name"}
        response = requests.get(file_url, headers=headers, params=params)
        return response.json()

    def create_new_folder(self, new_folder):
        file_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {"path": new_folder}
        response = requests.put(file_url, headers=headers, params=params)
        return response.json()

    def get_upload_link(self, new_folder, url_link, filename):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {"path": new_folder + '/' + filename,
                  "url": url_link}
        response = requests.post(upload_url, params=params, headers=headers)

        response.raise_for_status()
        if response.status_code == 202:
            print(f'Фото "{filename}" загружено на диск.')
        else:
            print(f'Ошибка загрузки "{filename}": '
                  f'{response.json().get("message")}. Status code: {response.status_code}')


def put_photos_in_YaDisk(owner_idss):
    ''' Функция для загрузки фото на Я. Диск '''
    ya = YaDisk(token=owner_idss)
    new_folder = 'template_photos'

    '''Выводит содержимое Я.Диска '''
    list_dir = ya.get_f_list()

    folder = []
    result_list_dir = []
    path_dir = os.getcwd()
    image_path = os.listdir()

    ''' Записываем в список все фото из папки '''
    for i in os.walk(path_dir + '\\' + str(new_folder)):
        folder.append(i)

    flag = 0
    ''' Записываем в список все имя папок на Я.Диске для проверки '''
    for elem in list(list_dir['_embedded']['items']):
        if str(new_folder) in elem['name']:
            pprint(f' Данная папка  {new_folder}  уже существует на Я.Диске')
            flag = 1
            break
        else:
            flag = 0
            continue

    if flag == 0:
        '''Создаёт новую папку на Я.Диск'''
        ya.create_new_folder(f'/{new_folder}')
        pprint(f' Папка  {new_folder}  создана на Я.Диске')


    for file_name, url_link in tqdm(url_photos.items()):
        time.sleep(1)
        ''' Загружает фото из локальной папки в папку на  Я.Диск '''
        ya.get_upload_link(new_folder, url_link, filename=f'{file_name}')


if __name__ == '__main__':
    ''' Входящие данные для VK API: 
            owner_ids = '552934290' 
            count = 5 '''

vk_result = get_photos_from_VK_API(owner_ids=int(input("Введите ID пользователя: ").strip()), count=5)
ya_token = input('Яндекс токен:')
pprint(put_photos_in_YaDisk(ya_token))
