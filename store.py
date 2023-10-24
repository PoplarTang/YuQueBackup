import yaml
import os
from loguru import logger
TOKEN_FILE = "secret.yaml"

def save_config(access_token, user_agent, download_pic=False):
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        data = {
            "ACCESS_TOKEN": access_token, 
            "USER_AGENT": user_agent,
            "DOWNLOAD_PIC": download_pic,
        }
        yaml.dump(data, f)

def load_config():
    access_token = None
    user_agent = None
    download_pic = False
    if not os.path.exists(TOKEN_FILE):
        return access_token, user_agent, download_pic
    
    # load from secret.yaml
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            secret: dict = yaml.load(f, Loader=yaml.FullLoader)
            access_token = secret.get("ACCESS_TOKEN", None)
            user_agent = secret.get("USER_AGENT", None)
            download_pic = secret.get("DOWNLOAD_PIC", False)
    except Exception as e:
        logger.error(e)
        
    return access_token, user_agent, download_pic