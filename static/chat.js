let socket = io();

function setupSocket(username, friend, room) {
    socket.emit("join_room", { room });

    socket.on("receive_message", (data) => {
        let chatBox = document.getElementById("chat-box");
        let newMessage = document.createElement("p");

        if (data.sender === username) {
            newMessage.innerHTML = `<strong>You:</strong> ${data.message}`;
        } else {
            newMessage.innerHTML = `<strong>${data.sender}:</strong> ${data.message}`;
        }

        chatBox.appendChild(newMessage);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to latest message
    });
}

function sendMessage(receiver, room) {
    let message = document.getElementById("message").value;
    if (message.trim() === "") return;

    let chatBox = document.getElementById("chat-box");
    let newMessage = document.createElement("p");
    newMessage.innerHTML = `<strong>You:</strong> ${message}`;
    chatBox.appendChild(newMessage);
    chatBox.scrollTop = chatBox.scrollHeight;

    socket.emit("send_message", { receiver, message, room });

    document.getElementById("message").value = "";
}
