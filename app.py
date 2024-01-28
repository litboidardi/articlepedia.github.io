import bcrypt
from flask import Flask, render_template, request, redirect
from flask_pymongo import pymongo
from bson import ObjectId

CONNECTION_STRING = 'mongodb+srv://darci:darci@cluster0.pswij0e.mongodb.net/?retryWrites=true&w=majority'

client = pymongo.MongoClient(CONNECTION_STRING)

db = client.get_database('blog')
article_collection = pymongo.collection.Collection(db, 'articles')
user_collection = pymongo.collection.Collection(db, 'users')


app = Flask(__name__)


@app.route('/')
def index():
    # limitovanie na max 6 záznamov
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=6, type=int)
    skip = (page - 1) * limit

    articles = []
    total_articles = article_collection.count_documents({})
    total_pages = (total_articles - 1) // limit + 1

    for article in article_collection.find().skip(skip).limit(limit):
        author_id = article['author_id']
        author = user_collection.find_one({"_id": ObjectId(author_id)})
        if author:
            article['author_name'] = author['name']
        articles.append(article)

    return render_template("index.html", articles=articles, page=page, limit=limit, total_pages=total_pages)


@app.route('/article/<_id>')
def show_article(_id):
    article = article_collection.find_one({"_id": ObjectId(_id)})
    if article:
        author_id = article['author_id']
        author = user_collection.find_one({"_id": ObjectId(author_id)})
        if author:
            article['author_name'] = author['name']
        comments = article['comments']
        for comment in comments:
            comment_author_id = comment['author']
            comment_author = user_collection.find_one({"_id": ObjectId(comment_author_id)})
            if comment_author:
                comment['author_name'] = comment_author['name']
        return render_template("view.html", article=article)
    else:
        return "Article not found"


# vyvorenie articlu
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        text = request.form['text']
        author_id = request.form['author_id']
        image = request.form['image']

        article = {
            "title": title,
            "date": date,
            "text": text,
            "author_id": ObjectId(author_id),
            "image": image
        }
        article_collection.insert_one(article)
        return redirect('/')
    else:
        return render_template("create.html")

# update pre article
@app.route('/<_id>/update/', methods=('GET', 'POST'))
def update(_id):
    article = article_collection.find_one({"_id": ObjectId(_id)})
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        text = request.form['text']

        article_collection.update_one({"_id": ObjectId(_id)}, {'$set': {
            "name": name,
            "date": date,
            "text": text
        }})
        return redirect('/')
    else:
        return render_template("update.html", article=article)

# vymazanie articlu
@app.route("/<_id>/delete/", methods=('GET', 'POST'))
def delete(_id):
    article_collection.delete_one({"_id": ObjectId(_id)})
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)