from yuque.yuque_main import YuQueMain
import os
import yaml


def main():
    yuque = YuQueMain()
    # session.get_repo_list(is_print=True)
    # repo_detail = session.get_repo_detail("icheima/python", is_print=True)
    repo_detail = yuque.get_repo_detail("icheima/th7wl6", is_print=True)
    # 将data/toc_yml保存到repo/toc.yml
    if not os.path.exists("repos"):
        os.mkdir("repos")
    with open("repos/toc1.yml", "w", encoding="utf-8") as f:
        f.write(repo_detail["data"]["toc_yml"])

    # yuque.session.get_repo_docs("icheima/python", is_print=True)
    # yuque.session.get_doc_detail("icheima/python", slug="ow538zuoobsoi2ha", is_print=True)
    # yuque.session.get_doc_detail("icheima/python", slug="pip", is_print=True)

tips = """请先在secret.yaml中, 按照如下格式配置好YUQUE_TOKEN，USER_AGENT，COOKIES
YUQUE_TOKEN: "xxx"
USER_AGENT: "xxx"
COOKIES: "xxx"
"""

TOKEN_FILE = "secret.yaml"
if __name__ == "__main__":
    # check file secret.yaml exists
    if not os.path.exists(TOKEN_FILE):
        print("secret.yaml not found！")
        print(tips)
        exit(0)
    
    
    yuque_token = ""
    user_agent = ""
    cookies = ""
    # load from secret.yaml
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        secret = yaml.load(f, Loader=yaml.FullLoader)
        yuque_token = secret["YUQUE_TOKEN"]
        user_agent = secret["USER_AGENT"]
        if "COOKIES" in secret:
            cookies = secret["COOKIES"]
        
    yuque = YuQueMain(yuque_token, user_agent, cookies)

    # main()
    # -------------------> 保存所有仓库
    # save_all_repos()

    # -------------------> 保存单个仓库
    # yuque.save_repo("icheima/stc8h")
    yuque.save_repo("icheima/python")

    # -------------------> 保存单个文档
    # yuque.save_doc("icheima/python", "dev_pygame_snake")
