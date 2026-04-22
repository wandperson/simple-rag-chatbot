/*
    Send the message to the server and update chat
*/
function sendMessage() {
    let question = document.getElementById("message-input").value;
    if (question === "")
        return;
    
    fetch("/api/chat/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ content: question })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Response error: " + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        createChatItem("user", question, data.timestamp);
        document.getElementById("message-input").value = "";
        createChatItem(data.role, data.content, data.timestamp);

        // Scroll messages to the bottom
        let displayContainer = document.getElementById("display-container");
        displayContainer.scrollTo({
            top: displayContainer.scrollHeight,
            behavior: 'smooth'
        });
    })
    .catch(error => {
        console.error("Error while fetching: ", error);
    });
}

/*
    Create new chat item on the page
    Similar how chat created when templete render
*/
function createChatItem(role, content, timestamp) {
        let messagesList = document.getElementById("chat-messages");

        let li = document.createElement("li");
        li.className = `message-item message-item-${role}`;
        li.innerHTML = `
            <p>${content}</p>
            <small id="message-time">${timestamp}</small>
        `;
        
        messagesList.appendChild(li);
}

document.getElementById("message-input")
.addEventListener("keyup", function (event) {
    if (event.key == "Enter") {
        sendMessage()
    }
})
