from flask import Flask, request

app = Flask(__name__)
flags = {}

@app.route('/getsignal/<ticker>', methods=['GET'])
def receive_signal(ticker):
    return str(flags.get(ticker, "NULL"))

@app.route('/postsignal/<ticker>', methods=['POST'])
def make_signal(ticker):
    data = request.json
    if data:
        print(f"Made signal for {ticker}: {data['signal']}")
        flags[ticker] = data['signal']
    return "Signal made", 200

@app.route('/resetsignal/<ticker>', methods=['POST'])
def reset_signal(ticker):
    flags[ticker] = "NULL"
    return "Signal reset", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
