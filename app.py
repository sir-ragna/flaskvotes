from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'super-secret-key-$$&'
app.config['DATABASE'] = 'posts.db'

def get_votes(post_id, rating):
    """Database helper function to retrieve the votes of a post.
    get_votes(1, -1) # will return all -1 votes for post 1"""
    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.execute("""
            SELECT count(*) 
            FROM posts, votes 
            WHERE posts.post_id = votes.post_id
            AND posts.post_id = ?
            AND rating = ?
            GROUP BY rating, posts.post_id
            """, (post_id, rating))
        row = cursor.fetchone()
        if row == None:
            return 0 # no votes yet
        else:
            return row[0]

def get_top_posts(limit=5):
    """Retrieve the top rated posts. Default limit=5"""
    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.execute("""
            SELECT posts.post_id, SUM(
                CASE WHEN votes.rating IS NULL 
                    THEN 0 
                    ELSE votes.rating 
                END) as 'score'
            FROM posts
            LEFT JOIN votes on posts.post_id = votes.post_id
            GROUP BY posts.post_id
            ORDER BY score DESC
            LIMIT ?
            """, (limit,))
        posts = []
        for row in cursor.fetchall():
            posts.append({'post_id': row[0], 'score': row[1]})
        return posts

@app.route('/', methods=['GET', 'POST'])
def homepage():
    username = None
    if request.method == 'POST' and 'username' in request.form:
        session['username'] = request.form['username']
    if 'username' in session:
        username = session['username']

    return render_template('home.html', username=username, posts=get_top_posts())

@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'POST' and 'content' in request.form:
        content = request.form['content']
        with sqlite3.connect(app.config['DATABASE']) as conn:
            cursor = conn.execute('INSERT INTO posts (post_content) VALUES (?)', (content,))
            post_id = cursor.lastrowid
            conn.commit()
            return redirect(url_for('view_post', post_id=post_id))

    return render_template('createpost.html')

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.execute('SELECT post_id, post_content FROM posts'
            ' WHERE post_id = ?', (post_id,))
        row = cursor.fetchone()
        if row != None:
            post_id = row[0]
            upvotes = get_votes(post_id, 1)
            downvotes = get_votes(post_id, -1)
            return render_template('showpost.html', content=row[1], nr=post_id, upvotes=upvotes, downvotes=downvotes)
    return "Post could not be found", 404

@app.route('/vote')
def vote():
    post_id = request.args.get('post_id')
    rating = request.args.get('rating')

    if post_id == None:
        return "Cannot vote without post_id", 403
    if not 'username' in session:
        return "Not authenticated", 401

    if rating == 'good':
        rating = 1
    elif rating == 'bad':
        rating = -1
    else:
        return "Invalid score provided", 400

    try:
        with sqlite3.connect(app.config['DATABASE']) as conn:
            conn.execute("""INSERT INTO votes (post_id, username, rating) 
            VALUES (?, ?, ?)""", (post_id, session['username'], rating))
            conn.commit()
            return "Voted!", 200
    except sqlite3.IntegrityError as ex:
        return "Already voted (forbidden)", 403
    except Exception as ex:
        app.logger.error("{}".format(ex))
        return "Something went wrong", 500

@app.route('/signoff')
def signoff():
    session.clear()
    return redirect(url_for('homepage'))