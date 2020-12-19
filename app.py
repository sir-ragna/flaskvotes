from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'super-secret-key-$$&'


""" # TODO display ratings
SELECT count(*) as 'amount votes',posts.post_id,rating 
FROM posts, votes 
WHERE posts.post_id = votes.post_id
GROUP BY rating, posts.post_id
ORDER BY 'amount votes' DESC
LIMIT 5


SELECT count(*),rating 
FROM posts, votes 
WHERE posts.post_id = votes.post_id
AND posts.post_id = 2
AND rating = 'good'
GROUP BY rating, posts.post_id

SELECT count(*),rating 
FROM posts, votes 
WHERE posts.post_id = votes.post_id
AND posts.post_id = 2
AND rating = 'bad'
GROUP BY rating, posts.post_id
"""


@app.route('/', methods=['GET', 'POST'])
def homepage():
    username = None
    if request.method == 'POST' and 'username' in request.form:
        session['username'] = request.form['username']
    if 'username' in session:
        username = session['username']
    return render_template('home.html', username=username)

@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'POST' and 'content' in request.form:
        content = request.form['content']
        with sqlite3.connect('posts.db') as conn:
            cursor = conn.execute('INSERT INTO posts (post_content) VALUES (?)', (content,))
            post_id = cursor.lastrowid
            conn.commit()
            return redirect(url_for('view_post', post_id=post_id))

    return render_template('createpost.html')

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    with sqlite3.connect('posts.db') as conn:
        cursor = conn.execute('SELECT post_id, post_content FROM posts'
            ' WHERE post_id = ?', (post_id,))
        row = cursor.fetchone()
        if row != None:
            return render_template('showpost.html', content=row[1], nr=row[0])
    return "Post could not be found", 404

@app.route('/vote')
def vote():
    post_id = request.args.get('post_id')
    rating = request.args.get('rating')
    if post_id == None:
        return "Cannot vote without post_id", 403
    if not 'username' in session:
        return "Not authenticated", 401

    try:
        with sqlite3.connect('posts.db') as conn:
            conn.execute("""INSERT INTO votes (post_id, username, rating) 
            VALUES (?, ?, ?)""", (post_id, session['username'], rating))
            conn.commit()
    except sqlite3.IntegrityError as ex:
        return "Already voted (forbidden)", 403
    
    return "Voted!", 200

@app.route('/signoff')
def signoff():
    session.clear()
    return redirect(url_for('homepage'))