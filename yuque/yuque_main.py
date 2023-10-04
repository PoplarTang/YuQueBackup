

import os.path

import yaml

import utils.regex_util as regex_util
from utils.worker import Worker
from yuque.yuque_service import YuQueSession

repo_about_template = """# {}

## 基本信息
- id: `{}`
- type: `{}`
- slug: `{}`
- namespace: `{}`
- created_at: `{}`
- updated_at: `{}`

## 描述
{}
"""

doc_about_template = """# {}
## 基本信息
- id: `{}`
- slug: `{}`
- namespace: `{}`
- created_at: `{}`
- updated_at: `{}`

## 描述
{}
"""
folder_name_template = "{}.[{}]_{}"

docs_folder_dict = {}


def normalize_file_path(repo_name: str):
    repo_name = repo_name.replace(" ", "")
    repo_name = repo_name.strip()
    repo_name = repo_name.replace("/", "_")  # 将/替换成_
    repo_name = repo_name.replace("\\", "_")  # 将\替换成_
    return repo_name


class YuQueMain:
    
    def __init__(self, yuque_token, user_agent, cookies=""):
        self.session = YuQueSession(yuque_token, user_agent, cookies)

    def save_repo(self, namespace):
        repo_detail = self.session.get_repo_detail(namespace)  # --------------> 获取仓库详情
        repo_data = repo_detail["data"]

        # 根据data.name创建目录，放到repos目录下
        repo_name = normalize_file_path(repo_data["name"])

        repo_path = os.path.join("repos", repo_name)
        if not os.path.exists(repo_path):
            # 递归创建repo_path
            os.makedirs(repo_path)

        # 将data.toc_yml保存到repo_path/toc.yml
        with open(os.path.join(repo_path, "toc.yml"), "w", encoding="utf-8") as f:
            f.write(repo_data["toc_yml"])

        # 新建about.md文件
        with open(os.path.join(repo_path, "about.md"), "w", encoding="utf-8") as f:
            f.write(repo_about_template.format(repo_data["name"],
                                            repo_data["id"], repo_data["type"], repo_data["slug"],
                                            repo_data["namespace"], repo_data["created_at"], repo_data["updated_at"],
                                            repo_data["description"]))

        # 根据repo_data["toc_yml"]结构，创建目录结构
        repo_toc = repo_data["toc_yml"]
        repo_toc_yml = yaml.safe_load(repo_toc)
        self.create_directories(repo_toc_yml, "", repo_path)

        # 获取仓库文档列表
        docs_list = self.session.get_repo_docs(namespace)
        docs_list_data = docs_list["data"]
        for doc in docs_list_data:
            # id, slug, title
            doc_id, slug, title = doc["id"], doc["slug"], doc["title"]
            # doc_detail = self.session.get_doc_detail(namespace, slug)
            # 根据doc_id获取save_path
            save_path = None
            if doc_id in docs_folder_dict:
                save_path = docs_folder_dict[doc_id]
            self.save_doc(namespace, slug, save_path)

        print("仓库保存成功：", repo_name)

        return repo_path



    @staticmethod
    def create_directories(repo_data, parent_uuid, parent_path):
        # 过滤出parent_uuid的子目录
        items = [item for item in repo_data if "parent_uuid" in item and item["parent_uuid"] == parent_uuid]
        for index, item in enumerate(items):
            item_type, title, uuid = item["type"], item["title"], item["uuid"]
            # 将index前面补0，保证排序时按照index正常排序
            index_str = str(index).zfill(2)
            title_norm = normalize_file_path(title)
            folder_name = folder_name_template.format(index_str, item_type, title_norm)
            # 创建目录
            folder_path = os.path.join(parent_path, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # 如果是个DOC类型，则将其路径缓存起来，key为doc_id，value为folder_path
            if item_type == "DOC":
                doc_id = item["doc_id"]
                docs_folder_dict[doc_id] = folder_path

            # 递归创建子目录
            YuQueMain.create_directories(repo_data, uuid, folder_path)


    def save_all_repos(self):
        worker = Worker()
        repo_list = self.session.get_repo_list()  # -------------------> 获取仓库列表
        for repo in repo_list["data"]:
            name, namespace, description = repo["name"], repo["namespace"], repo["description"]
            if "临时" in name:
                print("--> 跳过：", name, namespace, description)
                continue

            print(name, namespace, description)

            worker.start_pool(self.save_repo, args=(namespace,))

        print("所有仓库保存成功")

            # 根据详情repo_detail里的data/toc_yml进行分文件夹存储
            # docs = self.session.get_repo_docs(namespace)  # ------------> 获取仓库文档列表
            # for doc in docs["data"]:
            #     slug, title, description = doc["slug"], doc["title"], doc["description"]
            #     print("\t->", slug, title)
            #     self.session.get_doc_detail(namespace, slug) # --------> 获取文档详情

        # self.session.get_repo_detail("icheima/python")
        # self.session.get_repo_docs("icheima/python")
        # self.session.get_doc_detail("icheima/python", slug="ow538zuoobsoi2ha")
        # self.session.get_doc_detail("icheima/python", slug="pip")


    def download_file(self, url, file_path):
        """
        使用requests下载文件, 将url下载到file_path
        :param url:  远程文件地址
        :param file_path:  本地文件路径
        :return: 是否下载成功
        """
        return self.session.download(url, file_path)



    def save_doc(self, namespace, slug, save_path=None, download_pic=False):
        """根据namespace和slug获取文档详情，并保存到本地

        :param namespace: 命名空间
        :param slug: 子空间
        :param save_path: _description_, defaults to None
        :param download_pic: _description_, defaults to False
        """
        doc_detail = self.session.get_doc_detail(namespace, slug)
        data = doc_detail["data"]
        # id, slug, title
        id, slug, title = data["id"], data["slug"], data["title"]
        new_title = normalize_file_path(title)
        if save_path is None:
            save_path = os.path.join("docs", new_title)

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # about: created_at、updated_at、description
        created_at, updated_at, description = data["created_at"], data["updated_at"], data["description"]
        with open(os.path.join(save_path, "about.md"), "w", encoding="utf-8") as f:
            template_format = doc_about_template.format(
                title, id, slug, namespace, created_at, updated_at, description
            )
            f.write(template_format)

        # md: body
        body = data["body"]
        with open(os.path.join(save_path, f"{new_title}.md"), "w", encoding="utf-8") as f:
            f.write(body)

        # 下载其中的图片和文件 ----------------------------------------------------
        if download_pic:
            url_list = regex_util.find_url(body)
            # 下载url_list中的图片和文件到save_path/res目录下
            for url, filename in url_list:
                # 下载文件
                file_path = os.path.join(save_path, "res", filename)
                if os.path.exists(file_path):
                    continue
            
                self.download_file(url, file_path)


        # html body_html
        # body_html = data["body_html"]
        # with open(os.path.join(save_path, f"{new_title}.html"), "w", encoding="utf-8") as f:
        #     f.write(body_html)

        print("\t-> DOC保存成功：", save_path)
