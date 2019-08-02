
import requests
import re

def get_page_html(url, cookies=None):
    if not cookies is None:
        r = requests.get(url, cookies=cookies)
    else:
        r = requests.get(url)
    return r.text, r.cookies


def split_crumb_store(v):
    return v.split(':')[2].strip('"')


def find_crumb_store(lines):
    # Looking for
    # ,"CrumbStore":{"crumb":"9q.A4D1c.b9
    for l in lines:
        if re.findall(r'CrumbStore', l):
            return l


def get_cookie_value(r):
    if 'B' in r.cookies:
        return {'B': r.cookies['B']}
    if 'JSESSIONID' in r.cookies:
        return {'JSESSIONID': r.cookies['JSESSIONID']}


def get_page_data(url):
    r = requests.get(url)
    cookie = get_cookie_value(r)

    # Code to replace possible \u002F value
    # ,"CrumbStore":{"crumb":"FWP\u002F5EFll3U"
    # FWP\u002F5EFll3U
    lines = r.content.decode('unicode-escape').strip(). replace('}', '\n')
    return cookie, lines.split('\n')


def get_cookie(url):
    cookie, lines = get_page_data(url)
    return cookie


def get_cookie_crumb(url):
    cookie, lines = get_page_data(url)
    crumb = split_crumb_store(find_crumb_store(lines))
    return cookie, crumb