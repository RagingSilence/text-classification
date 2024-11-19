import json
import os
from datetime import datetime

import requests
import pandas as pd
from src.utils.Logger import Logger
from src.utils.data_input import get_path

"""
实验性爬取   搜狐新闻
先尝试爬取公益新闻
"""

"""
    post 请求url https://odin.sohu.com/odin/api/blockdata
    post_data 请求体必要参数 有可能会过期 重要字段 productId page与size
"""

"""
    后续 1.可手动获取不同类别的productId与productId {https://www.sohu.com/ 查找需要的类别}
        2.对data中的url进行爬取
"""


class NewsCategory:

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
            NewsCategory('公益新闻', 13, 501),
            NewsCategory('教育新闻', 13, 665),
            NewsCategory('国内军事', 13, 2027),
            NewsCategory('体育新闻', 13, 1202),
            NewsCategory('健康', 13, 1595),
            NewsCategory('游戏', 15, 56210),
            NewsCategory('科技', 15, 54822),
            NewsCategory('美食', 13, 2096),
            NewsCategory('历史', 13, 396),
            NewsCategory('政务', 13, 502),
        ]


class RequestData:
    DEFAULT_PAGE_SIZE = 1000

    @staticmethod
    def get_tplCompKey():
        return 'TPLFeedMul_2_9_feedData'

    @staticmethod
    def get_post_data(category: NewsCategory, page: int = 0, size: int = DEFAULT_PAGE_SIZE):
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


def download():
    for category in NewsCategory.get_default_categories():
        urls = get_urls(category)
        df = pd.DataFrame(urls)
        path = os.path.join(get_path(), datetime.now().strftime('%m-%d-%H-%M'))
        if not os.path.exists(path):
            os.makedirs(path)
        df.to_csv(os.path.join(path, str(category) + '.csv'), index=False)


def get_urls(category: NewsCategory, item_nums: int = 1000):
    """
    爬取当前类别的url 不同类别爬取的条数有不同限制 可分多天爬取
    :param category: 类别
    :param item_nums: 爬取的最大数量 初步测试，网站后端最多返回300条以内的数据
    :return: 新闻url列表
    """

    resp = requests.post(url=RequestData.get_post_url(), data=RequestData.get_post_json_data(category),
                         headers=RequestData.get_headers())
    urls = [ele['url'] for ele in resp.json()['data'][RequestData.get_tplCompKey()]['list']]
    Logger.log(category, len(urls))
    return urls
    # while len(urls) < item_nums:
    #     # 保存urls_post结果
    #     urls_p = urls_post(category, len(urls) // RequestData.DEFAULT_PAGE_SIZE)
    #     if urls_p is None:
    #         break
    #     urls += urls_p
    #     Logger.log(category, len(urls))
    # print(len(set(urls)))


# def urls_post(category: NewsCategory, page: int):
#     """
#     发送请求 对含有urls的响应体进行解析获得url列表
#     :param category: 类别
#     :param page: 页码
#     :return:
#     """
#     resp = requests.post(url=RequestData.get_post_url(), data=RequestData.get_post_json_data(category, page),
#                          headers=RequestData.get_headers())
#     resp_json = resp.json()['data'][RequestData.get_tplCompKey()]
#     if resp_json is None or resp_json['list'] is None:
#         return None
#     return [ele['url'] for ele in resp_json['list']]


if __name__ == '__main__':
    # get_urls(NewsCategory.get_default_categories()[0])
    # path = [get_path(), datetime.now().strftime('%m-%d-%H-%M'), str(NewsCategory.get_default_categories()[0]) + '.csv']
    # print(path)
    # print(os.path.join(*path))
    download()
