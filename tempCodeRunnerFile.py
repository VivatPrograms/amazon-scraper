from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

# @app.route('/search', methods=['POST'])
# def search():
#     search_text = request.form['searchText']
#     return f"Received search text: {search_text}"

if __name__ == '__main__':
    app.run(debug=True)
