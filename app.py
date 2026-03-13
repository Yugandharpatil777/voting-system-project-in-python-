from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
# In a real app, use a secure random key
app.secret_key = 'super_secret_voting_key'

DATABASE = 'voting.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    candidates = conn.execute('SELECT * FROM candidates').fetchall()
    conn.close()
    return render_template('index.html', candidates=candidates)

@app.route('/vote', methods=['POST'])
def vote():
    candidate_id = request.form.get('candidate_id')
    voter_ip = request.remote_addr # Note: In production behind proxies, use request.headers.get('X-Forwarded-For', request.remote_addr)

    if not candidate_id:
        flash('Please select a candidate before voting.', 'error')
        return redirect(url_for('index'))

    conn = get_db_connection()
    existing_vote = conn.execute('SELECT id FROM votes WHERE voter_ip = ?', (voter_ip,)).fetchone()
    
    if existing_vote:
         # Prevent multiple votes from the same IP (optional strict rule)
         pass # Allowing multiple for testing purposes.

    try:
        conn.execute('INSERT INTO votes (candidate_id, voter_ip) VALUES (?, ?)',
                     (candidate_id, voter_ip))
        conn.commit()
        flash('Your vote has been successfully cast!', 'success')
    except sqlite3.Error as e:
        flash(f'An error occurred: {e}', 'error')
    finally:
        conn.close()

    return redirect(url_for('results'))

@app.route('/results')
def results():
    conn = get_db_connection()
    # Join candidates and votes to get tally
    query = '''
        SELECT c.name, COUNT(v.id) as vote_count
        FROM candidates c
        LEFT JOIN votes v ON c.id = v.candidate_id
        GROUP BY c.id
        ORDER BY vote_count DESC
    '''
    tally = conn.execute(query).fetchall()
    
    total_votes = conn.execute('SELECT COUNT(id) FROM votes').fetchone()[0]
    conn.close()
    
    return render_template('results.html', tally=tally, total_votes=total_votes)

if __name__ == '__main__':
    # Initialize db on first run if it doesn't exist
    if not os.path.exists(DATABASE):
        import init_db
        init_db.init_db()
    app.run(debug=True, port=8080)
