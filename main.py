import json
import os
from dotenv import load_dotenv
from vk_download_file import VkRequest
from yandex_disk_upload_file import Yandex

load_dotenv()

if __name__ == '__main__':
    vk_token = os.getenv("VK_TOKEN")
    vk_id = os.getenv("VK_ID")

    ya_token = os.getenv("YA_TOKEN")

    my_VK = VkRequest(vk_token, vk_id)  # Получение JSON списка с информацией о фотографиях
    with open('my_VK_photo.json', 'w') as outfile:  # Сохранение JSON списка в файл my_VK_photo.json
        json.dump(my_VK.json, outfile)

    # Создаем экземпляр класса Yandex с параметрами: "Имя папки", "Токен" и количество скачиваемых файлов
    my_yandex = Yandex('VK photo copies', ya_token, 5)
    my_yandex.create_copy(my_VK.export_dict)  # Вызываем метод create_copy для копирования фотографий с VK на Я-диск
