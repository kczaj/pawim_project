document.addEventListener("DOMContentLoaded", (event) => {
    const baseURL = "https://localhost:8080/"
    addEventListeners();

    function addEventListeners() {

        let signUpButton = document.getElementById("sign-up-button")
        let registrationForm = document.getElementById("form-reg")
        let oauthBtn = document.getElementById("oauthBtn")

        signUpButton.addEventListener("click", () => {
            let loginFrame = document.getElementById("login");
            let passwordFrame = document.getElementById("password");

            verifyAllFields();

            function verifyAllFields() {

                let alertDiv = document.getElementById("alert-text")
                if (alertDiv !== null) {
                    registrationForm.removeChild(alertDiv);
                }
                let registerAlert = document.getElementById("register-text")
                if (registerAlert !== null) {
                    registrationForm.removeChild(registerAlert);
                }


                let formData = new FormData();
                formData.append("username", loginFrame.value);
                formData.append("password", passwordFrame.value);

                logInUser(formData).then((response) => {
                    if (response === 200) {
                        let warning = prepareWarning("register-text", "Log in!");
                        warning.className = "success-text";
                        signUpButton.insertAdjacentElement("beforebegin", warning)
                        window.location.href = "user";
                    } else if (response === 401 || response === 404 || response === 400) {
                        let warning = prepareWarning("register-text", "Wrong username or password");
                        warning.className = "alert-text"
                        signUpButton.insertAdjacentElement("beforebegin", warning)
                    }
                });
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
        });

        oauthBtn.addEventListener("click", (e) => {
            e.preventDefault()
            window.location.href = "/login"
        })
    }

    function prepareWarning(newElemId, message) {
        let warningField = document.getElementById(newElemId);

        if (warningField === null) {
            let textMessage = document.createTextNode(message);

            warningField = document.createElement('div');

            warningField.setAttribute("id", newElemId);
            warningField.className = "alert-text";
            let spann = document.createElement('span')
            spann.appendChild(textMessage);
            warningField.appendChild(spann);
        }
        return warningField;
    }

})