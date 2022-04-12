import requests
import json
import time
from progress.bar import IncrementalBar

token_vk = "958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008"
token_yd = "..."
# test_vk_id = 552934290


class YaUploader:
    def __init__(self):

        self.token_vk = token_vk
        self.token_yd = token_yd
        self.vk_id = input('Введите ID профиля VK: ')
        self.yd_folder = input('Введите название папки на Яндекс Диске: ')
        self.photo_count = int(input('Введите количество фотографий для сохранения (5 по умолчанию): '))

    def create_new_folder(self):
        '''Метод, создающий новую папку для загрузки фотографиий на Яндекс Диск'''
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token_yd}'}
        params = {'path': self.yd_folder}
        response = requests.put(url=url, headers=headers, params=params)
        if response.status_code == 201: # успешное создание папки
            return print(f"Папка: {self.yd_folder} успешно создана")
        elif response.status_code == 409: # если папка уже создана
            pass
        else:
            return print(f"Ошибка выполнения запроса. Код ошибки: {response.status_code}")

    def get_requests_vk(self):
        '''Метод для получения словаря, описывающего фотографии из профиля ВК'''
        url = "https://api.vk.com/method/photos.get?"
        params = {
            'owner_id': self.vk_id,
            'album_id': 'profile',
            'extended': '1',
            'photo_sizes': '1',
            'access_token': self.token_vk,
            'v': '5.131'
        }
        response = requests.get(url=url, params=params)
        if response.status_code != 200:
            print('Ошибка')
        return response.json()

    def upload_file_yd(self, file_name, url_vk):
        '''Метод для загрузки файлов на Яндекс Диск'''
        self.create_new_folder()
        file_path = self.yd_folder + '/' + file_name
        up_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token_yd}'}
        params = {'url': url_vk, 'path': file_path}
        response = requests.post(url=up_url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 202:
            print(f'\n Файл {file_name} загружен на Яндекс Диск')

    def json_creator(self, info):
        '''Метод создания json-файла отчета'''
        with open('info_file.json', 'w') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

    def get_response(self):
        '''Метод, формирующий json-файл отчет'''
        count = 0
        info_list = []
        final_list = []
        for i in self.get_requests_vk()['response']['items']:
            if count < self.photo_count:
                temp_dict = {'file_name': f"{str(i['likes']['count'])}" + '.jpg',
                                 'size': f"{i['sizes'][-1]['type']}"}
                file_name = f"{str(i['likes']['count'])}" + '.jpg'
                if file_name not in info_list:
                    file_name = file_name
                    info_list.append(file_name)
                    final_list.append(temp_dict)
                    self.upload_file_yd(file_name, f"{i['sizes'][-1]['url']}")
                    count += 1
                    # print(file_name)
                else:
                    another_dict = {'file_name': f"{str(i['likes']['count'])}" + f"({str(i['date'])})" + '.jpg',
                                      'size': f"{i['sizes'][-1]['type']}"}
                    file_name = f"{str(i['likes']['count'])}" + f"({str(i['date'])})" + '.jpg'
                    info_list.append(file_name)
                    final_list.append(another_dict)
                    self.upload_file_yd(file_name, f"{i['sizes'][-1]['url']}")
                    count += 1
                    # print(file_name)
        self.json_creator(final_list)

    def progress_bar(self):
        """Метод, создающий прогресс-бар статуса загрузки фото на Яндекс Диск"""
        if self.photo_count is not None:
            bar = IncrementalBar('Загрузка', max=self.photo_count)
            for number in range(self.photo_count):
                bar.next()
                time.sleep(1)
            self.get_response()
            bar.finish()
        else:
            self.count_save = 5
            bar = IncrementalBar('Загрузка', max=self.photo_count)
            for number in range(5):
                bar.next()
                time.sleep(1)
            self.get_response()
            bar.finish()

if __name__ == '__main__':
    uploader = YaUploader()
    uploader.progress_bar()