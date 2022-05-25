document.addEventListener("DOMContentLoaded", (e) => {
    let baseURL = "https://localhost:8083/"
    const webSocketURL = "https://localhost:8084"
    let lockerId = window.location.href.split("/")[4]
    let submitBtn = document.getElementById("submit-btn")
    let mainDiv = document.getElementById("main")

    socket = io.connect(webSocketURL);

    socket.on("connect", function () {
        console.log("Correctly connected to the chat");
    });

    socket.on("joined_room", function (message) {
        console.log("Joined to the room ", message);
    });

    socket.on("left_room", function (message) {
        console.log("Left the room ", message);
    });

    submitBtn.addEventListener("click", (e) => {
        let form = document.getElementById("form")
        let formData = new FormData(form)

        function sendNotification(id) {
            useragent = navigator.userAgent;
            socket.emit("join", {useragent: useragent, room_id: id});
            socket.emit("change_state", {id: id, state: "LOCKER", room_id: id})
            socket.emit("leave", {useragent: useragent, room_id: id});
        }

        postPackage(formData).then((res) => {
            let alertDiv = document.getElementById("alert-div")
            if (alertDiv !== null) {
                mainDiv.removeChild(alertDiv)
            }
            let div = document.createElement("div")
            let text = ""
            if (res === 200) {
                div.setAttribute("class", "alert alert-success")
                div.setAttribute("id", "alert-div")
                div.setAttribute("role", "alert")
                text = document.createTextNode("You send your package successfully ID:" + formData.get("id"))
                let id = document.getElementById("id").value
                sendNotification(id)
            } else if (res === 404) {
                div.setAttribute("class", "alert alert-danger")
                div.setAttribute("id", "alert-div")
                div.setAttribute("role", "alert")
                text = document.createTextNode("We couldn't find your package")
            } else if (res === 400) {
                div.setAttribute("class", "alert alert-danger")
                div.setAttribute("id", "alert-div")
                div.setAttribute("role", "alert")
                text = document.createTextNode("You need to enter ID")
            } else if (res === 403) {
                div.setAttribute("class", "alert alert-danger")
                div.setAttribute("id", "alert-div")
                div.setAttribute("role", "alert")
                text = document.createTextNode("You package is already collected by courier")
            }
            div.appendChild(text)
            form.insertAdjacentElement("afterend", div)
            if (res === 200) {
                setTimeout(()=>{window.location.href = "/home/"}, 1000)
            }
        })
    })

    function postPackage(formData) {
        let requestURL = baseURL + "locker/noMatter/"
        let requestParam = {
            method: "POST",
            body: formData,
            redirect: "follow"
        };

        return fetch(requestURL, requestParam).then((response) => {
            if (response.status !== null) {
                return response.status;
            } else {
                throw "Unexpected response status: " + response.status;
            }
        }).catch(err => console.log("Caught error: " + err));
    }
})