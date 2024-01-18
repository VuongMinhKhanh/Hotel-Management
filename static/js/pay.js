function pay() {
    // room_type, booker, start_date, end_date, price
    // const form = new FormData(document.getElementById("receipt"))
    // if (confirm("Bạn chắc chắn thanh toán!") === true) {
    //     fetch("/api/pay", {
    //         method: "post"
    //     }).then(res => res.json()).then(data => {
    //         if (data.status === 200)
    //             location.reload();
    //         else
    //             alert(data.err_msg)
    //     })
    // }
    fetch("/api/pay", {
        method: "post",
        // body: JSON.stringify({
        //     "room_type": room_type,
        //     "booker": booker,
        //     "start_date": start_date,
        //     "end_date": end_date,
        //     "price": price,
        // })
    }).then(res => res.json())
    .then(data => {
        // alert(JSON.parse(JSON.stringify(data)))
        // location.reload();

        location.reload()
    })
}
