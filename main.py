from yuque.yuque_main import YuQueMain
import os
import yaml
import sys

tips = """请先在secret.yaml中, 按照如下格式配置好YUQUE_TOKEN，USER_AGENT，COOKIES
YUQUE_TOKEN: "xxx"
USER_AGENT: "xxx"
COOKIES: "xxx"
"""

TOKEN_FILE = "secret.yaml"


def fill_args():
    yuque_token = ""
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
        yuque_token = secret["YUQUE_TOKEN"]
        user_agent = secret["USER_AGENT"]
        if "COOKIES" in secret:
            cookies = secret["COOKIES"]

    if yuque_token.strip() == "":
        print("未发现YUQUE_TOKEN,请检查!")
        print(tips)
        exit(0)
    if user_agent.strip() == "":
        print("未发现USER_AGENT,请检查!")
        print(tips)
        exit(0)

    return yuque_token, user_agent, cookies


if __name__ == "__main__":
    
    save_path = ""
    if len(sys.argv) >= 2:
        save_path = sys.argv[1].strip()
    
    yuque_token, user_agent, cookies = fill_args()

    yuque = YuQueMain(yuque_token, user_agent, cookies)

    if save_path == "":
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
