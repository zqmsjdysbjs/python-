import logging
import requests

from urllib.parse import urljoin
import re

import json
from os import makedirs
from os.path import exists

import multiprocessing

Base_url = 'https://ssr1.scrape.center'
RESULTS_DIR = 'results'
exists(RESULTS_DIR) or makedirs(RESULTS_DIR)
#创建路径名称为results，如果存在则继续使用，不存在则创建

def scrape(url):
    logging.info('scraping %',url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
                return response.text
        else:
            logging.error('爬取%s时 得到无效反应代码:%s',url,response.status_code)
    except requests.RequestException:
        logging.error('在爬取%s出现错误',url,exc_info=True)
#定义一个普遍意义上的抓取
#logging.error负责记录错误, %s表示传入后面的参数, 按顺序传入

def scrape_pages(pages_n):
    global Base_url
    url1 = f'{Base_url}/page/{pages_n}'
    return scrape(url1)
#定义一个列表页的url，使用先前的爬取方法抓取列表页

def info_pages(html):
    pattern1 = re.compile('<a.*?href="(.*?)"\sclass="name"')
    index2s = re.findall(pattern1,html)
    if not index2s:
        logging.warning('No URLs found in HTML content')
    for index in index2s:
        url2 = urljoin(Base_url,index)
        logging.info('get detailed url %s',url2)
        yield url2
    #导出每次爬取响应文本结果为html传入这个函数获得详情页的url
    #yield返回的是一个生成器对象


response = requests.get('https://ssr1.scrape.center/page/1')
html = response.text
pattern = re.compile('<a.*?href="(.*?)"\sclass="name"')
index = re.findall(pattern,html)
for i in index:
    detail_url = urljoin(Base_url,i)
    print(detail_url,sep='\n')

for pages_n in range(1,11):
    url1 = f'{Base_url}/page/{pages_n}'
    print(url1)

def scrape_detail(url):
    return scrape(url)
#单独定义，只爬取详情页的函数

def parse_detail(html):
    cover_p = re.compile('<img.*?src="(.*?)".*?class="cover">', re.S)
    name_p = re.compile('<h2.*?class="m-b-sm">(.*?)</h2></a>', re.S)
    cato_p = re.compile(
        '<button.*?category.*?<span>(.*?)</span>',
        re.S)
    data_p = re.compile('<span.*?>(\d{4}-\d{2}-\d{2})\s上映</span>',re.S)
    drama_p = re.compile('<div.*?drama.*?>.*?<p.*?>(.*?)</p>', re.S)
    score_p = re.compile('<div.*?class="score m-t-md m-b-n-sm">(.*?)</p>',re.S)



    catos = re.findall(cato_p,html) if re.findall(cato_p,html) else []
    names = re.search(name_p,html).group(1).strip() if re.search(name_p,html) else None
    datas = re.search(data_p,html).group(1) if re.search(data_p,html) else None
    scores = float(re.search(score_p,html).group(1)) if re.search(score_p,html) else None
    dramas1 = re.search(drama_p, html).group(1) if re.search(drama_p, html) else None
    dramas = re.sub('[\s\n]','',dramas1)
    covers = re.search(cover_p,html).group(1).strip() if re.search(cover_p, html) else None
    return  {
            "catos":catos,
            'locations':datas,
            'names':names,
            'scores':scores,
            'dramas':dramas,
            'covers':covers
                }

def save_data(data):
    name = data.get('names')
    data_path = f'E:/Desktop/ABC/Scra/SZ/{RESULTS_DIR}/{name}'
    json.dump(data,open(data_path,'w',encoding='utf-8'),ensure_ascii=False,indent=2)


def main(i):
        Index_html = scrape_pages(i)
        Detail_htmls = info_pages(Index_html)
        for i in Detail_htmls:
            d1 = scrape_detail(i)
            data = parse_detail(d1)
            save_data(data)

if __name__ == '__main__':
    pool = multiprocessing.Pool()
    pages = range(1,11)
    pool.map(main,pages)
    pool.close()
    pool.join()














