import json, dotenv, base64, requests, os
from setproctitle import setproctitle
from telegram_utils import OpenCTMConverterTelegramBot

# Read the 2024-12-20_00058-001.html file.
# There's a <script> which has a DentalWebGL.m_Data object in JSON format.
# Parse the JSON in python and save the "data" field of the JSON as a .ctm file, after bse64-decoding it.

    
PROC_TITLE = 'exocad2stlbot_proc'
setproctitle(PROC_TITLE)
BASE_PATH="/home/gianfry/Documents/exocad2stl"

if __name__ == '__main__':
    
    dotenv.load_dotenv(os.path.join(BASE_PATH, ".env"))
    
    BOT_TOKEN = os.getenv("TELEGRAM_EXOCAD_BOT_TOKEN")            
    OpenCTMConverterTelegramBot(BOT_TOKEN, BASE_PATH)
    
