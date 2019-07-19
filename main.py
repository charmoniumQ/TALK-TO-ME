from pathlib import Path
import talk_to_me


fb_data = Path('~/Downloads/facebook-charmoniumq.zip').expanduser()
fb_name = 'Sam Grayson'


exchanges = talk_to_me.fb_data2exchanges(fb_name, fb_data)
exchanges = talk_to_me.exchanges_stats(exchanges, interactive=False)


bot = talk_to_me.Bot()
bot.fit(exchanges)
bot.interact()
