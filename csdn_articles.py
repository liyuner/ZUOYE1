import pdfkit
import requests
import parsel
import time
import random
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: "微软雅黑", SimSun; line-height: 1.8 }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db }}
        img {{ max-width: 100% !important; height: auto !important }}
        pre {{ background: #f5f5f5; padding: 10px }}
        .article {{ margin-bottom: 50px; page-break-after: always }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""


def save_to_pdf(articles, filename="csdn_articles.pdf"):
    try:
        config = pdfkit.configuration(wkhtmltopdf=r'F:\tools\wkhtmltopdf\bin\wkhtmltopdf.exe')

        # 合并所有文章内容
        combined_content = ""
        for article in articles:
            combined_content += f'<div class="article"><h1>{article["title"]}</h1>{article["content"]}</div>'

        html = html_template.format(title="CSDN博客合集", content=combined_content)

        with open('temp.html', 'w', encoding='utf-8') as f:
            f.write(html)

        pdfkit.from_file('temp.html', filename, configuration=config)
        print(f"成功生成PDF：{filename}")
    except Exception as e:
        print(f"PDF生成失败：{str(e)}")


def fetch_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Referer": "https://www.csdn.net/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Upgrade-Insecure-Requests": "1",
        "TE": "trailers"
    }

    try:
        # 创建会话对象
        session = requests.Session()

        # 配置重试策略
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504, 403, 429],
            allowed_methods=["GET"]
        )

        # 挂载适配器
        session.mount('https://', HTTPAdapter(max_retries=retries))
        session.mount('http://', HTTPAdapter(max_retries=retries))

        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        selector = parsel.Selector(response.text)
        title = selector.xpath('//h1[@class="title-article"]/text()').get('').strip()
        content = selector.css('.article_content').get()

        if content:
            # 处理图片链接（确保使用绝对路径）
            content = content.replace('src="//', 'src="https://')
            content = content.replace('src="/', 'src="https://blog.csdn.net/')

            # 移除不需要的元素
            content = content.replace('class="hide-article-box"', 'style="display:none"')

        if not all([title, content]):
            print(f"文章内容获取失败，可能页面结构已更新: {url}")
            return None

        return {'title': title, 'content': content, 'url': url}

    except requests.exceptions.RequestException as e:
        print(f"请求失败：{str(e)} - URL: {url}")
        return None


if __name__ == '__main__':
    # 要爬取的博客URL列表
    target_urls = [
        'https://blog.csdn.net/tiangang2024/article/details/144348740',
        'https://blog.csdn.net/ChailangCompany/article/details/138409237',
        'https://blog.csdn.net/tiangang2024/article/details/144807806',
        'https://blog.csdn.net/shuzaokeji/article/details/140035346',
        'https://blog.csdn.net/weixin_45710998/article/details/145136672',
        'https://blog.csdn.net/shuzaokeji/article/details/141196606'
    ]

    articles = []

    for url in target_urls:
        print(f"正在爬取: {url}")
        article_data = fetch_article(url)
        if article_data:
            articles.append(article_data)
            print(f"成功获取: {article_data['title']}")
        else:
            print(f"获取失败: {url}")

        # 随机延迟，避免被封
        time.sleep(random.uniform(1, 3))

    if articles:
        save_to_pdf(articles, "csdn_data_engineering_articles.pdf")
    else:
        print("没有成功获取任何文章内容")