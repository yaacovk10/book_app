from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Helper function to execute SQL queries and fetch results
def execute_query(query, params=()):
    conn = sqlite3.connect('mylibrary.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    result = cursor.fetchall()
    conn.close()
    return result

# Function to create the database tables if they don't exist
def create_tables():
    with sqlite3.connect('mylibrary.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES authors (id)
            )
        ''')
        conn.commit()

# Create tables before running the app
create_tables()

@app.route('/')
def index():
    # Fetch authors and books data from the database
    authors = execute_query("SELECT * FROM authors")
    books = execute_query("SELECT * FROM books")
    
    author_data = [{'id': author[0], 'name': author[1]} for author in authors]
    book_data = [{'id': book[0], 'title': book[1], 'author_id': book[2]} for book in books]
    
    return jsonify(authors=author_data, books=book_data)

@app.route('/add_author', methods=['POST'])
def add_author():
    data = request.json
    author_name = data.get('author_name')
    if author_name:
        execute_query("INSERT INTO authors (name) VALUES (?)", (author_name,))
        response = {'message': 'Author added successfully'}
    else:
        response = {'error': 'Author name cannot be empty'}
    return jsonify(response)

@app.route('/add_book', methods=['POST'])
def add_book():
    data = request.json
    author_name = data.get('author')
    book_title = data.get('book')

    if author_name and book_title:
        # Check if the author exists in the database, and get their ID
        author_query = execute_query("SELECT id FROM authors WHERE name = ?", (author_name,))
        if author_query:
            author_id = author_query[0][0]
            # Insert the book with the author's ID
            execute_query("INSERT INTO books (title, author_id) VALUES (?, ?)", (book_title, author_id))
            response = {'message': 'Book added successfully'}
        else:
            response = {'error': 'Author not found in the database'}
    else:
        response = {'error': 'Author and book fields are required'}
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
