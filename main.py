from flask import Flask, request

app = Flask(__name__)
flag = "NULL"
#создание локального сервера который будет хранить состояния 
@app.route('/getsignal', methods=['GET'])
def receive_signal():    
    return str(flag)

@app.route('/postsignal', methods=['POST'])
def make_signal():    
    global flag
    data = request.json    
    if data:
        print(f"Made signal: {data['signal']}")        
        flag = data['signal']
    return "Signal made", 200

@app.route('/resetsignal', methods=['POST'])def reset_signal():
    global flag    
    flag = "NULL"
    return "Signal reset", 200

if __name__ == "__main__":    
    app.run(debug=True, port=5000)
