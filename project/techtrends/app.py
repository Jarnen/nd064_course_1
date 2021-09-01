import sqlite3
from datetime import datetime

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, Response
from werkzeug.exceptions import abort
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(name)s: %(message)s')


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row

    # record connections made to db
    time = str(datetime.now())
    connection.execute('INSERT INTO connections (datetime) VALUES (?)', (time,))
    connection.commit()

    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    # log line
    if post:
        today = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        app.logger.info('%s, Article "%s" retrieved!', today, post[2])

    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        # log line
        today = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        app.logger.info('%s: Error 404: Trying to access Non-existing article.', today)

        return render_template('404.html'), 404
    else:
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    # log line
    today = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    app.logger.info('%s, "About Us" page is retrieved!', today)
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()

            # log line
            today = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            app.logger.info('%s: New article, Title: "%s" created,', today, title)

            connection.close()
            return redirect(url_for('index'))
    return render_template('create.html')


# healthcheck endpoint
@app.route('/healthz')
def status():
    static_status = {"result": "OK - healthy"}
    response = Response(
        response=json.dumps(static_status),
        status=200,
        mimetype='application/json',
    )
    # log line
    app.logger.info('Health check request successful')
    return response


# metrics endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM posts')
    post_count = len(cursor.fetchall())

    cursor.execute('SELECT * FROM connections')
    db_connection_count = len(cursor.fetchall())

    data = {"db_connection_count": db_connection_count, "post_count": post_count}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json',
    )

    app.logger.info('Metrics request successful')
    connection.close()
    return response


# start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3111')
