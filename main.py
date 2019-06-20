from pathlib import Path
from tqdm import tqdm
import talk_to_me


fb_data = Path('~/Downloads/facebook-charmoniumq.zip').expanduser()
fb_name = 'Sam Grayson'
exchanges = list(tqdm(talk_to_me.fb_data2exchanges(fb_name, fb_data), desc='load data'))
talk_to_me.exchanges_stats(exchanges)
# bot = talk_to_me.Bot()
# bot.fit(exchanges)
# try:
#     while True:
#         print(words2sentence(bot.transform(input())))
# except EOFError:
#     pass
