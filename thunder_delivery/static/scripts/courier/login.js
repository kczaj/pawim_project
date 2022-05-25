document.addEventListener("DOMContentLoaded", (e) => {
    const baseURL = "https://localhost:8082/"
    addEventListeners();

    function addEventListeners() {
        let signUpButton = document.getElementById("sign-in-btn")
        let mainDiv = document.getElementById("main")

        signUpButton.addEventListener("click", (e) => {
            let form = document.getElementById("login-form")

            let formData = new FormData(form)
            logInUser(formData).then((response) => {
                if (response === 200) {
                    sessionStorage.setItem("courier_id", document.getElementById("username").value + "_courier")
                    window.location.href = "user/"
                } else if (response === 401 || response === 404 || response === 400) {
                    let alertDiv = document.getElementById("alert-div")
                    if (alertDiv !== null) {
                        mainDiv.removeChild(alertDiv)
                    }
                    let div = document.createElement("div")
                    div.setAttribute("class", "alert alert-danger")
                    div.setAttribute("id", "alert-div")
                    div.setAttribute("role", "alert")
                    let text = document.createTextNode("Your username or password is wrong.")
                    div.appendChild(text)
                    form.insertAdjacentElement("afterend", div)
                }
            })
        })
    }

    function logInUser(formData) {
        let requestURL = baseURL + "login/";
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