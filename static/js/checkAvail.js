function checkAvail() {
    // const formData = new FormData(document.getElementsByClassName('formData'));
    let room_type = document.getElementById("room_type")
    let quantity = document.getElementById("room_quantity")
    let cki = document.getElementById("room_checkin_day")
    let cko = document.getElementById("room_checkout_day")
    fetch("/api/checkAvail", {
        method: "post",
        body: JSON.stringify({
            "room_type": room_type.value,
            "quantity": quantity.value,
            "checkin_day": cki.value,
            "checkout_day": cko.value
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function (res) {
        return res.json();
    }).then(function (data) {
        if (JSON.parse(JSON.stringify(data))) {
            displayStep(2).click();
        } else {
            alert("Không đủ phòng")
        }
    });
}


function disableNextBtn() {
    let button = document.getElementById("btn-next-step-1")
    button.classList.add("disabled")

    button = document.getElementById("btn-next-step-1")
    // button.classList.add("disabled")
    button.addEventListener("click", function (event) {
        // Prevent the default click action
        event.preventDefault();
    });

    button = document.getElementById("btn-next-step-1")
    // button.classList.add("disabled")
    button.addEventListener("click", function (event) {
        // Prevent the default click action
        event.preventDefault();
    });

}

function enableNextBtn() {
    let button = document.getElementById("btn-next-step-1")
    button.classList.remove("disabled")

    button = document.getElementById("btn-next-step-1")
    // button.classList.remove("disabled")
    button.addEventListener("click", function (event) {
        // event.preventDefault();
    });
    button = document.getElementById("btn-next-step-1")
    // button.classList.remove("disabled")
    button.addEventListener("click", function (event) {
        // event.preventDefault();
    });
}