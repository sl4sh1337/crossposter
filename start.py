try:
    import tkinter as tk  # for python 3
    import tkinter.filedialog
except:
    import Tkinter as tk  # for python 2
import pygubu
import vk
import requests
import twitter

photos = ['', '', '', '']
videos = ['']


def vk_post(p, text, v):
    """
    Функция для постинга вк
    Для каждого файла запрашивается адрес сервера для загрузки, затем выполняется http post запрос с файлом и вызывается
    метод для сохранения файла
    """
    import vk_meta
    session = vk.AuthSession(vk_meta.VK_APP_ID, vk_meta.VK_EMAIL, vk_meta.VK_PASSWORD, scope="docs,wall,photos,video")
    api = vk.API(session)

    result = []

    for path in p:
        if path:
            photo_server = api.photos.getWallUploadServer(group_id=vk_meta.VK_GROUP_ID)
            photo_url = photo_server["upload_url"]
            photo_files = {'photo': open(path, 'rb')}
            photo_r = requests.post(photo_url, files=photo_files)
            photo_response = photo_r.json()
            result.append(api.photos.saveWallPhoto(group_id=vk_meta.VK_GROUP_ID, photo=photo_response["photo"], server=photo_response["server"], hash=photo_response["hash"])[0]["id"])
    for path in v:
        if path:
            video_server = api.video.save(group_id=vk_meta.VK_GROUP_ID, wallpost=0)
            video_url = video_server["upload_url"]
            vid = 'video' + str(video_server['owner_id']) + '_' + str(video_server['vid'])
            video_files = {'video_file': open(path, 'rb')}
            video_r = requests.post(video_url, files=video_files)
            video_response = video_r.json()
            result.append(vid)

    # Вызов метода для отправки поста
    api.wall.post(owner_id=(-1 * vk_meta.VK_GROUP_ID), from_group=1, message=text, attachments=','.join(result))
    print("vk sent")


def twitter_post(p, text, v):
    """
    В посте твиттера должно содержаться либо не больше четырёх фотографий, либо одно видео
    Поэтому если в посте есть одновременно фото и видео, то приоритет отдаётся фото
    """
    import twitter_meta
    api = twitter.Api(consumer_key=twitter_meta.TWI_CONSUMER_KEY, consumer_secret=twitter_meta.TWI_CONSUMER_SECRET, access_token_key=twitter_meta.TWI_ACCESS_TOKEN_KEY, access_token_secret=twitter_meta.TWI_ACCESS_TOKEN_SECRET)

    send_photos = []
    send_videos = []
    for path in p:
        if path:
            send_photos.append(path)
    for pathv in v:
        if pathv:
            vid = pathv
            break
    if send_photos:
        status = api.PostUpdate(status=text, media=send_photos)
    else:
        status = api.PostUpdate(status=text, media=vid)
    print ("twitter sent")


def facebook_post(p, text, v):
    """
    То же самое, что и с твиттером, только с помощью апи нельзя прикрепить к посту более
    одной фотографии
    """
    import fb_meta
    for path in p:
        if path:
            files = {'source': open(path, 'rb')}
            data = {'access_token':fb_meta.FB_ACCESS_TOKEN, 'caption':text}
            r = requests.post(url='https://graph.facebook.com/{}/photos'.format(fb_meta.FB_GROUP_ID), data=data, files=files)
            print('fb sent')
            return
    for pathv in v:
        if pathv:
            files = {'source': open(pathv, 'rb')}
            data = {'access_token':fb_meta.FB_ACCESS_TOKEN, 'caption':text}
            r = requests.post(url='https://graph.facebook.com/{}/videos'.format(fb_meta.FB_GROUP_ID), data=data, files=files)
            print('fb sent')
            return
    data = {'access_token':fb_meta.FB_ACCESS_TOKEN, 'caption':text}
    r = requests.post(url='https://graph.facebook.com/{}/feed'.format(fb_meta.FB_GROUP_ID), data=data)
    print('fb sent')


class Application:

    def __init__(self, master):

        #1: Create a builder
        self.builder = builder = pygubu.Builder()

        #2: Load an ui file
        builder.add_from_file('untitled.ui')

        #3: Create the widget using a master as parent
        self.mainwindow = builder.get_object('Frame_1', master)

        builder.connect_callbacks(self)

    def click(self, event):
        """Функция обработки клика по кнопке выбора фотографии"""
        id = event.widget.cget('text')[-1]
        path = tk.filedialog.askopenfilename(filetypes=(('Изображения', '*.jpg;*.jpeg;*.png;*.gif'), ('All files', '*.*')))
        label = self.builder.get_object('Label' + id)
        label.config(text=path[path.rfind("/")+1:])
        photos[int(id)-1] = path

    def on_submit(self, event):
        """Функция обработки клика по кнопке отправки"""
        text = self.builder.get_object('Text')
        message = text.get("1.0","end")[:-1]
        vk_post(photos, message, videos)
        twitter_post(photos, message, videos)
        facebook_post(photos, message, videos)

    def on_video_click(self, event):
        """Функция обработки клика по кнопке выбора видео"""
        path = tk.filedialog.askopenfilename(filetypes=(('Видео', '*.AVI;*.MP4;*.3GP;*.MPEG;*.MOV;*.MP3;*.FLV;*.WMV'), ('All files', '*.*')))
        label = self.builder.get_object('Video1')
        label.config(text=path[path.rfind("/")+1:])
        videos[0] = path


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
