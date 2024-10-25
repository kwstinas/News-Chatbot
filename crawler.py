from fastapi import FastAPI
from pymongo import MongoClient
from typing import List

# Σύνδεση με MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['news_database']
collection = db['articles']

# Δημιουργία FastAPI instance
app = FastAPI()

# Μοντέλο δεδομένων για τα άρθρα
class ArticleModel:
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

@app.get("/api/articles", response_model=List[dict])
def get_articles():
    """
    Επιστρέφει όλα τα άρθρα από τη MongoDB
    """
    articles = collection.find()  # Ανάκτηση όλων των άρθρων από τη MongoDB
    
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

# Εκκίνηση του FastAPI server με uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
