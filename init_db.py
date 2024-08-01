# init_db.py
import sqlite3

conn = sqlite3.connect('app.db')
c = conn.cursor()

# Table pour les mots mystères
c.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL,
        used BOOLEAN NOT NULL DEFAULT 0
    )
''')

# Table pour les résultats des jeux
c.execute('''
    CREATE TABLE IF NOT EXISTS guesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL,
        similarity REAL NOT NULL,
        guessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Insertion de plus de 3000 mots
words = ["mot1", "mot2", "mot3", "..."]  # Ajoutez ici plus de 3000 mots

c.executemany('INSERT INTO words (word) VALUES (?)', [(word,) for word in words])

conn.commit()
conn.close()
