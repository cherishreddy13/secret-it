function register() {
   let username = document.getElementById("username").value;
   let password = document.getElementById("password").value;

   fetch("/register", {
       method: "POST",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify({ username, password })
   })
   .then(res => res.json())
   .then(data => alert(data.message));
}

function login() {
   let username = document.getElementById("username").value;
   let password = document.getElementById("password").value;

   fetch("/login", {
       method: "POST",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify({ username, password })
   })
   .then(res => res.json())
   .then(data => {
       if (data.message === "Login successful") {
           window.location.href = "/friends";
       } else {
           alert(data.message);
       }
   });
}

function addFriend() {
   let friend_username = document.getElementById("friend-username").value;

   fetch("/add_friend", {
       method: "POST",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify({ friend_username })
   })
   .then(res => res.json())
   .then(data => alert(data.message));
}
