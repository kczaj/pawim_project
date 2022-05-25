document.addEventListener("DOMContentLoaded", (event) => {
    const baseURL = "https://localhost:8080/"
    addEventListeners();
    let isLoginFree = true;

    function addEventListeners() {

        let loginFrame = document.getElementById("login");
        let signUpButton = document.getElementById("sign-up-button")
        let registrationForm = document.getElementById("form-reg")

        loginFrame.addEventListener("change", () => {
            let alertDiv = document.getElementById("alert-text-login")
            if (alertDiv !== null) {
                registrationForm.removeChild(alertDiv);
            }
            isLoginAvailable().then((response) => {
                if (!response) {
                    let warning = prepareWarning("alert-text-login", "Warning! This login is already taken.");
                    signUpButton.insertAdjacentElement("beforebegin", warning)
                    isLoginFree = false;
                } else {
                    isLoginFree = true
                }
            })

            function isLoginAvailable() {
                let requestURL = baseURL + "username/" + loginFrame.value;
                let form = new FormData
                form.append("username", loginFrame.value)
                let requestParam = {
                    method: "GET"
                }
                return fetch(requestURL, requestParam).then((response) => {
                    if (response.status == 200) {
                        return false;
                    } else if (response.status == 404) {
                        return true;
                    } else {
                        throw "Unexpected response status: " + response.status;
                    }
                }).catch(err => console.log("Caught error: " + err));
            }
        });

        signUpButton.addEventListener("click", () => {
            let loginFrame = document.getElementById("login");
            let passwordFrame = document.getElementById("password");
            let secondPasswordFrame = document.getElementById("second_password");
            let peselFrame = document.getElementById("pesel");
            let nameFrame = document.getElementById("name");
            let surnameFrame = document.getElementById("surname");
            let birthDateFrame = document.getElementById("birth_date");
            let streetFrame = document.getElementById("street");
            let numberFrame = document.getElementById("number");
            let codeFrame = document.getElementById("code");
            let countryFrame = document.getElementById("country");

            let responseMap = {
                TO_SHORT_LOGIN: "Your login must be longer than 5 letters.",
                BAD_LOGIN_FORMAT: "Your login must contain only letters.",
                BAD_PESEL: "Your PESEL number is wrong.",
                NOT_SAME_PASSWORD: "Your password and repeated password cannot be different.",
                BAD_PASSWORD_FORMAT: "Your password must contain minimum 8 characters (uppercase and lowercase letters, digits, special characters (!@#$%&*))",
                BAD_NAME_FORMAT: "Your name must contains only letters.",
                BAD_SURNAME_FORMAT: "Your surname must contains only letters.",
                BAD_DATE_FORMAT: "Your date has wrong format.",
                BAD_STREET_FORMAT: "Your street name can not have any special characters.",
                BAD_NUMBER_FORMAT: "Your street number must be number.",
                BAD_CODE_FORMAT: "Your code number has wrong format.",
                BAD_COUNTRY_FORMAT: "Your country name must contain only letters."
            }
            verifyAllFields();

            function verifyAllFields() {
                let responseString = "";
                responseString += verifyLogin();
                responseString += verifyPassword();
                responseString += verifyPesel();
                responseString += verifyName();
                responseString += verifySurname();
                responseString += verifyBirthDate();
                responseString += verifyStreetName();
                responseString += verifyNumber();
                responseString += verifyCodeNumber();
                responseString += verifyCountryName();

                let alertDiv = document.getElementById("alert-text")
                if (alertDiv !== null) {
                    registrationForm.removeChild(alertDiv);
                }
                let registerAlert = document.getElementById("register-text")
                if (registerAlert !== null) {
                    registrationForm.removeChild(registerAlert);
                }

                if (responseString === "" && isLoginFree === true) {
                    let formData = new FormData();
                    formData.append("username", loginFrame.value);
                    formData.append("password", passwordFrame.value);
                    formData.append("second_password", secondPasswordFrame.value);
                    formData.append("pesel", peselFrame.value);
                    formData.append("name", nameFrame.value);
                    formData.append("surname", surnameFrame.value);
                    formData.append("birth_date", birthDateFrame.value);
                    formData.append("street", streetFrame.value);
                    formData.append("number", numberFrame.value);
                    formData.append("code", codeFrame.value);
                    formData.append("country", countryFrame.value);

                    registerNewUser(formData).then((response) => {
                        if (response === "201") {
                            let warning = prepareWarning("register-text", "Signed up successfully!");
                            warning.className = "success-text";
                            signUpButton.insertAdjacentElement("beforebegin", warning)
                            window.location.href = "user"
                            isLoginFree = false;
                        }
                        else if(response === "400"){
                            let warning = prepareWarning("register-text", "Login is already taken");
                            warning.className = "alert-text"
                            signUpButton.insertAdjacentElement("beforebegin", warning)
                        }
                    });
                } else if (responseString !== "") {
                    let warning = prepareWarning("alert-text", responseString);
                    signUpButton.insertAdjacentElement("beforebegin", warning)
                }
            }

            function verifyLogin() {
                let value = loginFrame.value + '';
                let returnString = "";

                if (!/^[a-zA-Z]+$/.test(value)) {
                    returnString += responseMap.BAD_LOGIN_FORMAT + " ";
                }
                if (value.length <= 4) {
                    returnString += responseMap.TO_SHORT_LOGIN + " ";
                }
                return returnString;
            }

            function verifyPassword() {
                let value1 = passwordFrame.value + '';
                let value2 = secondPasswordFrame.value + '';
                let returnString = "";

                if (value1 != value2) {
                    returnString += responseMap.NOT_SAME_PASSWORD + " ";
                }
                if (value1 < 8 || !/\d/.test(value1) || !/[a-z]/.test(value1) || !/[A-Z]/.test(value1) || !/[!@#$%&*]/.test(value1)) {
                    returnString += responseMap.BAD_PASSWORD_FORMAT + " ";
                }
                return returnString;
            }

            function verifyPesel() {
                let value = peselFrame.value + '';
                let returnString = "";

                if (value.length == 11) {
                    let result = 9 * value.charAt(0) + 7 * value.charAt(1) + 3 * value.charAt(2) + 1 * value.charAt(3) + 9 * value.charAt(4) + 7 * value.charAt(5) + 3 * value.charAt(6) + 1 * value.charAt(7) + 9 * value.charAt(8) + 7 * value.charAt(9);
                    let expected = value.charAt(10)
                    if (expected != result % 10) {
                        returnString += responseMap.BAD_PESEL + " ";
                    }
                } else {
                    returnString += responseMap.BAD_PESEL + " ";
                }
                return returnString;
            }

            function verifyName() {
                let value = nameFrame.value + '';
                let returnString = "";

                if (!/^[a-zA-Z]+$/.test(value)) {
                    returnString = responseMap.BAD_NAME_FORMAT + " ";
                }

                return returnString;
            }

            function verifySurname() {
                let value = surnameFrame.value + '';
                let returnString = "";

                if (!/^[a-zA-Z]+$/.test(value)) {
                    returnString = responseMap.BAD_SURNAME_FORMAT + " ";
                }

                return returnString;
            }

            function verifyBirthDate() {
                let value = birthDateFrame.value + '';
                let returnString = "";

                if (!/^\d{2}[/]\d{2}[/]\d{4}$/.test(value)) {
                    returnString = responseMap.BAD_DATE_FORMAT + " ";
                }

                return returnString;
            }

            function verifyStreetName() {
                let value = streetFrame.value + '';
                let returnString = "";

                if (!/^[a-zA-Z\d.-]+$/.test(value)) {
                    returnString = responseMap.BAD_STREET_FORMAT + " ";
                }

                return returnString;
            }

            function verifyNumber() {
                let value = numberFrame.value + '';
                let returnString = "";

                if (!/^\d+$/.test(value)) {
                    returnString = responseMap.BAD_NUMBER_FORMAT + " ";
                }

                return returnString;
            }

            function verifyCodeNumber() {
                let value = codeFrame.value + '';
                let returnString = "";

                if (!/^\d{2}[-]\d{3}$/.test(value)) {
                    returnString = responseMap.BAD_CODE_FORMAT + " ";
                }

                return returnString;
            }

            function verifyCountryName() {
                let value = countryFrame.value + '';
                let returnString = "";

                if (!/^[a-zA-Z]+$/.test(value)) {
                    returnString = responseMap.BAD_COUNTRY_FORMAT + " ";
                }

                return returnString;
            }

            function registerNewUser(formData) {
                let requestURL = baseURL + "register/";
                let requestParam = {
                    method: "POST",
                    body: formData,
                    redirect: "follow"
                };

                return fetch(requestURL, requestParam).then((response) => {
                    if (response.status === 201) {
                        return "201";
                    } else if (response.status === 400) {
                        return "400";
                    }
                    else {
                        throw "Unexpected response status: " + response.status;
                    }
                }).catch(err => console.log("Caught error: " + err));
            }
        });


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