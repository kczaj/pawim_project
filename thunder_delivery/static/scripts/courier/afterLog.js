document.addEventListener("DOMContentLoaded", (e) => {
    const baseURL = "https://localhost:8082/"
    const webSocketURL = "https://localhost:8084"
    let currentURL = baseURL + "packages/0/"
    let signOut = document.getElementById("sign-out")
    let cookies = document.cookie.split(";")

    cookies.forEach((cookie) => {
        console.log(cookie)
        if (cookie.includes("courier_id")) {
            if (cookie.includes("_courier")) {
                sessionStorage.setItem("courier_id", cookie.split("=")[1])
            } else {
                sessionStorage.setItem("courier_id", cookie.split("=")[1] + "_courier_oauth")
            }

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

    socket.on("change_package", function (message) {
        getAndSetPackages(currentURL)
    })

    getAndSetPackages(baseURL + "packages/0/");

    function joinRoom() {
        useragent = navigator.userAgent;
        socket.emit("join", {useragent: useragent, room_id: sessionStorage.getItem("courier_id")});
    }

    joinRoom();

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

    function getAndSetPackages(url) {
        getPackages(url).then((response) => {
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
                text = document.createTextNode(package["street"] + " " + package["number"])
                newCell.appendChild(text)

                newCell = newRow.insertCell()
                text = document.createTextNode(package["code"])
                newCell.appendChild(text)
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
                    currentURL = prev_url
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
                    currentURL = next_url
                    getAndSetPackages(next_url)
                })
                li.appendChild(a)
                ul_next.appendChild(li)
            }
            currentPackageCount = packageList.length
        })
    }

    function getPackages(url) {
        let requestURL = url
        let requestParam = {
            method: "GET",
            redirect: "follow",
            credentials: 'include'
        };

        return fetch(requestURL, requestParam).then((response) => {
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