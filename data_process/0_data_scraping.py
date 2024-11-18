import json

import requests

"""
实验性爬取  https://gongyi.sohu.com/   搜狐公益新闻
"""

"""
    post 请求url https://odin.sohu.com/odin/api/blockdata
    post_data 请求体必要参数 有可能会过期 重要字段 page与size
"""
url = 'https://odin.sohu.com/odin/api/blockdata'
post_data = {
    "mainContent": {
        "productType": "13",
        "productId": "503",
        "secureScore": "50"

    },
    "resourceList": [
        {
            "tplCompKey": "TPLFeedMul_2_9_feedData",

            "configSource": "mp",
            "content": {
                "productId": "501",
                "productType": "13",
                "size": 20,  # 每页给出的新闻数量 实验得最大值为100
                "page": 0,  # 当前页
                "requestId": "1731934160045iGvyWZL_503"
            }
        }
    ]
}
headers = {
    'Content-Type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 '
                  'Safari/537.36',
}
resp = requests.post(url=url, data=json.dumps(post_data), headers=headers)
data = resp.json()['data']['TPLFeedMul_2_9_feedData']['list']  # data是个列表 其中有新闻url 相对路径
