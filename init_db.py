import sqlite3

def init_db():
    # Connect to the database (it will be created if it doesn't exist)
    connection = sqlite3.connect('voting.db')
    
    # Read the schema file
    with open('schema.sql') as f:
        connection.executescript(f.read())

    # Create a cursor object
    cur = connection.cursor()

    # Pre-populate some candidates
    candidates = [
        ('Narendra modi', 'Experienced leader focused on community growth.'),
        ('Rahul gandhi', 'Innovative thinker with a tech-forward platform.'),
        ('amit shah', 'Dedicated to education and infrastructure.')
    ]

    cur.executemany(
        "INSERT INTO candidates (name, description) VALUES (?, ?)",
        candidates
    )

    # Commit changes and close the connection
    connection.commit()
    connection.close()
    print("Database initialized successfully with sample candidates.")

if __name__ == '__main__':
    init_db()
