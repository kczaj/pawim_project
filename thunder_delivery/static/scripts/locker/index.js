document.addEventListener("DOMContentLoaded", (e) => {
    let baseURL = "https://localhost:8083/"
    let submitBtn = document.getElementById("submit-btn")



    submitBtn.addEventListener("click", (e) => {
        let id = document.getElementById("id")

       console.log(id.value)

        checkIfLockerExist(id).then((res) => {
            if (res === 200){
                window.location.href = "/home/"
            }
            else if(res === 404) {
                console.log("Couldnt't find locker")
            }else if(res === 400){
                console.log("Bad request")
            }
        })
    })

    function checkIfLockerExist(input) {
        let requestURL = baseURL + "locker/"+ input.value + "/";
        let requestParam = {
            method: "GET",
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