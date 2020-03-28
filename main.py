import pickle
import sys
from pathlib import Path
import talk_to_me


fb_data = Path(sys.argv[1]).expanduser()
fb_name = sys.argv[2]

exchanges = talk_to_me.fb_data2exchanges(fb_name, fb_data)
# with open('exchanges.pickle', 'wb') as f:
#     pickle.dump(list(exchanges), f)
# with open('exchanges.pickle', 'rb') as f:
#     exchanges = pickle.load(f)
exchanges = talk_to_me.exchanges_stats(exchanges, interactive=True)


# bot = talk_to_me.Bot()
# bot.fit(exchanges)
# bot.interact()
