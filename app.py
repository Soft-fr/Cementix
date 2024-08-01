# app.py
from flask import Flask, request, jsonify, render_template
import random
import sqlite3
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

app = Flask(__name__)

# Fonction pour obtenir le mot mystère actuel
def get_current_word():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
    c.execute('SELECT word FROM words WHERE used = 1 AND strftime("%Y-%m-%d %H", hour) = ?', (current_hour,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

# Fonction pour choisir un nouveau mot mystère
def choose_new_word():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute('SELECT word FROM words WHERE used = 0 ORDER BY RANDOM() LIMIT 1')
    row = c.fetchone()
    if row:
        new_word = row[0]
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        c.execute('UPDATE words SET used = 1, hour = ? WHERE word = ?', (current_hour, new_word))
        conn.commit()
        conn.close()
        return new_word
    else:
        # Si tous les mots ont été utilisés, les réinitialiser
        c.execute('UPDATE words SET used = 0')
        conn.commit()
        conn.close()
        return choose_new_word()

# Route pour démarrer une nouvelle partie (toutes les heures)
@app.route('/new_game', methods=['GET'])
def new_game():
    word = get_current_word()
    if not word:
        word = choose_new_word()
    return jsonify({"message": "Nouvelle partie commencée !"})

# Route pour faire une supposition
@app.route('/guess', methods=['POST'])
def guess():
    data = request.get_json()
    guess_word = data.get("word")
    mystery_word = get_current_word()
    if not mystery_word:
        mystery_word = choose_new_word()
    similarity = calculate_similarity(mystery_word, guess_word)
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute('INSERT INTO guesses (word, similarity) VALUES (?, ?)', (guess_word, similarity))
    conn.commit()
    conn.close()
    return jsonify({"similarity": similarity})

# Fonction pour calculer la similarité sémantique
def calculate_similarity(word1, word2):
    vectorizer = TfidfVectorizer().fit_transform([word1, word2])
    vectors = vectorizer.toarray()
    return cosine_similarity(vectors)[0, 1]

# Route pour afficher l'interface utilisateur
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
