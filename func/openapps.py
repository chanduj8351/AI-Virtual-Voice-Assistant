import os
import typing
import requests
import ijson
import re
import json
import webbrowser
from bs4 import BeautifulSoup
import time
from AppOpener import open_app


class AppWebsiteOpener:
    @staticmethod
    def open_apps(app_name: str) -> bool:           ### OPENING LOCAL APPS
        
        try:
            open_app(app_name, output=True, match_closest=True, throw_error=True)
            return True
        except Exception as e:
            print(f"The app '{app_name}' is not available: {e}")
            return False

    @staticmethod
    def find_url_by_app_name(app_name: str,
                        cache_file_path: str = os.getcwd() + "func\\assets\\url_links.json") -> typing.Union[str, None]:
        
        def load_cache():
            if os.path.exists(cache_file_path):
                with open(cache_file_path, 'r') as cache_file:
                    return json.load(cache_file)
            return {}
        
        def save_cache(cache):
            with open(cache_file_path, 'w') as cache_file:
                json.dump(cache, cache_file, indent=4)
        
        def clean_app_name(app_name):
            return re.sub(r'[_\.\*\s]', '', app_name.lower())
        
        def extract_links(html: typing.Union[str, None]) -> typing.List[str]:
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsapp_name': 'UWckNb'})
            return [link.get('href') for link in links]
        
        def search_google(query: str) -> typing.Union[str, None]:
            url = f"https://www.google.com/search?q={query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                return None

        cache = load_cache()
        clean_search_app_name = clean_app_name(app_name)

        if clean_search_app_name in cache:
            return cache[clean_search_app_name]

        html = search_google(app_name)
        print("html: ", html)
        if not html:
            return None
        try:
            links = extract_links(html)
            print(links)
            if links:
                cache[clean_search_app_name] = links[0]
                save_cache(cache)

                return links[0]
            return None
        except:
            return None


    @staticmethod
    def open_website(url: str) -> bool:                     ### OPEN ONLINE WEBSITES
        link = AppWebsiteOpener.find_url_by_app_name(url)
        if link:
            webbrowser.open(link)
            return True
        return False
    

    @staticmethod
    def open_main(app_name: list[str]) -> bool:
        # Enhanced splitting logic
        split_pattern = r'[,&+]| and | or '
        app_names = re.split(split_pattern, app_name.lower())
        results = []
        
        for app in app_names:
            app = app.strip()
            if not app:
                continue
            if AppWebsiteOpener.open_apps(app):
                results.append(True)
                continue
            if AppWebsiteOpener.open_website(app):
                results.append(True)
        
        return any(results)


if __name__ == '__main__':
    st = time.time()
    print('start time:', st)
    AppWebsiteOpener.open_main('claudeai')
    ed = time.time()
    print('end time:', ed)
    print('time elapsed:', ed - st)
