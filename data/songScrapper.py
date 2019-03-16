import urllib.request as urllib2
from bs4 import BeautifulSoup
import pandas as pd
import re
from unidecode import unidecode
class songScrapper(object):
    def __init__(self, baseurl=None, dynamicurl=None, trailerurl=None):
        self.base_url = baseurl
        if dynamicurl is None:
            print("No dynamic list provided and trailer url will be ignored")
            self.dynamic_list, self.trailer_url = "", ""
        else:
            self.dynamic_list = dynamicurl
            if trailerurl is None:
                print("No trailer url provided")
                self.trailer_url = ""
            else:
                self.trailer_url = trailerurl

    def construct_url(self):
        if type(self.dynamic_list) is list:
            url_level_1 = [self.base_url + dy + self.trailer_url for dy in self.dynamic_list]
            return url_level_1
        elif type(self.dynamic_list) is str:
            url_level_1 = [self.base_url + self.dynamic_list + self.trailer_url]
            return url_level_1
    
    def get_soup(self, url):
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        return soup
    
    def run(self):
        url_level_1 = self.construct_url()
        df = pd.DataFrame(None,columns=["title","lyrics"])
        count = 0
        for url in url_level_1:
            soup_1 = self.get_soup(url)
            # check for single or multiple page
            multipage_check = soup_1.find_all("p", attrs={"class","pagination"})
            if len(multipage_check) == 1:
                do_while_loop = True
                nextpage_check = soup_1.find_all("a", attrs={"class","button next"})
                while do_while_loop:
                    url_level_2 = nextpage_check[0]["href"]
                    soup_2 = self.get_soup(url_level_2)
                    # get song url
                    for a in soup_2.find_all("a",attrs={"class":"title"}):
                        if "target" not in a.attrs:
                            url_level_3 = a.attrs["href"]
                            title = a.attrs["title"]
                            soup_3 = self.get_soup(url_level_3)
                            verses_check = soup_3.find_all('p', attrs={'class': 'verse'})
                            if len(verses_check) == 0:
                                print("skipping** ", title)
                                continue
                            else:
                                print(title) 
                                lyrics = ''
                                for verse in verses_check:
                                    text = verse.text.strip()
                                    text = re.sub(r"\[.*\]\n", "", unidecode(text))
                                    if lyrics == '':
                                        lyrics = lyrics + text.replace('\n', '|-|')
                                    else:
                                        lyrics = lyrics + '|-|' + text.replace('\n', '|-|')
                                df.loc[count]=[title,lyrics]
                                count += 1
                    nextpage_check = soup_2.find_all("a", attrs={"class","button next"})
                    if len(nextpage_check) == 0:
                        do_while_loop = False
            else:
                print(url)
                # get song url
                soup_2 = self.get_soup(url)
                for a in soup_2.find_all("a",attrs={"class":"title"}):
                    if "target" not in a.attrs:
                        url_level_3 = a.attrs["href"]
                        title = a.attrs["title"]
                        soup_3 = self.get_soup(url_level_3)
                        verses_check = soup_3.find_all('p', attrs={'class': 'verse'})
                        if len(verses_check) == 0:
                            print("skipping", title)
                            continue
                        else:
                            print(title) 
                            lyrics = ''
                            for verse in verses_check:
                                text = verse.text.strip()
                                text = re.sub(r"\[.*\]\n", "", unidecode(text))
                                if lyrics == '':
                                    lyrics = lyrics + text.replace('\n', '|-|')
                                else:
                                    lyrics = lyrics + '|-|' + text.replace('\n', '|-|')
                            df.loc[count]=[title,lyrics]
                            count += 1
        return df
if __name__ == "__main__":
    base_url = "http://www.metrolyrics.com/"
    trailer_url = "-lyrics.html"
    artist_list = ["anirudh-ravichander", 
                   "ar-rahman",
                   "d-imman",
                   "deva",
                   "shankar-mahadevan",
                   "devi-sri-prasad",
                   "sid-sriram",
                   "chinmayi-sripada",
                   "srinivas",
                   "chinmayi-sripaada",
                   "sriram-parthasarathy",
                   "gv-prakash-kumar",
                   "vijay-prakash",
                   "sathya-prakash",
                   "ghibran",
                   "harris-jayaraj",
                   "thaman-s",
                   "yuvan-shankar-raja",
                   "arunraja-kamaraj",
                   "ilayaraja",
                   "t-m-sounderarajan",
                   "govind-vasantha",
                   "mani-sharma",
                   "vijay-yesudas",
                   "shankar-ehsaan-loy",
                   "santhosh-narayanan",
                   "dhanush",
                   "kamal-haasan"]
    ss = songScrapper(base_url,artist_list,trailer_url)
    df = ss.run()
    df.to_csv("lyrics.csv",index=False)