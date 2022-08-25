from flask import Flask
from flask import request
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)


class AuthorModel(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(32), unique=True)
   quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic', cascade="all, delete-orphan")

   def __init__(self, name):
       self.name = name
   def to_dict(self):
       return {
           "id": self.id,
           "name": self.name
       }

class QuoteModel(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
   text = db.Column(db.String(255), unique=False)

   def __init__(self, author, text):
       self.author_id = author.id
       self.text = text

   def to_dict(self):
       return {
           "id": self.id,
           "author": self.author.to_dict(),
           "text": self.text
           }


@app.route("/authors")
def get_authors():
    authors = AuthorModel.query.all()
    authors_dict = []
    for author in authors:
        authors_dict.append(author.to_dict())
    return authors_dict


@app.route("/authors/<int:id>")
def get_author_by_id(id):
    author = AuthorModel.query.get(id)
    if author:
        return author.to_dict()
    return f"Quote with id {id} not found.", 404


@app.route("/authors", methods=["POST"])
def create_author():
       author_data = request.json
       author = AuthorModel(author_data["name"])
       author_old = AuthorModel.query.get(id)
       db.session.add(author)
       db.session.commit()
       return author.to_dict(), 201


@app.route("/authors/<int:id>", methods=["PUT"])
def edit_authors(id):
    author = AuthorModel.query.get(id)
    if author is None:
        return f"Quote with id {id} not found.", 404
    new_data = request.json
    for key in new_data.keys():
        setattr(author, key, new_data[key])
    db.session.commit()
    return author.to_dict()


@app.route("/authors/<int:id>", methods=["DELETE"])
def delete_authors(id):
    author = AuthorModel.query.get(id)
    db.session.delete(author)
    db.session.commit()
    return author.to_dict(), 201






@app.route("/quotes")
# object --> dict --> JSON
def get_quotes():
    quotes = QuoteModel.query.all()
    quotes_dict = []
    for quote in quotes:
        quotes_dict.append(quote.to_dict())
    return quotes_dict


@app.route("/quotes/<int:id>")
def get_quote_by_id(id):
    quote = QuoteModel.query.get(id)
    if quote:
        return quote.to_dict()
    return f"Quote with id {id} not found.", 404


@app.route("/quotes", methods=['POST'])
def create_quote():
    new_quote = request.json
    # quote = QuoteModel(author=new_quote['author'], text=new_quote['text'])
    quote = QuoteModel(**new_quote)
    db.session.add(quote)
    db.session.commit()
    return quote.to_dict(), 201


@app.route("/quotes/filter")
def get_quotes_by_filter():
    params = request.args
    filter_quotes = [quote for quote in quotes if quote["author"] == params["author"]]
    return filter_quotes, 200


# /quotes/4
@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
    quote = QuoteModel.query.get(id)
    if quote is None:
        return f"Quote with id {id} not found.", 404

    new_data = request.json
    for key in new_data.keys():
        setattr(quote, key, new_data[key])

    db.session.commit()
    return quote.to_dict()


if __name__ == "__main__":
    app.run(debug=True)