import telebot
from loguru import logger
import os
import requests
from collections import Counter

YOLO_URL = 'http://localhost:8081'


class Bot:

    def __init__(self, token):
        self.bot = telebot.TeleBot(token, threaded=False)
        self.bot.set_update_listener(self._bot_internal_handler)

        self.current_msg = None

    def _bot_internal_handler(self, messages):
        """Bot internal messages handler"""
        for message in messages:
            self.current_msg = message
            self.handle_message(message)

    def start(self):
        """Start polling msgs from users, this function never returns"""
        logger.info(f'{self.__class__.__name__} is up and listening to new messages....')
        logger.info(f'Telegram Bot information\n\n{self.bot.get_me()}')

        self.bot.infinity_polling()

    def send_text(self, text):
        self.bot.send_message(self.current_msg.chat.id, text)

    def send_text_with_quote(self, text, message_id):
        self.bot.send_message(self.current_msg.chat.id, text, reply_to_message_id=message_id)

    def is_current_msg_photo(self):
        return self.current_msg.content_type == 'photo'

    def download_user_photo(self, quality=2):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :param quality: integer representing the file quality. Allowed values are [0, 1, 2]
        :return:
        """
        if not self.is_current_msg_photo():
            raise RuntimeError(
                f'Message content of type \'photo\' expected, but got {self.current_msg.content_type}')

        file_info = self.bot.get_file(self.current_msg.photo[quality].file_id)
        data = self.bot.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def handle_message(self, message):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {message}')
        self.send_text(f'Your original message: {message.text}')



class QuoteBot(Bot):
    def handle_message(self, message):
        logger.info(f'Incoming message: {message}')

        if message.text != 'Please don\'t quote me':
            self.send_text_with_quote(message.text, message_id=message.message_id)




class ObjectDetectionBot(Bot):
    def handle_message(self, message):
        logger.info(f'Incoming message: {message}')

        if message.chat.type == 'private' or ():
            if self.is_current_msg_photo():
                photo_path = self.download_user_photo()

                # Send the photo to the YOLO service for object detection
                res = requests.post(f'{YOLO_URL}/predict', files={
                    'file': (photo_path, open(photo_path, 'rb'), 'image/png')
                })

                if res.status_code == 200:
                    detections = res.json()
                    logger.info(f'response from detect service with {detections}')

                    # calc summary
                    element_counts = Counter([l['class'] for l in detections])
                    summary = 'Objects Detected:\n'
                    for element, count in element_counts.items():
                        summary += f"{element}: {count}\n"

                    self.send_text(summary)

                else:
                    self.send_text('Failed to perform object detection. Please try again later.')






if __name__ == '__main__':

    with open('.telegramToken') as f:
        _token = f.read()

    my_bot = ObjectDetectionBot(_token)


    @my_bot.bot.message_handler(commands=['start'])
    def handle_start(message):
        my_bot.send_text('Welcome to the POLY-vision bot. Send an image or tag an image with /yolo to detect objects.')


    @my_bot.bot.message_handler(commands=['help'])
    def handle_help(message):
        help_text = 'How to use the bot:\n\n' \
                    '/start - Start the bot and get a welcome message\n' \
                    '/help - Get instructions on how to use the bot\n' \
                    '/yolo - Tag an image to detect objects'
        my_bot.send_text(help_text)


    @my_bot.bot.message_handler(commands=['yolo'])
    def handle_yolo(message):
        if message.reply_to_message and message.reply_to_message.photo:
            my_bot.current_msg = message.reply_to_message
            my_bot.handle_message(message.reply_to_message)
        elif message.photo:
            my_bot.current_msg = message
            my_bot.handle_message(message)
        else:
            my_bot.send_text('Please tag an image or send an image for object detection.')



    my_bot.start()
