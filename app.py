from flask import Flask, request, render_template, jsonify
from scraper.amazon import runAmazonScraper, give_search_data, give_all_data
import threading

app = Flask(__name__)
search_in_progress = False

def run_search(search_term):
    global search_in_progress
    search_in_progress = True
    output = runAmazonScraper(search_term)
    search_in_progress = False
    return output

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/initial_data', methods=['POST'])
def initialize_data():
    output = give_all_data()
    return jsonify(output)

@app.route('/search', methods=['POST'])
def search():
    global search_in_progress
    if search_in_progress:
        return jsonify({"message": "Wait"})
    search_term = request.json.get('search_term')
    output = run_search(search_term)
    return output

@app.route('/button_click', methods=['POST'])
def button_click():
    global search_in_progress
    if search_in_progress:
        return jsonify({"message": "Wait"})
    button_text = request.json.get('button_text')
    output = run_search(button_text)
    return output

if __name__ == '__main__':
    app.run(debug=True)
