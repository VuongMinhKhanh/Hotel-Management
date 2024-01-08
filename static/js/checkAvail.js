function checkAvail() {
    const formData = new FormData(document.getElementById('formData'));
    fetch("/api/checkAvail", {
        method: "post",
        body: formData,
        // headers: {
        //     'Content-Type': 'application/json'
        // }
    }).then(function(res) {
        return res.json();
    }).then(function(data) {
        alert("Received data: " + JSON.stringify(data));
    });

}

function inform() {
    // const axios = require('axios');
    //
    // axios.get('/api/check_avail')
    // .then(function(res) {
    //     return res.json();
    // })
    // .then(function(data) {
    //     // Display a message using JavaScript, not 'alert'
    //     alert(data.message);
    // })
    alert("Hello world")
}