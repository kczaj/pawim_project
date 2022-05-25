document.addEventListener("DOMContentLoaded", (e) => {
    const baseURL = "https://localhost:8083/"
    const webSocketURL = "https://localhost:8084"
    let takePackageList = []
    let submitButton = document.getElementById("submit-btn")
    let cookies = document.cookie.split(";")
    let courier_id = ""

    cookies.forEach((cookie) => {
        console.log(cookie)
        if (cookie.includes("courier_id")) {
            courier_id = cookie.split("=")[1]
        }
    })

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

    socket.on("change_state_message", function (message) {
        console.log("Left the room ", message);
    });

    getAndSetPackages(baseURL + "packages/0/");

    joinRoom()

    function joinRoom() {
        useragent = navigator.userAgent;
        socket.emit("join", {useragent: useragent, room_id: courier_id});
    }

    function getAndSetPackages(url) {
        getPackages(url).then(async (response) => {
            let table = document.getElementById("table")
            let tbodyEle = document.getElementById("tbody")
            let ul_next = document.getElementById("next-ul")
            let next_li = document.getElementById("next-li")
            if (next_li !== null) {
                ul_next.removeChild(next_li)
            }
            let ul_prev = document.getElementById("prev-ul")
            let prev_li = document.getElementById("prev-li")
            if (prev_li !== null) {
                ul_prev.removeChild(prev_li)
            }
            if (tbodyEle !== null) {
                table.removeChild(tbodyEle)
            }
            let json = JSON.parse(response)
            let packageList = json["packages"]
            let tbody = document.createElement("tbody")
            tbody.setAttribute("id", "tbody")
            packageList.forEach((element) => {
                let package = JSON.parse(element)
                let newRow = tbody.insertRow()
                let newCell = newRow.insertCell()
                let text = document.createTextNode(package["id"])
                newCell.appendChild(text)

                newCell = newRow.insertCell()
                let checkBox = document.createElement("input")
                checkBox.setAttribute("class", "form-check-input")
                checkBox.setAttribute("type", "checkbox")
                if (takePackageList.includes(package["id"])) {
                    checkBox.checked = true
                }
                newCell.appendChild(checkBox)
                checkBox.addEventListener("click", (e) => {
                    let id = package["id"]
                    if (checkBox.checked === true) {
                        takePackageList.push(id)
                    } else {
                        takePackageList = takePackageList.filter((ele) => {
                            return ele !== id
                        })
                    }
                })
            })
            table.appendChild(tbody)
            let next_url = json["next_url"]
            let prev_url = json["prev_url"]

            if (prev_url !== "") {
                let li = document.createElement("li")
                li.setAttribute("class", "page-item")
                li.setAttribute("id", "prev-li")
                let a = document.createElement("a")
                a.setAttribute("class", "page-link")
                let text = document.createTextNode("<<")
                a.appendChild(text)
                a.addEventListener("click", (e) => {
                    getAndSetPackages(prev_url)
                })
                li.appendChild(a)
                ul_prev.appendChild(li)
            }
            if (next_url !== "") {
                let li = document.createElement("li")
                li.setAttribute("class", "page-item")
                li.setAttribute("id", "next-li")
                let a = document.createElement("a")
                a.setAttribute("class", "page-link")
                let text = document.createTextNode(">>")
                a.appendChild(text)
                a.addEventListener("click", (e) => {
                    getAndSetPackages(next_url)
                })
                li.appendChild(a)
                ul_next.appendChild(li)
            }
        })
    }

    function sendNotification(element) {
        console.log(element)
        useragent = navigator.userAgent;
        socket.emit("join", {useragent: useragent, room_id: element});
        socket.emit("change_state", {id: element, state: "COURIER_L", room_id: element})
        socket.emit("leave", {useragent: useragent, room_id: element});
        socket.emit("package_remove", {id: element, state: "COURIER_L", room_id: courier_id})
    }

    submitButton.addEventListener("click", (e) => {
        try {
            takePackageList.forEach(async (element) => {
                let status = await removePackageFromLocker(element)
                if (status !== 200) {
                    throw status
                }

            })
            takePackageList.forEach((e) => {
                sendNotification(e)
            })
            setTimeout(() => {
                window.location.href = "/home/"
            }, 10000)
        } catch (error) {
            console.log("Unexpected response status: " + error)
        }


    })

    async function removePackageFromLocker(id) {
        let requestURL = baseURL + "packages/" + id + "/"
        let requestParam = {
            method: "POST",
            redirect: "follow",
            credentials: 'include'
        };

        let res = await fetch(requestURL, requestParam)
        return res.status
    }

    async function getPackages(url) {
        let requestURL = url
        let requestParam = {
            method: "GET",
            redirect: "follow",
            credentials: 'include'
        };

        return await fetch(requestURL, requestParam).then((response) => {
            if (response.status === 200) {
                return response.text().then((value) => {
                    return value;
                });
            } else {
                return null;
            }
        }).catch(err => console.log("Caught error: " + err));

    }
})