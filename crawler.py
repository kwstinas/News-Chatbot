import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pymongo import MongoClient
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from typing import List
import uvicorn

# Σύνδεση με MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['news_database']
collection = db['articles']

# Δημιουργία FastAPI instance
app = FastAPI()

class Article:
    def __init__(self, title, link, content, author=None, published_date=None, category=None):
        self.title = title
        self.link = link
        self.content = content
        self.author = author
        self.published_date = published_date
        self.category = category

    def to_dict(self):
        return {
            'title': self.title,
            'link': self.link,
            'content': self.content,
            'author': self.author,
            'published_date': self.published_date,
            'category': self.category
        }

class Crawler:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Θα προκαλέσει εξαίρεση σε περίπτωση 404 ή άλλου HTTP σφάλματος
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.HTTPError as e:
            print(f"Skipping {url} due to HTTP error: {e}")  # Αγνοεί τις σελίδες που επιστρέφουν 404 ή άλλα σφάλματα
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_article(self, article_soup):
        raise NotImplementedError("Η μέθοδος αυτή πρέπει να υλοποιηθεί από τις υποκλάσεις!")

    def crawl(self):
        page_soup = self.fetch_page(self.base_url)
        if not page_soup:
            return []

        articles = []

        # Αναζήτηση άρθρων με έλεγχο συνδέσμων
        for item in page_soup.find_all('article'):
            link_element = item.find('a')
            
            if link_element and link_element.has_attr('href'):
                article_url = urljoin(self.base_url, link_element['href'])
            else:
                continue

            # Απόπειρα άντλησης σελίδας άρθρου και διαχείριση μη διαθέσιμων σελίδων
            article_soup = self.fetch_page(article_url)
            if article_soup:
                article = self.parse_article(article_soup)
                if article:
                    articles.append(article)

        return articles

class NewsbeastCrawler(Crawler):
    def __init__(self):
        super().__init__('https://www.newsbeast.gr/')

    def parse_article(self, article_soup):
        title = article_soup.find('h1').text.strip() if article_soup.find('h1') else 'No title found'
        content = " ".join([p.text.strip() for p in article_soup.find_all('p')])

        time_element = article_soup.find('time')
        published_date = time_element['datetime'] if time_element and 'datetime' in time_element.attrs else None
        
        author = article_soup.find('span', class_='author').text.strip() if article_soup.find('span', class_='author') else 'Unknown'
        link = article_soup.find('link', rel='canonical')['href'] if article_soup.find('link', rel='canonical') else None

        return Article(title, link, content, author, published_date, 'General')

class LifoCrawler(Crawler):
    def __init__(self):
        super().__init__('https://www.lifo.gr/')

    def parse_article(self, article_soup):
        title = article_soup.find('h1').text.strip() if article_soup.find('h1') else 'No title found'
        content = " ".join([p.text.strip() for p in article_soup.find_all('p')])

        time_element = article_soup.find('time')
        published_date = time_element['datetime'] if time_element and 'datetime' in time_element.attrs else None
        link = article_soup.find('link', rel='canonical')['href'] if article_soup.find('link', rel='canonical') else None

        return Article(title, link, content, None, published_date, 'General')

def save_article_to_db(article):
    if collection.count_documents({'link': article.link}) == 0:
        collection.insert_one(article.to_dict())

@app.get("/api/articles", response_model=List[dict])
def get_articles():
    articles = collection.find()
    result = []
    for article in articles:
        article_data = {
            'title': article.get('title'),
            'link': article.get('link'),
            'content': article.get('content'),
            'author': article.get('author'),
            'published_date': article.get('published_date'),
            'category': article.get('category')
        }
        result.append(article_data)
    return result

@app.post("/api/crawl")
def crawl_and_save_articles():
    crawlers = [
        NewsbeastCrawler(),
        LifoCrawler(),
    ]
    for crawler in crawlers:
        articles = crawler.crawl()
        for article in articles:
            save_article_to_db(article)
    return {"status": "completed", "message": "Articles crawled and saved successfully"}

# Προγραμματισμένη εργασία που εκτελεί την άντληση κάθε 1 ώρα
scheduler = BackgroundScheduler()

def scheduled_crawl():
    crawlers = [
        NewsbeastCrawler(),
        LifoCrawler(),
    ]
    for crawler in crawlers:
        articles = crawler.crawl()
        for article in articles:
            save_article_to_db(article)
    print("Scheduled crawl completed.")

# Προσθήκη του scheduled crawl στο scheduler κάθε 1 ώρα
scheduler.add_job(scheduled_crawl, 'interval', hours=1)

@app.on_event("startup")
def startup_event():
    scheduler.start()
    print("Scheduler started successfully.")

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    print("Scheduler terminated.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
