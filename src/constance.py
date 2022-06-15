import os
SCROLL_PAUSE_TIME = int(os.getenv('SCROLL_PAUSE_TIME', 5))
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
IFTTT_URL = os.getenv('IFTTT_URL', 'https://maker.ifttt.com/')
IFTTT_EVENT = os.getenv('IFTTT_EVENT', 'YOUR_EVENT_NAME')
IFTTT_KEY = os.getenv('IFTTT_KEY', 'YOUR_IFTTT_KEY')
DIVAR_URL = os.getenv('DIVAR_URL', 'https://divar.ir/')
