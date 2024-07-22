from flask import Flask, request, jsonify, render_template
from flask import session,redirect, url_for
import os

app = Flask(__name__)
class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

# Dummy user credentials for demonstration purposes
users = [
    User("admin", "admin@hello", "password"),  # User 1
    User("user", "user@hello", "123456")    # User 2
]
# Dummy user credentials for demonstration purposes
secret_key = os.urandom(24)  # Generate a random 24-byte key

# Set the secret key for the Flask application
app.secret_key = secret_key
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    # Dummy authentication logic - check if user exists
    user1 = next((user for user in users if user.username == username and user.password == password), None)

    if user1:
        session['username'] = user1.username
        return redirect(url_for('letters'))
    else:
        return jsonify({'message': 'Некорректные имя пользователя или пароль, пробуйте снова','status':'401'}),401

@app.route('/signup', methods=['POST','get'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Simple validation - check if username and email are unique
    if any(user.username == username for user in users):
        return jsonify({"message": "Такое имя уже существует, станьте более уникальными","status":"400"}), 400

    if any(user.email == email for user in users):
        return jsonify({"message": "Есть такая почта, вам не достанется","status":"400"}), 400

    # Create a new user
    new_user = User(username,email,password)
    print(new_user.username,new_user.email,new_user.password)
    users.append(new_user)


    return jsonify({"message": "Успех","status":"201"}), 201

class Letter:
    def __init__(self, letter_id, sender,receiver_email, content):
        self.id = letter_id
        self.sender = sender
        self.receiver = receiver_email
        self.content = content

    def serialize(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "content": self.content
        }

letter_data = [
    Letter(1,'admin','admin@hello', 'Hello, World!'),
    Letter(2,'admin','user@hello', 'Hello, User!')
]

def get_current_user():
    if 'username' in session:
        username = session['username']
        return next((user for user in users if user.username==username),None)
    return None

@app.route('/letters', methods=['GET', 'POST', 'PUT', 'DELETE'])
def letters():
    if request.method == 'GET':
        # Get the current user (you need to implement this based on authentication)
        current_user = get_current_user()
        if current_user:
            # Filter messages based on the current user
            
            user_letters = [letter.serialize() for letter in letter_data if letter.receiver == current_user.email]
            return render_template('letters.html',letter_data=user_letters)
        else:
            return jsonify({"message": "А вы не в системе-_()_-", 'status':'401'}), 401

    if request.method == 'POST':
        # Create a new letter
        new_letter_data = request.json
        receiver = new_letter_data.get('receiver')
        if not receiver:
            return jsonify({"message": "А кому?", 'status':'400'}), 400
        if not new_letter_data.get('content'):
            return jsonify({"message": "А что слать?", 'status':'400'}), 400
        if next((user for user in users if user.email == receiver), None) is None:
            return jsonify({"message": "Нет такой почты", 'status':'400'}), 400
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "А вы не в системе-_()_-", 'status':'401'}), 401
        if current_user is None:
            return jsonify({"message": "А мы тебя не нашли", 'status':'401'}), 401
        new_letter = Letter(letter_data[-1].id+1 if len(letter_data) else 1, current_user.username,receiver,new_letter_data.get('content'))
        print(new_letter.sender,':',new_letter.content)
        letter_data.append(new_letter)
        return jsonify({"message": "Успех?",'status':'201'}), 201

    if request.method == 'PUT':
        # Update an existing letter
        letter_id = request.json.get('id')
        updated_content = request.json.get('content')
        for letter in letter_data:
            if letter.id == letter_id:
                letter.content = updated_content
                break
        else:
            return jsonify({"message": "Letter not found.", 'status':'404'}), 404
        return jsonify({"message": "Letter updated successfully!", 'status':'200'}), 200

    if request.method == 'DELETE':
        # Delete a letter
        letter_id = request.json.get('id')
        try:
            int(letter_id)
        except Exception as e:
            return jsonify({"message": "Не нашли, введи только число", 'status':'404'}), 410
        user = get_current_user()
        for letter in letter_data:
            if letter.id == int(letter_id) and user.email == letter.receiver:
                letter_data.remove(letter)
                break
        else:
            return jsonify({"message": "Не нашли письмо", 'status':'404'}), 404
        return jsonify({"message": "Успех?", 'status':'200'}), 200
    return jsonify({"message": "Не хацкай!", 'status':'400'}), 400
app.run(host = '192.168.100.3', port = '80', threaded=True, debug=True)
