# https://rutube.ru/api/play/options/f2910dcbe135717a6f5e90141592bb22/?no_404=true&referer=https%253A%252F%252Frutube.ru&pver=v2&client=wdp
import os.path
import shutil
from concurrent.futures import ThreadPoolExecutor
import requests

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/98.0.4758.132 YaBrowser/22.3.1.892 Yowser/2.5 Safari/537.36',
    'accept': '*/*'
}


def get_m3u8_list(url):
    req = requests.get(url=url, headers=headers)
    video_data = req.json()
    video_author = video_data['author']['name']
    video_title = video_data['title']
    dict_repl = ["/", "\\", "[", "]", "?", "'", '"', ":", "."]
    for repl in dict_repl:
        if repl in video_title:
            video_title = video_title.replace(repl, "")
        if repl in video_author:
            video_author = video_author.replace(repl, "")
    video_title = video_title.replace(" ", "_")
    video_author = video_author.replace(" ", "_")

    video_m3u8 = video_data['video_balancer']['m3u8']
    return video_author, video_title, video_m3u8


def get_link_from_m3u8(url_m3u8, dir):
    req = requests.get(url=url_m3u8, headers=headers)
    data_m3u8_dict = []
    if not os.path.isdir(dir):
        os.mkdir(dir)

    with open(f'{dir}\\pl_list.txt', 'w', encoding='utf-8') as file:
        file.write(req.text)
    with open(f'{dir}\\pl_list.txt', 'r', encoding='utf-8') as file:
        src = file.readlines()

    for item in src:
        data_m3u8_dict.append(item)

    url_playlist = data_m3u8_dict[-1]
    return url_playlist


def get_segment_count(m3u8_link):
    req = requests.get(url=m3u8_link, headers=headers)
    data_seg_dict = []
    for seg in req:
        data_seg_dict.append(seg)
    seg_count = str(data_seg_dict[-2]).split("/")[-1].split("-")[1]
    return seg_count


def get_download_link(m3u8_link):
    link = f'{m3u8_link.split(".m3u8")[0]}/'
    return link


def download(url):
    filename = url[0].split("/")[-1]
    r = requests.get(url[0], allow_redirects=False)

    with open(f"{url[1]}\\{filename}", "wb") as binary:
        binary.write(r.content)
    print('Загружен файл:', filename)


def get_download_segment(dir, link, count):
    if not os.path.isdir(dir):
        os.mkdir(dir)
    links = []
    for item in range(1, count + 1):

        file = f'{dir}\\segment-{item}-v1-a1.ts'
        if not os.path.isfile(file):
            links.append([f'{link}segment-{item}-v1-a1.ts', dir])
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(download, links)
    print('[INFO] - Все сегменты загружены')


def merge_ts(dir, seg_dir, title, count,):
    if not os.path.isdir(dir):
        os.mkdir(dir)
    with open(f'{dir}\\{title}.ts', 'wb') as merged:
        for ts in range(1, count + 1):
            with open(f'{seg_dir}\\segment-{ts}-v1-a1.ts', 'rb') as mergefile:
                shutil.copyfileobj(mergefile, merged)
    # os.system(f"ffmpeg -i seg\\{title}.ts {author}\\{title}.mp4")
    print('[+] - Конвертирование завершено')

    file_dir = os.listdir(seg_dir)
    for file in file_dir:
        os.remove(f'{seg_dir}\\{file}')
    os.rmdir(seg_dir)


def main():
    if not os.path.isdir('seg'):
        os.mkdir('seg')
    if not os.path.isdir('gotovoe'):
        os.mkdir('gotovoe')
    while True:
        url = input('[+] - Введите ссылку на видео для загрузки >>> ').split("/")[-2]
        video_author, video_title, m3u8_url = get_m3u8_list(
            f'https://rutube.ru/api/play/options/{url}/?no_404=true&referer=https%3A%2F%2Frutube.ru')
        seg_dir = f"seg\\{video_title}"
        m3u8_link = get_link_from_m3u8(m3u8_url, seg_dir)
        seg_count = int(get_segment_count(m3u8_link))
        dwnl_link = get_download_link(m3u8_link)
        get_download_segment(seg_dir, dwnl_link, seg_count)
        merge_ts(f"gotovoe\\{video_author}",seg_dir, video_title, seg_count )


if __name__ == "__main__":
    main()
