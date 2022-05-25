document.addEventListener("DOMContentLoaded", (e) => {
    const dbBaseURL = "https://localhost:8081/"
    const baseURL = "https://localhost:8080/"
    let createButton = document.getElementById("create-button");
    let registrationForm = document.getElementById("form-reg");
    let signOutButton = document.getElementById("sign-out-button");

    signOutButton.addEventListener("click", (e) => {

        function logOutUser() {
            let requestURL = baseURL + "logout/";
            let requestParam = {
                method: "POST",
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

        logOutUser().then((response) => {
            if (response === 200) {
                window.location.href = baseURL + "home";
            }
        });

    })

    createButton.addEventListener("click", (e) => {
        let senderNameFrame = document.getElementById("name_sender")
        let senderSurnameFrame = document.getElementById("surname_sender")
        let senderStreetFrame = document.getElementById("street_sender")
        let senderNumberFrame = document.getElementById("number_sender")
        let senderCodeFrame = document.getElementById("code_sender")
        let senderPhoneNumberFrame = document.getElementById("phone_number_sender")
        let receiverNameFrame = document.getElementById("name_receiver")
        let receiverSurnameFrame = document.getElementById("surname_receiver")
        let receiverStreetFrame = document.getElementById("street_receiver")
        let receiverNumberFrame = document.getElementById("number_receiver")
        let receiverCodeFrame = document.getElementById("code_receiver")
        let receiverPhoneNumberFrame = document.getElementById("phone_number_receiver")
        let photoInput = document.getElementById("image_receiver")

        let responseMap = {
            BAD_NAME_FORMAT: "Your name must contains only letters",
            BAD_SURNAME_FORMAT: "Your surname must contains only letters",
            BAD_STREET_FORMAT: "Your street name can not have any special characters",
            BAD_NUMBER_FORMAT: "Your street number must be number",
            BAD_CODE_FORMAT: "Your code number has wrong format",
            BAD_PHONE_FORMAT: "Your phone number must contains 9 digits and format must be DDDDDDDDD",
            BAD_FILE_FORMAT: "You must add photo"
        }
        verifyAllFields();



        function verifyAllFields() {
            let responseString = "";

            responseString += verifyName();
            responseString += verifySurname();
            responseString += verifyStreetName();
            responseString += verifyNumber();
            responseString += verifyCodeNumber();
            responseString += verifyPhoneNumber();
            responseString += verifyPhoto();

            let alertDiv = document.getElementById("alert-text")
            if (alertDiv !== null) {
                registrationForm.removeChild(alertDiv);
            }
            let registerAlert = document.getElementById("register-text")
            if (registerAlert !== null) {
                registrationForm.removeChild(registerAlert);
            }

            if (responseString === "") {
                let formData = new FormData();
                formData.append("sender_name", senderNameFrame.value);
                formData.append("sender_surname", senderSurnameFrame.value);
                formData.append("sender_street", senderStreetFrame.value);
                formData.append("sender_number", senderNumberFrame.value);
                formData.append("sender_code", senderCodeFrame.value);
                formData.append("sender_phone", senderPhoneNumberFrame.value);
                formData.append("receiver_name", receiverNameFrame.value);
                formData.append("receiver_surname", receiverSurnameFrame.value);
                formData.append("receiver_street", receiverStreetFrame.value);
                formData.append("receiver_number", receiverNumberFrame.value);
                formData.append("receiver_code", receiverCodeFrame.value);
                formData.append("receiver_phone", receiverPhoneNumberFrame.value);
                formData.append("photo", photoInput.files[0])

                registerNewPackage(formData).then((response) => {
                    if (response === true) {
                        let warning = prepareWarning("register-text", "Created package successfully!");
                        warning.className = "success-text";
                        createButton.insertAdjacentElement("beforebegin", warning)
                        window.location.href = "/home/user"
                    } else if (response === false) {
                        let warning = prepareWarning("register-text", "Something went wrong");
                        warning.className = "alert-text"
                        createButton.insertAdjacentElement("beforebegin", warning)
                    }
                });
            } else if (responseString !== "") {
                let warning = prepareWarning("alert-text", responseString);
                createButton.insertAdjacentElement("beforebegin", warning)
            }

            function verifyName() {
                let valueSender = senderNameFrame.value + '';
                let valueReceiver = receiverNameFrame.value + '';
                let returnString = "";

                if (!/^[a-zA-Z]+$/.test(valueSender)) {
                    returnString += responseMap.BAD_NAME_FORMAT + " in SENDER section. ";
                }

                if (!/^[a-zA-Z]+$/.test(valueReceiver)) {
                    returnString += responseMap.BAD_NAME_FORMAT + " in RECEIVER section. ";
                }

                return returnString;
            }

            function verifySurname() {
                let valueSender = senderSurnameFrame.value + '';
                let valueReceiver = receiverSurnameFrame.value + '';
                let returnString = "";

                if (!/^[a-zA-Z]+$/.test(valueSender)) {
                    returnString += responseMap.BAD_SURNAME_FORMAT + " in SENDER section. ";
                }

                if (!/^[a-zA-Z]+$/.test(valueReceiver)) {
                    returnString += responseMap.BAD_SURNAME_FORMAT + " in RECEIVER section. ";
                }

                return returnString;
            }

            function verifyStreetName() {
                let valueSender = senderStreetFrame.value + '';
                let valueReceiver = receiverStreetFrame.value + '';
                let returnString = "";

                if (!/^[a-zA-Z\d.-]+$/.test(valueSender)) {
                    returnString += responseMap.BAD_STREET_FORMAT + " in SENDER section. ";
                }

                if (!/^[a-zA-Z\d.-]+$/.test(valueReceiver)) {
                    returnString += responseMap.BAD_STREET_FORMAT + " in RECEIVER section. ";
                }

                return returnString;
            }

            function verifyNumber() {
                let valueSender = senderNumberFrame.value + '';
                let valueReceiver = receiverNumberFrame.value + '';
                let returnString = "";

                if (!/^\d+$/.test(valueSender)) {
                    returnString += responseMap.BAD_NUMBER_FORMAT + " in SENDER section. ";
                }

                if (!/^\d+$/.test(valueReceiver)) {
                    returnString += responseMap.BAD_NUMBER_FORMAT + " in RECEIVER section. ";
                }

                return returnString;
            }

            function verifyCodeNumber() {
                let valueSender = senderCodeFrame.value + '';
                let valueReceiver = receiverCodeFrame.value + '';
                let returnString = "";

                if (!/^\d{2}[-]\d{3}$/.test(valueSender)) {
                    returnString += responseMap.BAD_CODE_FORMAT + " in SENDER section. ";
                }

                if (!/^\d{2}[-]\d{3}$/.test(valueReceiver)) {
                    returnString += responseMap.BAD_CODE_FORMAT + " in RECEIVER section. ";
                }

                return returnString;
            }

            function verifyPhoneNumber() {
                let valueSender = senderPhoneNumberFrame.value + '';
                let valueReceiver = receiverPhoneNumberFrame.value + '';
                let returnString = "";

                if (!/^\d{9}$/.test(valueSender)) {
                    returnString += responseMap.BAD_PHONE_FORMAT + " in SENDER section. ";
                }

                if (!/^\d{9}$/.test(valueReceiver)) {
                    returnString += responseMap.BAD_PHONE_FORMAT + " in RECEIVER section. ";
                }

                return returnString;
            }

            function verifyPhoto() {
                let returnString = "";

                if(photoInput.files.length === 0){
                    returnString += responseMap.BAD_FILE_FORMAT + ' '
                }

                return returnString;
            }

            function registerNewPackage(formData) {
                let requestURl = dbBaseURL + "packages/add/";
                let requestParam = {
                    method: "POST",
                    body: formData,
                    mode: "cors",
                    redirect: "follow",
                    credentials: 'include'
                };


                return fetch(requestURl, requestParam).then((response) => {
                    if (response.status === 201) {
                        return true;
                    } else if (response === 400) {
                        return false
                    } else {
                        throw "Unexpected response status: " + response.status;
                    }
                }).catch(err => console.log("Caught error: " + err));
            }
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

    });
});