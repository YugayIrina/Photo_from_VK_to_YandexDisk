import datetime
import random
import time
import requests
from tenacity import retry, wait_fixed, stop_after_attempt


class VkRequest:
    def __init__(self, vk_token, vk_id, version='5.131'):
        # Получаем основные параметры для VK
        self.token = vk_token
        self.id = vk_id
        self.version = version
        self.start_params = {'access_token': self.token, 'v': self.version}
        self.json, self.export_dict = self._sort_info()

    @retry(wait=wait_fixed(10), stop=stop_after_attempt(3))
    def _request_photo_info(self, url, **params):
        time.sleep(random.randint(3,5))
        try:
            photo_info = requests.get(url, params={**self.start_params, **params}).json()['response']
        except Exception as e:
            print(f'Ошибка VK request: {e}')
            raise Exception
        else:
            return photo_info

    def _get_photo_info(self):
        # Получаем кол-во и массив фото
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': 'profile', 'photo_sizes': 1, 'extended': 1, 'rev': 1}

        try:
            photo_info = self._request_photo_info(url, **params)
        except:
            print('Не смотря на несколько попыток, не удалось получить файлы от VK')
            print('Программа будет выключена через 1 минуту')
            time.sleep(60)
            exit()
        else:
            return photo_info['count'], photo_info['items']

    def find_max_dpi(self, dict_in_search):
        # Получаем максимальный размер фото
        max_dpi = 0
        need_elem = 0
        for j in range(len(dict_in_search)):
            file_dpi = dict_in_search[j].get('width') * dict_in_search[j].get('height')
            if file_dpi > max_dpi:
                max_dpi = file_dpi
                need_elem = j
        return dict_in_search[need_elem].get('url'), dict_in_search[need_elem].get('type')

    def time_convert(self, time_unix):
        # Получаем дату загрузки фото в адаптированном формате
        time_bc = datetime.datetime.fromtimestamp(time_unix)
        str_time = time_bc.strftime('%Y-%m-%d time %H-%M-%S')
        return str_time

    def _get_logs_only(self):
        # Получаем словарик с параметрами фото
        photo_count, photo_items = self._get_photo_info()
        result = {}
        for i in range(photo_count):
            likes_count = photo_items[i]['likes']['count']
            url_download, picture_size = self.find_max_dpi(photo_items[i]['sizes'])
            time_warp = self.time_convert(photo_items[i]['date'])
            new_value = result.get(likes_count, [])
            new_value.append(
                {'likes_count': likes_count, 'add_name': time_warp, 'url_picture': url_download, 'size': picture_size})
            result[likes_count] = new_value
        return result

    def _sort_info(self):
        # Получаем словарик с параметрами фото и списка JSON для выгрузки
        json_list = []
        sorted_dict = {}
        picture_dict = self._get_logs_only()
        counter = 0
        for elem in picture_dict.keys():
            for value in picture_dict[elem]:
                if len(picture_dict[elem]) == 1:
                    file_name = f'{value["likes_count"]}.jpeg'
                else:
                    file_name = f'{value["likes_count"]} {value["add_name"]}.jpeg'
                json_list.append({'file name': file_name, 'size': value["size"]})
                if value["likes_count"] == 0:
                    sorted_dict[file_name] = picture_dict[elem][counter]['url_picture']
                    counter += 1
                else:
                    sorted_dict[file_name] = picture_dict[elem][0]['url_picture']
        return json_list, sorted_dict
