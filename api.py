from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# For practice only
books_dict = [
    {
        "id": 1,
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "genre": "Fiction",
    },
    {
        "id": 2,
        "title": "1984",
        "author": "George Orwell",
        "genre": "Dystopian",
    },
    {
        "id": 3,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "genre": "Fiction",
    }
]

@app.route('/books' , methods=['GET', 'POST'])
def books():
    if request.method == 'GET':
        if len(books_dict) > 0:
            return jsonify(books_dict)
        
        else:
            'Nothing found', 404

    if request.method == 'POST':
        new_title = request.form['title']
        new_author = request.form['author']
        new_genre = request.form['genre']
        iD = books_dict[-1]['id']+1

        new_object = {
        "id": iD,
        "title": new_title,
        "author": new_author,
        "genre": new_genre,
        }

        books_dict.append(new_object)
        return jsonify(books_dict), 201

if __name__ == '__main__':
    app.run(debug=True)