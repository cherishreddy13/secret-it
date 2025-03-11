from flask import Flask, render_template, request, jsonify, redirect, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key"
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

import dns.resolver
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']

# MongoDB Connection
client = MongoClient("mongodb+srv://reddycherish76:Cherish1302@dataleak.zr189.mongodb.net/")
db = client["chat_app"]
users_collection = db["users"]
messages_collection = db["messages"]
friends_collection = db["friends"]

@app.route("/")
def home():
    if "username" in session:
        return redirect("/friends")
    return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data["username"]
    password = data["password"]

    if users_collection.find_one({"username": username}):
        return jsonify({"message": "Username already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({"username": username, "password": hashed_password})
    return jsonify({"message": "Registration successful"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]

    user = users_collection.find_one({"username": username})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return jsonify({"message": "Invalid username or password"}), 401

    session["username"] = username
    return jsonify({"message": "Login successful"}), 200

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/")

@app.route("/friends")
def friends():
    if "username" not in session:
        return redirect("/")
    
    username = session["username"]
    friends = friends_collection.find({"user": username}, {"_id": 0, "friend": 1})
    return render_template("friends.html", username=username, friends=[f["friend"] for f in friends])

@app.route("/add_friend", methods=["POST"])
def add_friend():
    if "username" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json
    friend_username = data["friend_username"]
    username = session["username"]

    if users_collection.find_one({"username": friend_username}) is None:
        return jsonify({"message": "User does not exist"}), 404

    if friends_collection.find_one({"user": username, "friend": friend_username}):
        return jsonify({"message": "Already friends"}), 400

    friends_collection.insert_one({"user": username, "friend": friend_username})
    friends_collection.insert_one({"user": friend_username, "friend": username})
    return jsonify({"message": "Friend added successfully"}), 201

@app.route("/chat/<friend>")
def chat(friend):
    if "username" not in session:
        return redirect("/")
    
    username = session["username"]
    room = f"{min(username, friend)}_{max(username, friend)}"

    chat_logs = messages_collection.find({
        "$or": [
            {"sender": username, "receiver": friend},
            {"sender": friend, "receiver": username}
        ]
    }).sort("_id")

    chat_history = [{"sender": msg["sender"], "message": msg["message"]} for msg in chat_logs]
    return render_template("chat.html", username=username, friend=friend, chat_history=chat_history, room=room)

@socketio.on("join_room")
def handle_join_room(data):
    join_room(data["room"])
    print(f"{session['username']} joined room {data['room']}")

@socketio.on("leave_room")
def handle_leave_room(data):
    leave_room(data["room"])
    print(f"{session['username']} left room {data['room']}")

@socketio.on("send_message")
def handle_send_message(data):
    sender = session["username"]
    receiver = data["receiver"]
    message = data["message"]
    room = data["room"]

    messages_collection.insert_one({"sender": sender, "receiver": receiver, "message": message})
    
    emit("receive_message", {"sender": sender, "message": message}, room=room, include_self=False)

@socketio.on("message")
def handle_message(msg):
    print(f"Message received: {msg}")
    socketio.send(msg, broadcast=True)
    
    
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
