import urllib
from datetime import datetime
from bs4 import BeautifulSoup
import nltk
import pytz

from articles.models import Article

def createArticleObject(title, subtitle, body, date, keywords, url, type, source):
    #print([title, subtitle, body, date, keywords, url, type, source])
    try:
        article = Article(Headline=title, SubHeadline=subtitle,
                      Content=body, Url=url,
                      DateTime=date, Keywords=keywords,
                      Type=type,
                      Source=source)
    except Exception as err:
                print("In createArticleObject():"+ err)
    return article

def createArticleByUrl(url):
    [title, subtitle, body, date, keywords, source] = getArticleDetailsByUrl(url)
    article = createArticleObject(title, subtitle, body, date, keywords, url, "RSS", source)
    return article



def getArticleDetailsByUrl(url):
    page = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(page)
    soup.prettify()
    title = soup.title.string
    #print("in getArticlesDetails(), title: "+ title + " Done!")


    title_clean = str.split(soup.title.string, ' | ')[0]
    doc_descr = soup.head.find("meta",attrs={"name":"description"}).get('content')
    doc_body = ''

    if "The Irish Times" in soup.text:
        for body_p_tag in soup.article.find_all("p", attrs={"class": "no_name"}):
            doc_body += body_p_tag.get_text() + '\n'
    elif "BBC" in title:
        for tag in soup.find("div", attrs={"class": "story-body"}).find_all("p"):
            if "JavaScript" not in tag.get_text():
                doc_body += tag.get_text() + '\n'

    date = datetime.utcnow()
    source = "Other"
    if "The Irish Times" in soup.text:
        source = "Irish Times"
        body_p_tag = soup.article.find("div", attrs={"class": "last_updated"}).find("p")
        date = datetime.strptime(body_p_tag.get_text(), "%a, %b %d, %Y, %H:%M")
        local_dt = pytz.timezone('Europe/Dublin').localize(date, is_dst=None)
        date = local_dt.astimezone(pytz.utc)
    elif "BBC" in title:
        source = "BBC"
        tag = soup.find("span", attrs={"class": "date"})
        date = tag.get_text()
        tag = soup.find("span", attrs={"class": "time"})
        date += " " + tag.get_text()
        if "GMT" in date:
            date = datetime.strptime(date, "%d %B %Y %H:%M %Z")
        else:
            date = datetime.strptime(date, "%d %B %Y %H:%M")
            local_dt = pytz.timezone('Europe/Dublin').localize(date, is_dst=None)
            date = local_dt.astimezone(pytz.utc)

    keywords = extractKeywords(title_clean)

    #print([title_clean, doc_descr, doc_body, date, keywords, source])

    return [title_clean, doc_descr, doc_body, date, keywords, source]


def extractKeywords(text):
    stop_words = load_stopwords()
    keywords = []
    tokens = nltk.word_tokenize(text)
    #print(tokens)

    for token in tokens:
        if token not in stop_words:
            keywords.append(token.lower())

    #print(keywords)
    return ", ".join(keywords)

def load_stopwords():
    stop_words = nltk.corpus.stopwords.words('english')
    # custom stop words
    stop_words.extend(['this', 'that', 'the', 'might', 'have', 'been', 'from',
                           'but', 'they', 'will', 'has', 'having', 'had', 'how', 'went'
                            'were', 'why', 'and', 'still', 'his','her',
                           'was', 'its', 'per', 'cent',
                           'a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also', 'am', 'among',
                           'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can',
                           'cannot', 'could', 'dear', 'did', 'do', 'does', 'either', 'else', 'ever', 'every',
                           'for', 'from', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers', 'him', 'his',
                           'how', 'however', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'least', 'let',
                           'like', 'likely', 'may', 'me', 'might', 'most', 'must', 'my', 'neither', 'no', 'nor',
                           'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our', 'own', 'rather', 'said',
                           'say', 'says', 'she', 'should', 'since', 'so', 'some', 'than', 'that', 'the', 'their',
                           'them', 'then', 'there', 'these', 'they', 'this', 'tis', 'to', 'too', 'twas', 'us',
                           'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who',
                           'whom', 'why', 'will', 'with', 'would', 'yet', 'you', 'your', 've', 're', 'rt'])
    #turn list into set for faster search
    stop_words = set(stop_words)
    return stop_words