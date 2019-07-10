#/usr/bin/python
import main as m
import time
import telepot
import local_settings as l


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        bot.sendMessage(chat_id, 'Is there anyone there?')
        m.snap(bot)

if __name__ == "__main__":
    bot = telepot.Bot(l.telegram['token'])
    bot.message_loop(handle)

    # Keep the program running.
    while 1:
        time.sleep(10)
