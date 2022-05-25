document.addEventListener("DOMContentLoaded", (e) => {
    const baseURL = "https://localhost:8082/"
    addEventListeners();


    function addEventListeners() {
        let submitBtn = document.getElementById("submit-btn")
        let mainDiv = document.getElementById("main")
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

        submitBtn.addEventListener("click", async (e) => {
            let form = document.getElementById("package-form")
            let input = document.getElementById("name")

            let alertDiv = document.getElementById("alert-div")
            if (alertDiv !== null) {
                mainDiv.removeChild(alertDiv)
            }
            let alertContent = document.createElement("div")
            alertContent.setAttribute("id", "alert-div")
            alertContent.setAttribute("role", "alert")
            let text;
            try {
                let response = await grantAccess(input)
                text = document.createTextNode("Access granted. TOKEN:" + response["token"])
                alertContent.setAttribute("class", "alert alert-success")
            } catch (error) {
                alertContent.setAttribute("class", "alert alert-danger")
                switch (error) {
                    case 401:
                        text = document.createTextNode("You are not authenticated")
                        break;
                    case 400:
                        text = document.createTextNode("Couldn't find locker")
                        break;
                    default:
                        text = document.createTextNode("Unexpected response status: " + error);
                }
            } finally {
                alertContent.appendChild(text)
                form.insertAdjacentElement("afterend", alertContent)
            }

        })


        async function grantAccess(input) {
            let requestURL = baseURL + "access/" + input.value + "/";
            let requestParam = {
                method: "GET",
                redirect: "follow",
                credential: "include"
            };

            let res = await fetch(requestURL, requestParam)
            if (res.status === 200) {
                return await res.json()
            } else {
                throw res.status
            }
        }

    }

})