import re
import requests

# 匹配 [text](url) 结构的URL模式
URL_PATTERN = r'\[.*?\]\((https?://\S+)\)'


def find_url(text):
    rst_list = []
    # 查找匹配的URL链接
    urls = re.findall(URL_PATTERN, text)
    # 打印提取的URL链接
    for url in urls:
        # 取出url中的文件名
        filename = url.split('/')[-1]
        # 截取?号前面的内容
        filename = filename.split('?')[0]
        # 截取#号前面的内容
        filename = filename.split('#')[0]
        rst_list.append((url, filename))
    return rst_list


COOKIES = ""
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}


def download_url(url, filename):
    try:
        cookies = {}
        for cookie in COOKIES.split(';'):
            index = cookie.find("=")
            cookies[cookie[:index]] = cookie[index + 1:]

        resp = requests.get(url, cookies=cookies, headers=headers, stream=True, allow_redirects=True)
        # 打印其重定向的URL

        if resp.history:
            print("Request was redirected")
            for redirect in resp.history:
                print("Redirected from:", redirect.url)
            print("Final URL:", resp.url)
        else:
            print("Request was not redirected")

        with open(filename, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(e)
    return False


def test2():
    download_url(
        "https://www.yuque.com/attachments/yuque/0/2023/zip/27903758/1685414484659-2d734034-de41-4aac-a476-7a2c0d2d301e.zip",
        "img.zip")


def test1():
    text = """
    ![image.png](https://cdn.nlark.com/yuque/0/2023/png/27903758/1685414420230-640a3351-5f34-4fb9-a132-2ddf5aeb3fb8.png#averageHue=%23a1cc56&clientId=ub6c62449-a61f-4&from=paste&height=511&id=u7534342a&originHeight=511&originWidth=640&originalType=binary&ratio=1&rotation=0&showTitle=false&size=52135&status=done&style=none&taskId=u268051ce-9c7b-4fb7-8ee7-1e0bc48816e&title=&width=640)
    [img.zip](https://www.yuque.com/attachments/yuque/0/2023/zip/27903758/1685414484659-2d734034-de41-4aac-a476-7a2c0d2d301e.zip)
    """
    rst_list = find_url(text)
    for url, filename in rst_list:
        print(filename, "->", url)


if __name__ == '__main__':
    # test1()
    test2()
