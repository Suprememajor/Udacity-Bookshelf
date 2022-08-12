from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from models import Book, setup_db, db

BOOKS_PER_SHELF = 8


# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.

def paginate_books(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF
    books = [book.format() for book in selection]
    current_books = books[start:end]

    return current_books

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route('/books')
    def get_books():
        selection = Book.query.order_by(Book.rating.desc(), Book.title)
        current_books = paginate_books(request, selection)

        if len(current_books) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "books": current_books,
                "total_books": len(Book.query.all())
            }
        )

    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars

    @app.route('/books/<int:book_id>', methods=["PATCH"])
    def edit_book_rating(book_id):
        book = Book.query.get(book_id)
        book.rating = request.json["rating"]
        success = True

        try:
            db.session.commit()
        except:
            success = False
            db.session.rollback()
        finally:
            db.session.close()

        return jsonify({"success": success})

    @app.route('/books/<int:book_id>', methods=["DELETE"])
    def delete_book(book_id):
        book = Book.query.get(book_id)
        success = True

        try:
            db.session.delete(book)
            db.session.commit()
        except:
            success = False
            db.session.rollback()
        finally:
            db.session.close()

        return jsonify({"success": success})

    @app.route('/books', methods=["POST"])
    def add_book():
        response = dict()
        book = Book(
            title=request.json["title"],
            author=request.json["author"],
            rating=request.json["rating"]
        )
        response["success"] = True

        try:
            db.session.add(book)
            db.session.commit()
            response["created"] = book.id
        except:
            response["success"] = False
            db.session.rollback()
        finally:
            db.session.close()

        return jsonify(response)

    return app
