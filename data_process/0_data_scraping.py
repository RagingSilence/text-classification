import asyncio
import json
import os
from collections import defaultdict
from datetime import datetime
from aiohttp import ClientSession
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

from src.utils.Logger import Logger
from src.utils.data_input import get_path

"""
爬取搜狐新闻
"""


class NewsCategory:
    """
    新闻类 用于爬取不同种类的新闻
    """

    def __init__(self, product_name: str, product_type: int, product_id: int):
        """
            :param product_name 新闻分类名称
            :param product_type 新闻类型    抓包获得
            :param product_id   新闻id    抓包获得

        """
        self.name = product_name
        self.id = product_id
        self.type = product_type

    def __str__(self):
        return self.name

    @staticmethod
    def get_default_categories():
        return [
            NewsCategory('公益', 13, 501),
            NewsCategory('教育', 13, 665),
            NewsCategory('国内军事', 13, 2027),
            NewsCategory('体育', 13, 1202),
            NewsCategory('健康', 13, 1595),
            NewsCategory('游戏', 15, 56210),
            NewsCategory('科技', 15, 54822),
            NewsCategory('美食', 13, 2096),
            NewsCategory('历史', 13, 396),
            NewsCategory('政务', 13, 502),
            NewsCategory('房产', 13, 7238),
            NewsCategory('财经', 15, 54401),
            NewsCategory('旅游', 13, 2079),
        ]


class RequestData:
    """
        发送request需要的Data
    """
    DEFAULT_PAGE_SIZE = 1000

    @staticmethod
    def get_tplCompKey():
        return 'TPLFeedMul_2_9_feedData'

    @staticmethod
    def get_post_data(category: NewsCategory, page: int = 0, size: int = DEFAULT_PAGE_SIZE):
        """
        获取新闻urls列表时需要的post_data
        一般搜狐能爬取的urls数量会在300以内 可以只post一次获取所有数据
        :param category: 新闻类
        :param page: 页码
        :param size: 新闻条数
        :return: urls post请求体
        """
        return {
            "mainContent": {
                "productType": "13",  # 默认
                "productId": "503",  # 不重要 随便填
                "secureScore": "50"  # 默认
            },
            "resourceList": [
                {
                    "tplCompKey": RequestData.get_tplCompKey(),  # 不重要 随便填后面获取数据时保持一致即可
                    "content": {
                        "productId": category.id,
                        "productType": category.type,  # 默认 与id匹配
                        "size": size,  # 每页给出的新闻数量 实验得最大值为100
                        "page": page,  # 当前页
                        "requestId": "1731934160045iGvyWZL_503"  # 不重要 随便填
                    }
                }
            ]
        }

    @staticmethod
    def get_post_json_data(category: NewsCategory, page: int = 0, size: int = DEFAULT_PAGE_SIZE):
        return json.dumps(RequestData.get_post_data(category, page, size))

    @staticmethod
    def get_headers():
        return {
            'Content-Type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 '
                          'Safari/537.36',
        }

    @staticmethod
    def get_post_url():
        return 'https://odin.sohu.com/odin/api/blockdata'

    @staticmethod
    def get_page_url():
        return 'https://www.sohu.com'


def get_url_base_path():
    return os.path.join(get_path(), 'urls')


def get_news_base_path():
    return os.path.join(get_path(), 'news')


def get_time_now():
    return datetime.now().strftime('%m-%d-%H-%M')


def urls_download():
    """
    爬取各种类别新闻的urls列表并保存在data文件夹下
    """
    cnt = 0
    for category in NewsCategory.get_default_categories():
        urls = get_urls(category)
        df = pd.DataFrame(urls)
        path = os.path.join(get_url_base_path(), get_time_now())
        if not os.path.exists(path):
            os.makedirs(path)
        df.to_csv(path_or_buf=os.path.join(path, str(category) + '.csv'), index=False)
        cnt += df.shape[0]
    Logger.log(f'共写入{cnt}条url')


def get_urls(category: NewsCategory, item_nums: int = RequestData.DEFAULT_PAGE_SIZE):
    """
    爬取当前类别的url 不同类别爬取的条数有不同限制 可每天爬一次
    :param category: 类别
    :param item_nums: 爬取的最大数量 初步测试，网站后端最多返回300条以内的数据
    :return: 新闻url列表
    """
    resp = requests.post(url=RequestData.get_post_url(), data=RequestData.get_post_json_data(category, size=item_nums),
                         headers=RequestData.get_headers())
    urls = [ele['url'] for ele in resp.json()['data'][RequestData.get_tplCompKey()]['list']]
    Logger.log(category, 'urls数量：', len(urls))
    return urls


def urls_merge() -> dict:
    """
    将urls文件夹下各个分类下得url进行合并去重
    :return: key为新闻种类 value为合并去重后的urls列表
    """
    record = defaultdict(list)
    for entry in os.listdir(get_url_base_path()):
        full_path = os.path.join(get_url_base_path(), entry)
        if os.path.isdir(full_path):
            for file_name in os.listdir(full_path):
                record[file_name.split('.')[0]].append(pd.read_csv(os.path.join(full_path, file_name)))
    for k, v in record.items():
        df = pd.concat(v)
        t = df.shape[0]
        v = pd.concat(v).iloc[:, 0].unique().tolist()
        Logger.log(f'{k}\t合并前：{t}条，合并后：{len(v)}条')
    return record


async def fetch(url, session):
    async with session.get(url) as response:
        txt = await response.text()
        return html_to_content(txt)


def html_to_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    p_tags = soup.find_all('p')
    # 遍历所有p标签并输出只包含文本的p标签的内容
    content = ''
    for p in p_tags:
        content += p.get_text(strip=True)

    return content


async def write_news_to_file(path, contents, lock):
    """
    写入新闻
    :param path: 写入文件路径
    :param contents: 新闻列表
    :param lock: 每个batch爬取完需同步写入一次
    :return:
    """
    async with lock:
        with open(path, 'a', encoding='utf-8') as file:
            for content in contents:
                file.write(content + "\n")


async def process_batch(path: str, tasks, batch_size, pbar):
    lock = asyncio.Lock()
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        contents = await asyncio.gather(*batch)
        await write_news_to_file(path, contents, lock)
        pbar.update(len(contents))


async def news_download(batch_size=100):
    """
    并发爬取urls列表新闻
    每个种类的新闻每次爬取batch_size条新闻
    写入文件后 每一行代表一条新闻
    :param batch_size 并发数量 可适当增大
    :return:
    """
    # key: 新闻种类 value: urls列表
    total_tasks = []
    urls_dict = urls_merge()
    # 创建保存路径
    folder_path = os.path.join(get_news_base_path(), get_time_now())
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    pbar = tqdm(total=sum(len(urls) for urls in urls_dict.values()), desc=f"Processing", unit="url")
    async with ClientSession(headers=RequestData.get_headers()) as session:
        for category, urls in urls_dict.items():
            tasks = [fetch(RequestData.get_page_url() + url, session) for url in urls]
            path = os.path.join(folder_path, category + '.txt')
            total_tasks.append(process_batch(path, tasks, batch_size, pbar))
        await asyncio.gather(*total_tasks)
    pbar.close()


if __name__ == '__main__':
    # 爬取urls
    # urls_download()
    # 爬取新闻
    asyncio.run(news_download())
