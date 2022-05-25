document.addEventListener("DOMContentLoaded", (e) => {
    const baseURL = "https://localhost:8080/"
    const dbBaseURL = "https://localhost:8081/"
    const webSocketURL = "https://localhost:8084"
    let newPackageButton = document.getElementById("new-package-button")
    let signOutButton = document.getElementById("sign-out-button")
    let link = window.location.href.split("/");
    let formReg = document.getElementById("form-reg")
    let currentPackages = []

    getAndSetPackages(dbBaseURL + "packages/0/");

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
        let id = message["id"]
        let status = message["state"]
        let td = document.getElementById(id)
        td.innerText = ""
        let text = document.createTextNode(status)
        td.appendChild(text)
        let btnDel = document.getElementById(id+"BTN")
        if(btnDel !== null){
            btnDel.remove()
        }
    });

    function connectToSockets(currentPackages) {
        currentPackages.forEach((e) => {
            useragent = navigator.userAgent;
            socket.emit("join", {useragent: useragent, room_id: e});
        })
    }

    newPackageButton.addEventListener("click", (e) => {
        console.log("here")
        window.location.href = "/home/user/newshipping";
    });

    signOutButton.addEventListener("click", (e) => {

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

    function disconnectFromSockets(currentPackages) {
        while (currentPackages.length) {
            let element = currentPackages.pop()
            useragent = navigator.userAgent;
            socket.emit("leave", {useragent: useragent, room_id: element});
        }
    }

    function getAndSetPackages(url) {
        getPackages(url).then((result) => {
            let packageDiv = document.getElementById("package-display")
            if (packageDiv !== null) {
                formReg.removeChild(packageDiv)
            }
            let packagesJson = JSON.parse(result)
            let packagesList = packagesJson["packages"]
            let tableDiv = document.getElementById("table-div")
            tableDiv.innerHTML = ""
            let navDiv = document.getElementById("nav-div")
            navDiv.innerHTML = ""
            let newPackageBtn = document.getElementById("new-package-button")
            let div = document.createElement("div")
            div.setAttribute("class", "package-display")
            div.setAttribute("id", "package-display")
            let packageAmount = document.createElement("span")
            let textField = document.createTextNode("PACKAGES: " + packagesList.length)
            packageAmount.appendChild(textField)
            div.appendChild(packageAmount)
            newPackageBtn.insertAdjacentElement("afterend", div)
            if (packagesList.length !== 0) {
                let packageTable = document.createElement("table")
                let tbody = document.createElement("tbody")

                let row = tbody.insertRow()
                let cell = row.insertCell()
                let th = document.createElement("th")
                let text = document.createTextNode("ID")
                th.appendChild(text)
                cell.appendChild(th)

                cell = row.insertCell()
                th = document.createElement("th")
                text = document.createTextNode("CREATED")
                th.appendChild(text)
                cell.appendChild(th)

                cell = row.insertCell()
                th = document.createElement("th")
                text = document.createTextNode("STATUS")
                th.appendChild(text)
                cell.appendChild(th)

                packagesList.sort().forEach((element) => {
                    let package = JSON.parse(element)
                    let newRow = tbody.insertRow()

                    let newCell = newRow.insertCell()
                    let newText = document.createTextNode(package["id"]);
                    newCell.appendChild(newText);

                    newCell = newRow.insertCell()
                    newText = document.createTextNode(package["created"].split(".")[0]);
                    newCell.appendChild(newText);

                    newCell = newRow.insertCell()
                    newCell.setAttribute("id", package["id"])
                    newText = document.createTextNode(package["status"]);
                    newCell.appendChild(newText);

                    newCell = newRow.insertCell()
                    let form = document.createElement("form")
                    form.setAttribute("action", dbBaseURL + "pdf/" + package["id"])
                    form.setAttribute("method", "GET")
                    let input = document.createElement("input")
                    input.setAttribute("type", "submit")
                    input.setAttribute("value", "DOWNLOAD")
                    input.setAttribute("class", "download-button")
                    form.appendChild(input)
                    newCell.appendChild(form)

                    if (package["status"] === "NEW") {
                        newCell = newRow.insertCell()
                        newCell.setAttribute("id", package["id"]+"BTN")
                        input = document.createElement("input")
                        input.setAttribute("type", "submit")
                        input.setAttribute("value", "DELETE")
                        input.setAttribute("class", "delete-button")
                        input.addEventListener("click", (e) => {
                            deletePackage(package["id"]).then((r) => {
                                window.location.href = "user"
                            })
                        })
                        newCell.appendChild(input)
                    }

                    currentPackages.push(package["id"])
                });
                let next_url = packagesJson["next_url"]
                let prev_url = packagesJson["prev_url"]
                packageTable.appendChild(tbody)
                tableDiv.appendChild(packageTable)
                if (prev_url !== "") {
                    let div = document.createElement("div")
                    div.setAttribute("class", "prev-button-div")
                    input = document.createElement("input")
                    input.setAttribute("type", "submit")
                    input.setAttribute("value", "PREV")
                    input.setAttribute("class", "download-button")
                    input.addEventListener("click", (e) => {
                        disconnectFromSockets(currentPackages)
                        getAndSetPackages(prev_url)
                    })
                    div.appendChild(input)
                    navDiv.appendChild(div)
                }
                if (next_url !== "") {
                    div = document.createElement("div")
                    div.setAttribute("class", "next-button-div")
                    input = document.createElement("input")
                    input.setAttribute("type", "submit")
                    input.setAttribute("value", "NEXT")
                    input.setAttribute("class", "download-button")
                    input.addEventListener("click", (e) => {
                        disconnectFromSockets(currentPackages)
                        getAndSetPackages(next_url)
                    })
                    div.appendChild(input)
                    navDiv.appendChild(div)
                }

                connectToSockets(currentPackages)

            } else {
                let span = document.createElement("h3")
                let text = document.createTextNode("Seems like you don't have any package yet.")
                span.appendChild(text)
                tableDiv.appendChild(span)
            }
        });

    }

    function deletePackage(id) {
        console.log(id)
        let requestURl = dbBaseURL + "pdf/" + id;
        let requestParam = {
            method: "delete",
            mode: "cors",
            redirect: "follow",
            credentials: 'include'
        };

        return fetch(requestURl, requestParam).then((response) => {
            return response.status
        }).catch(err => console.log("Caught error: " + err));

    }


    function getPackages(url) {

        let requestURL = url
        let requestParam = {
            method: "GET",
            mode: "cors",
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

});