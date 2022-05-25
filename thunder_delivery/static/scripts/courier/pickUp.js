document.addEventListener("DOMContentLoaded", (e) => {
    const baseURL = "https://localhost:8082/"
    const webSocketURL = "https://localhost:8084"
    addEventListeners();

    function addEventListeners() {
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

        let signOut = document.getElementById("sign-out")

        signOut.addEventListener("click", (e) => {
            function logOutUser() {
                let requestURL = baseURL + "logout/";
                let requestParam = {
                    method: "POST",
                    redirect: "follow",
                    mode: 'no-cors'
                };

                return fetch(requestURL, requestParam).then((response) => {
                    if (response.status !== null) {
                        return response.status;
                    } else {
                        throw "Unexpected response status: " + response.status;
                    }
                }).catch(err => console.log("Caught error: " + err));
            }

            logOutUser().then((response) => {
                if (response === 200) {
                    window.location.href = baseURL + "home";
                }
            });
        })

        submitBtn.addEventListener("click", (e) => {
            let form = document.getElementById("package-form")

            let formData = new FormData(form)

            function sendNotification(id) {
                useragent = navigator.userAgent;
                socket.emit("join", {useragent: useragent, room_id: id});
                socket.emit("change_state", {id: id, state: "COURIER", room_id: id})
                socket.emit("leave", {useragent: useragent, room_id: id});
            }

            pickUpPackage(formData).then((response) => {
                let alertDiv = document.getElementById("alert-div")
                if (alertDiv !== null) {
                    mainDiv.removeChild(alertDiv)
                }
                let div = document.createElement("div")
                div.setAttribute("id", "alert-div")
                div.setAttribute("role", "alert")
                let text = ""
                if (response === 200) {
                    text = document.createTextNode("Correctly added package. ID:" + formData.get("id"))
                    div.setAttribute("class", "alert alert-success")
                    sendNotification(formData.get("id"))
                } else {
                    div.setAttribute("class", "alert alert-danger")
                    switch (response) {
                        case 401:
                            text = document.createTextNode("You are not authenticated")
                            break;
                        case 404:
                            text = document.createTextNode("Couldn't find package id")
                            break;
                        case 403:
                            text = document.createTextNode("Package is already picked up")
                            break;
                        default:
                            throw "Unexpected response status: " + response.status;
                    }
                }
                div.appendChild(text)
                form.insertAdjacentElement("afterend", div)
            }).catch(err => console.log("Caught error: " + err));
        })

        function pickUpPackage(formData) {
            let requestURL = baseURL + "packages/";
            let requestParam = {
                method: "POST",
                body: formData,
                redirect: "follow",
                credential: "include"
            };

            return fetch(requestURL, requestParam).then((response) => {
                if (response.status !== null) {
                    return response.status;
                } else {
                    throw "Unexpected response status: " + response.status;
                }
            }).catch(err => console.log("Caught error: " + err));
        }

    }

})