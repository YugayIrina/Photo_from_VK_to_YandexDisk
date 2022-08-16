import json
import random
import time
import requests
from tenacity import wait_fixed, stop_after_attempt, retry
from tqdm import tqdm


class Yandex:
    def __init__(self, folder_name, yandex_token, num=5):
        # Получаем основные параметры фото для загрузки на YandexDisk
        self.token = yandex_token
        self.added_files_num = num
        self.url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        self.headers = {'Authorization': self.token}
        self.folder = self._create_folder(folder_name)

    @retry(wait=wait_fixed(10), stop=stop_after_attempt(3))
    def _send_requests(self, method, url, headers, params):
        time.sleep(random.randint(3, 5))
        if method == 'get':
            try:
                req_get = requests.get(url=url, headers=headers, params=params)

            except Exception as e:
                print(f'Не удалось отправить get запрос в Yandex, ошибка: {e}')
            else:
                return req_get
        elif method == 'post':
            try:
                req_post = requests.post(url=url, headers=headers, params=params)
            except Exception as e:
                print(f'Не удалось отправить post запрос в Yandex, ошибка: {e}')
            else:
                return req_post

        elif method == 'put':
            try:
                req_put = requests.put(url=url, headers=headers, params=params)
            except Exception as e:
                print(f'Не удалось отправить put запрос в Yandex, ошибка: {e}')
            else:
                return req_put
        else:
            print(f'Данный метод: {method} не предусмотрен')

        return

    def _create_folder(self, folder_name):
        # Создаем папку на YandexDisk для дальнейшей загрузки фото
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {'path': folder_name}

        try:
            req_put = self._send_requests(method='put', url=url, headers=self.headers, params=params)
        except:
            print('Не удалось создать папку на YandexDisk, не смотря на несколько попыток')
            print('Программа будет выключена через 1 минуту')
            time.sleep(60)
            exit()
        else:
            if req_put.status_code == 201:
                print(f'\nПапка {folder_name} папка успешно создана в корневом каталоге Яндекс диска\n')
                return folder_name


            elif json.loads(req_put.text)['error'] == 'DiskPathPointsToExistentDirectoryError':
                print(f'\nПапка {folder_name} уже существует. Файлы с одинаковыми именами не будут скопированы\n')
                return folder_name
            else:
                print(req_put.text['message'])
                print('Программа будет выключена через 1 минуту')
                time.sleep(60)
                exit()

    def _in_folder(self, folder_name):
        # Получаем ссылку для загрузки фото на YandexDisk
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {'path': folder_name}
        try:
            resource = self._send_requests('get', url=url, headers=self.headers, params=params)
        except:
            print('Не удалось создать папку на YandexDisk, не смотря на несколько попыток')
            print('Программа будет выключена через 1 минуту')
            time.sleep(60)
            exit()
        else:
            resource = resource.json()['_embedded']['items']
        in_folder_list = []
        for elem in resource:
            in_folder_list.append(elem['name'])
        return in_folder_list

    def create_copy(self, dict_files):
        # Загружаем фото на YandexDisk
        files_in_folder = self._in_folder(self.folder)
        copy_counter = 0
        for key, i in zip(dict_files.keys(), tqdm(range(self.added_files_num))):
            if copy_counter < self.added_files_num:
                if key not in files_in_folder:
                    params = {'path': f'{self.folder}/{key}', 'url': dict_files[key], 'overwrite': 'false'}
                    try:
                        self._send_requests('post', url=self.url, headers=self.headers, params=params)
                    except:
                        print(
                            'Не смотря на несколько попыток, не удалось отправить пост запрос на YandexDisk для загрузки фото')
                        print('Программа будет выключена через 1 минуту')
                        time.sleep(60)
                        exit()

                    else:
                        copy_counter += 1
                else:
                    print(f'Внимание: Файл {key} уже существует')
            else:
                break

        print(f'\nЗапрос завершен, новых файлов скопировано (по умолчанию: 5): {copy_counter}'
              f'\nВсего файлов в исходном альбоме VK: {len(dict_files)}')
