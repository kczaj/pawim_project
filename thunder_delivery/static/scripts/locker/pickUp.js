document.addEventListener("DOMContentLoaded", (e) => {
    const baseURL = "https://localhost:8083/"
    let lockerId = window.location.href.split("/")[4]
    addEventListeners();

    function addEventListeners() {
        let submitBtn = document.getElementById("submit-btn")
        let mainDiv = document.getElementById("main")

        submitBtn.addEventListener("click", async (e) => {
            let form = document.getElementById("token-form")
            let input = document.getElementById("token")

            let alertDiv = document.getElementById("alert-div")
            if (alertDiv !== null) {
                mainDiv.removeChild(alertDiv)
            }
            let alertContent = document.createElement("div")
            alertContent.setAttribute("id", "alert-div")
            alertContent.setAttribute("role", "alert")
            let text;
            try {
                await grantAccess(input)
                text = document.createTextNode("Access granted.")
                alertContent.setAttribute("class", "alert alert-success")
                window.location.href = "/home/list/"
            } catch (error) {
                alertContent.setAttribute("class", "alert alert-danger")
                switch (error) {
                    case 403:
                        text = document.createTextNode("Invalid token")
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
            let requestURL = baseURL + "locker/" + lockerId + "/access/" + input.value + "/";
            let requestParam = {
                method: "GET",
                redirect: "follow",
                credential: "include"
            };

            let res = await fetch(requestURL, requestParam)
            if (res.status === 200) {
                return res.status
            } else {
                throw res.status
            }
        }

    }

})