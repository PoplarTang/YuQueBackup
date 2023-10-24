import json
import os
from urllib import parse

import requests
from requests.cookies import RequestsCookieJar

from loguru import logger

class YuQueSession(requests.Session):
    
    URL_BASE = "https://xxx.yuque.com/api/v2"
    
    DOC_BASE_PATH = "https://www.yuque.com"
    
    
    def __init__(self, token, user_agent, cookies=""):
        super().__init__()
        self.URL_BASE = f"https://{user_agent}.yuque.com/api/v2"
        self.COOKIES = cookies
        self.token = token
        self.headers.update({
            "X-Auth-Token": token,
            "User-Agent": user_agent
        })
        self.URL_REPOS = f"/users/{user_agent}/repos"
        # 从浏览器中复制出来的cookies

        self.download_cookies = {}
        for cookie in self.COOKIES.split(';'):
            index = cookie.find("=")
            self.download_cookies[cookie[:index]] = cookie[index + 1:]

        self.allowed_url_hosts = [
            "www.yuque.com",
            "cdn.nlark.com",
            "yuque.com",
        ]
        
        # 确保docs，repos目录存在
        if not os.path.exists("docs"):
            os.mkdir("docs")
        if not os.path.exists("repos"):
            os.mkdir("repos")

    def get_repo_list(self, is_print=False):
        """
        获取知识库列表
        :return:
        """
        url = self.URL_BASE + self.URL_REPOS
        resp = self.get(url)
        if resp.status_code != 200:
            print("url: %s" % url)
            raise Exception("get repo list failed, status_code: %s" % resp.status_code)

        if is_print:
            # 将内容以良好的Json格式进行打印
            print(json.dumps(resp.json(), indent=4, ensure_ascii=False))

        return resp.json()

    def get_repo_detail(self, namespace, repo_type="Book", is_print=False):
        """
        获取知识库详情
        :param namespace: 仓库名称，如：/repos/icheima/python
        :param repo_type: 仓库类型 Book文库, Design设计稿
        :return:
        """
        # 将如下路径合理拼接，self.URL_BASE, /repos/ icheima/python
        url = parse.urljoin(self.URL_BASE + "/repos/", namespace)
        resp = self.get(url, params={"type": repo_type})
        if resp.status_code != 200:
            raise Exception("get repo detail failed, status_code: %s" % resp.status_code)

        if is_print:
            # 将内容以良好的Json格式进行打印
            print(json.dumps(resp.json(), indent=4, ensure_ascii=False))

        return resp.json()

    def get_repo_docs(self, namespace, repo_type="Book", is_print=False):
        """
        获取知识库详情
        :param namespace: 仓库名称，如：/repos/icheima/python
        :param repo_type: 仓库类型 Book文库, Design设计稿
        :return:
        """
        # 将如下路径合理拼接，self.URL_BASE, /repos/ icheima/python
        url = parse.urljoin(self.URL_BASE + "/repos/", namespace + "/docs")
        resp = self.get(url)
        if resp.status_code != 200:
            raise Exception("get repo detail failed, status_code: %s" % resp.status_code)

        if is_print:
            # 将内容以良好的Json格式进行打印
            print(json.dumps(resp.json(), indent=4, ensure_ascii=False))

        return resp.json()

    def get_doc_detail(self, namespace, slug, is_print=False):
        """
        获取文档详情
        :param slug:
        :return:
        """
        # 将如下路径合理拼接，self.URL_BASE, /repos/ icheima/python /docs/ ow538zuoobsoi2ha
        url = parse.urljoin(self.URL_BASE + "/repos/", namespace + "/docs/" + slug)
        resp = self.get(url, params={"raw": 1})  # raw raw=1 返回文档最原始的格式
        if resp.status_code != 200:
            doc_path = f"{self.DOC_BASE_PATH}/{namespace}/{slug}"
            logger.error(f"获取文档详情失败, 请检查以下链接是否可打开：\n{doc_path}")
            raise Exception("获取文档详情失败，状态码: %s" % resp.status_code)

        # 将内容以良好的Json格式进行打印
        resp_json = resp.json()

        if is_print:
            print(json.dumps(resp_json, indent=4, ensure_ascii=False))

        # 按照docs/doc.json将data/body下的内容保存到docs/doc.md
        with open("docs/doc.md", "w", encoding="utf-8") as f:
            f.write(resp_json["data"]["body"])

        # 按照docs/doc.json将data/body_html下的内容保存到docs/doc.html
        with open("docs/doc.html", "w", encoding="utf-8") as f:
            f.write(resp_json["data"]["body_html"])

        return resp_json

    def download(self, url: str, file_path: str) -> bool:
        """下载文件

        Args:
            url (str): 文件下载路径
            file_path (str): 文件保存路径

        Returns:
            bool: 保存成功
        """
        # 判断url是否合法， 仅允许下载域名为self.allowed_url_hosts中的内容
        no_head_url = url[url.find("//") + 2:]
        if not any([no_head_url.startswith(host) for host in self.allowed_url_hosts]):
            return False

        # 如果没有self.download_cookies， 则返回
        if not self.download_cookies or len(self.download_cookies) == 0:
            print("没有COOKIES 无法下载文件")
            return False

        try:
            r = requests.get(url, cookies=self.download_cookies, stream=True, allow_redirects=True)
            if r.status_code != 200:
                return False

            # 创建父级目录
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 保存文件
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        f.flush()
            return True
        except Exception as e:
            print(e)

        return False
