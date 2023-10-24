from yuque.yuque_main import YuQueMain
import os
import yaml
import sys

from loguru import logger
logger.remove()
logger.add(sink=sys.stdout, level="INFO")

tips = """请先在secret.yaml中, 按照如下格式配置好ACCESS_TOKEN，USER_AGENT，COOKIES
ACCESS_TOKEN: "xxx"
USER_AGENT: "xxx"
COOKIES: "xxx"
"""

TOKEN_FILE = "secret.yaml"


def fill_args():
    access_token = ""
    user_agent = ""
    cookies = ""
    # check file secret.yaml exists
    if not os.path.exists(TOKEN_FILE):
        print("未发现secret.yaml文件,请检查!")
        print(tips)
        exit(0)

    # load from secret.yaml
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        secret = yaml.load(f, Loader=yaml.FullLoader)
        access_token = secret["ACCESS_TOKEN"]
        user_agent = secret["USER_AGENT"]
        if "COOKIES" in secret:
            cookies = secret["COOKIES"]

    if access_token.strip() == "":
        print("未发现ACCESS_TOKEN,请检查!")
        print(tips)
        exit(0)
    if user_agent.strip() == "":
        print("未发现USER_AGENT,请检查!")
        print(tips)
        exit(0)

    return access_token, user_agent, cookies


if __name__ == "__main__":
    
    save_path = ""
    if len(sys.argv) >= 2:
        save_path = sys.argv[1].strip()
    
    access_token, user_agent, cookies = fill_args()

    logger.info(f"ACCESS_TOKEN: {access_token}")
    logger.info(f"USER_AGENT: {user_agent}")

    yuque = YuQueMain(access_token, user_agent, cookies)

    # yuque.save_repo("icheima/stc8h")
    # yuque.save_doc("icheima/python", "dev_pygame_snake", download_pic=True)
    # yuque.save_doc("icheima/python", "intro", download_pic=True)
    if save_path == "" or save_path.count("/") == 0:
        # -------------------> 保存所有仓库
        yuque.save_all_repos()
    elif save_path.count("/") == 1:
        # -------------------> 保存单个仓库
        # yuque.save_repo("icheima/stc8h")
        yuque.save_repo(save_path)
    else:
        # -------------------> 保存单个文档
        # yuque.save_doc("icheima/python", "dev_pygame_snake")
        index = save_path.rfind("/")
        namespace = save_path[0:index]
        slug = save_path[index + 1:]
        yuque.save_doc(namespace, slug)
