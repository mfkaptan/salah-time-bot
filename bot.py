import sys
import time
import telepot
import urllib


class SalahTimeBot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(SalahTimeBot, self).__init__(*args, **kwargs)
        self.location = {}
        self.START = 'Send /salah for salah times, /restart for reset location'
        self.FORMAT = 'Please send your "country, city" in this format:\n germany, munich'
        self.ERROR = "Couldn't find your country, city!"

    def handle(self, msg):
        flavor = telepot.flavor(msg)
        if flavor != "chat":
            return

        text, chat_id = None, None

        try:
            content_type, chat_type, chat_id = telepot.glance(msg)
            text = msg['text']
        except:
            return
        else:
            if content_type != "text":
                return

        if text == '/start' or text == "/restart":
            bot.sendMessage(chat_id, self.FORMAT)

        elif "," in text:
            country, city = [x.strip() for x in text.split(",")]
            self.location[chat_id] = tuple([country, city])
            bot.sendMessage(chat_id, ('Your location has been saved as ' +
                                      country + ', ' + city))

            show_keyboard = {'keyboard': [['/salah', '/restart']]}
            bot.sendMessage(chat_id, self.START, reply_markup=show_keyboard)

        elif text == "/salah":
            if chat_id in self.location:
                msg = ('Salah times for ' + self.location[chat_id][0] + ', ' +
                       self.location[chat_id][1] +
                       '\nAccording to www.salahtimes.com:')

                bot.sendMessage(chat_id, msg)

            else:
                bot.sendMessage(chat_id, self.FORMAT)
                return

            b = None
            try:
                f = urllib.urlopen(("http://www.salahtimes.com/" +
                                    self.location[chat_id][0] + '/' +
                                    self.location[chat_id][1]))
                b = f.read()
            except:
                bot.sendMessage(chat_id, self.ERROR)
                b = None
            finally:
                f.close()

            if b is not None:
                salah = self.find_between(b, '<tr class="active">', '</tr>')
                salah = self.parse(salah)
                if len(salah) > 0:
                    bot.sendMessage(chat_id, salah)
                else:
                    bot.sendMessage(chat_id, self.ERROR)

        else:
            bot.sendMessage(chat_id, self.FORMAT)

    def find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    def parse(self, salah):
        table = [t.replace("</td>", "").replace("<td>", "").strip() for t in salah.split("\r\n")]
        table = [t for t in table if len(t) > 0]
        if len(table) == 0:
            return ""

        salah = table[0] + " " + table[1] + ":\n"
        times = ["Fajr", "Sunrise", "Zohar", "Asar", "Magrib", "Isha"]

        for t, s in zip(times, table[2:]):
            salah += t + " : " + s + "\n"

        return salah

# Getting the token from command-line is better than embedding it in code,
# because tokens are supposed to be kept secret.
TOKEN = sys.argv[1]

bot = SalahTimeBot(TOKEN)
bot.message_loop()

print 'Listening ...'

# Keep the program running.
while 1:
    time.sleep(10)
