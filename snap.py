#/usr/bin/python
import main as m
import local_settings as l
import telepot


if __name__ == "__main__":
    bot = telepot.Bot(l.telegram['token'])
    m.snap(bot)
