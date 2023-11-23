const updateBtns = document.getElementsByClassName("update-cart")


for(let i=0; i<updateBtns.length; i++) {
    updateBtns[i].addEventListener("click", function() {
        const productId = this.dataset.product
        const action = this.dataset.action

        if(user == 'AnonymousUser') {
            console.log("Not Logged in")
        } else {
            updateUserOrder(productId, action)
        }
    })
}

function updateUserOrder(productId, action) {
    let url = "/update_item/"

    fetch(url, {
        method: "POST",
        headers:{
            "Content-Type":"application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({"productId": productId, "action": action})
    })
    .then((response) => {
        return response.json()
    })
    .then((data) => {
        console.log("data:", data)
        location.reload();
    })
}