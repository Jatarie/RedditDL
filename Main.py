import requests
import argparse
import os
import re

parser = argparse.ArgumentParser(description="Download images from reddit")
parser.add_argument('subreddit', metavar='N', type=str)
parser.add_argument('limit', metavar='R', type=int)
args = parser.parse_args()


class Post:
    def __init__(self, link, subreddit, reddit_id, name):
        self.subreddit = subreddit
        self.reddit_id = reddit_id
        self.link = link
        self.name = name
        self.extension = ""
        self.final_url = None
        self.album_list = None
        self.album_extensions = []


class UrlHandler:
    @staticmethod
    def get_posts(subreddit, limit=100, time="all"):
        url = 'https://api.reddit.com/r/{}/top?t={}&limit={}'.format(subreddit, time, limit)
        posts = []
        while limit > 0:
            r = requests.get(url, headers={"user-agent": "nothing-interesting"}).json()
            posts += [Post(
                r["data"]["children"][i]["data"]["url"],
                r["data"]["children"][i]["data"]["subreddit"],
                r["data"]["children"][i]["data"]["id"],
                r["data"]["children"][i]["data"]["name"]
            )
                for i in range(len(r["data"]["children"]))]
            url = 'https://api.reddit.com/r/{}/top?t={}&limit={}&after={}'.format(subreddit, time, limit,
                                                                                  posts[-1].name)
            limit -= 100
        return posts

    @staticmethod
    def progress(posts):
        number = 0
        demon = 0
        for i in posts:
            if i.final_url != None:
                number += 1
            else:
                print(i.link)
            demon += 1
        print("{}/{}".format(number, demon))

    @staticmethod
    def filter(posts):
        for index, i in enumerate(posts):
            try:
                x = re.findall(r'(.png|.jpeg|.jpg|.mp4|.gif)$', i.link)[0]
                i.final_url = i.link
            except (IndexError, KeyError):
                try:
                    if "imgur" in i.link:
                        i.final_url = UrlHandler.imgur(i)
                except (IndexError, KeyError):
                    pass
                try:
                    if "gfycat" in i.link:
                        i.final_url = UrlHandler.gfycat(i)
                except KeyError:
                    pass
        return posts

    @staticmethod
    def imgur(post):
        try:
            x = re.findall(r'[0-9a-zA-Z]{6,}', post.link)[0]
        except IndexError:
            pass
        client_id = "9b80ec93de0f36b"
        if "gallery" not in post.link and "/a/" not in post.link:
            r = requests.get("https://api.imgur.com/3/image/{}?client_id={}".format(x, client_id)).json()
            if "gifv" in post.link:
                return r["data"]["mp4"]
            return r["data"]["link"]
        if "/a/" in post.link:
            x = re.findall(r'(?<=/a/).+$', post.link)[0]
            r = requests.get("https://api.imgur.com/3/album/{}/images?client_id={}".format(x, client_id)).json()
            post.album_list = [r["data"][i]["link"] for i in range(len(r["data"]))]
            return "Album"

    @staticmethod
    def gfycat(post):
        x = re.findall(r'(?<=gfycat\.com/)[a-zA-Z0-9]+', post.link)[0]
        r = requests.get("https://api.gfycat.com/v1/gfycats/{}".format(x)).json()
        return r["gfyItem"]["mp4Url"]

    @staticmethod
    def extensions(posts):
        for post in posts:
            if post.album_list is not None:
                for link in post.album_list:
                    x = re.findall(r'\.[0-9a-zA-Z]{,4}$', link)
                    post.album_extensions.append(x[0])

            try:
                x = re.findall(r'\.[0-9a-zA-Z]{,4}$', post.final_url)
                post.extension = x[0]
            except:
                pass
        return posts


class LinkDownloader:

    @staticmethod
    def download(posts):
        counter = 1
        for post in posts:
            print("{} - {}".format(post.link, post.final_url))
            try:
                try:
                    os.mkdir("D:\\porn\\reddit\\{}".format(post.subreddit))
                except FileExistsError:
                    pass
                if post.final_url == "Album":
                    print(post.album_list)
                    for index, url in enumerate(post.album_list):
                        print(url)
                        LinkDownloader.get_url(post, url, counter, post.album_extensions[index])
                        counter += 1
                else:
                    LinkDownloader.get_url(post, post.final_url, counter, post.extension)
                    counter += 1
            except:
                pass

    @staticmethod
    def get_url(post, url, counter, extension):
        r = requests.get(url)
        with open("D:\porn\\reddit\{}\{}{}".format(post.subreddit, counter, extension), "wb") as f:
            for chunk in r.iter_content(chunk_size=255):
                if chunk:
                    f.write(chunk)


posts = UrlHandler.get_posts(vars(args)["subreddit"], vars(args)["limit"])
posts = UrlHandler.filter(posts)
posts = UrlHandler.extensions(posts)
UrlHandler.progress(posts)
LinkDownloader.download(posts)

