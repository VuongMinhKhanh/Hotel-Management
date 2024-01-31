function bookrooms() {
    if (confirm("Bạn có muốn đặt phòng?")) {
        fetch("/api/bookrooms", {
            method: "post"
        }).then(function (res) {
            window.location.href = "/"
            return res.json();
        })
    }

}

function addCustomer() {
    var table = document.getElementById('customerTable')
    // var customer = new FormData(document.getElementById('customerData'));
    var customer = {
        "fname": document.getElementById('fname').value,
        "lname": document.getElementById('lname').value,
        "cccd": document.getElementById('cccd').value,
        "type": document.getElementById('type').value,
        "phoneNumber": document.getElementById('phoneNumber').value,
        "email": document.getElementById('email').value,
        "addr": document.getElementById('addr').value
    }

    for (let i = 1, row; row = table.rows[i]; i++) {
        if (row.cells[2].innerText == customer["cccd"]) {
            alert("Đã có khách hàng")
            return
        }
    }
    // alert(customer.get("name"))
    var row = table.insertRow()
    var cell0 = row.insertCell(0)
    var cell1 = row.insertCell(1)
    var cell2 = row.insertCell(2)
    var cell3 = row.insertCell(3)
    var cell4 = row.insertCell(4)
    var cell5 = row.insertCell(5)
    var cell6 = row.insertCell(6)
    var cell7 = row.insertCell(7)

    cell0.setAttribute("onclick", "adjustInfo(this)");
    cell1.setAttribute("onclick", "adjustInfo(this)");
    cell2.setAttribute("onclick", "adjustInfo(this)");
    cell3.setAttribute("onclick", "adjustInfo(this)");
    cell4.setAttribute("onclick", "adjustInfo(this)");
    cell5.setAttribute("onclick", "adjustInfo(this)");
    cell6.setAttribute("onclick", "adjustInfo(this)");

    cell0.innerText = customer["fname"];
    cell1.innerText = customer["lname"]
    cell2.innerText = customer["cccd"];
    if (customer["type"] == "noi_dia") {
        cell3.innerText = "Nội địa";
    } else {
        cell3.innerText = "Nước ngoài";
    }
    cell4.innerText = customer["addr"];
    cell5.innerText = customer["phoneNumber"];
    cell6.innerText = customer["email"];
    cell7.innerHTML = "<button onclick='removeCustomer(this)'>X</button>"
}


function adjustInfo(td) {
    var newInfo = prompt("Nhập thông tin cần sửa", td.innerText)
    if (newInfo != null) {
        td.innerText = newInfo
    }
}


function removeCustomer(button) {
    button.closest("tr").remove()
}


function retrieveCustomer() {
    var table = document.getElementById("customerTable");
    const customers = [];
    let booker = {};
    let customerTab = document.querySelector(".step-2 .tab-content")

    if (customerTab != null) {
        booker = {
            "fname": document.getElementById("booker_fname").value,
            "lname": document.getElementById("booker_lname").value,
            "cccd": document.getElementById("booker_cccd").value,
            "addr": document.getElementById("booker_addr").value,
            "phoneNum": document.getElementById("booker_phoneNumber").value,
            "email": document.getElementById("booker_email").value,
            "booker_type": "Khách hàng"
        }
    }

    for (let i = 1; i < table.rows.length; i++) {
        let row = table.rows[i];
        let fname = row.cells[0].innerText;
        let lname = row.cells[1].innerText;
        let cccd = row.cells[2].innerText;
        let type = row.cells[3].innerText;
        let addr = row.cells[4].innerText;
        let phoneNum = row.cells[5].innerText;
        let email = row.cells[6].innerText;

        let customer = {
            "fname": fname,
            "lname": lname,
            "cccd": cccd,
            "type": type,
            "addr": addr,
            "phoneNum": phoneNum,
            "email": email
        };
        customers.push(customer)
    }

    fetch("/api/retrieveCustomer", {
        method: "post",
        body: JSON.stringify({
            booker: booker,
            customers: customers
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function (res) {
        return res.json();
    }).then(function (data) {
        if (data === false) {
            alert("Không đủ phòng (mỗi phòng chỉ ở tối đa 3 người")
        } else {
            displayStep(3)

            let form = document.getElementById("last-step")
            // step 1
            form.querySelector("#room_type").value = data[0]["info"]["room_type"]
            form.querySelector("#room_quantity").value = data[0]["info"]["avail_rooms"].length
            form.querySelector("#checkin").value = data[0]["info"]["start_date"].join("-")
            form.querySelector("#checkout").value = data[0]["info"]["end_date"].join("-")

            // step 2
            let booker = data[2]["booker"]
            if (booker["booker_type"] == "Khách hàng") {
                form.querySelector("#booker_fname").value = booker["fname"]
                form.querySelector("#booker_lname").value = booker["lname"]
                form.querySelector("#booker_cccd").value = booker["cccd"]
                form.querySelector("#booker_phoneNumber").value = booker["phoneNum"]
                form.querySelector("#booker_email").value = booker["email"]
                form.querySelector("#booker_addr").value = booker["addr"]

            }
            else {
                form.querySelector("#booker_recep").value = booker["full_name"]
            }

            // step 3
            let sourceTable = document.querySelector(".step.step-2 #customerTable")
            let destinationTable = form.querySelector("#customerTable")
            let clonedTable = sourceTable.cloneNode(true)

            destinationTable.innerHTML = ""
            destinationTable.appendChild(clonedTable.querySelector("thead"))
            destinationTable.appendChild(clonedTable.querySelector("tbody"))

            let lastColumnIndex = destinationTable.rows[0].cells.length - 1
            Array.from(destinationTable.rows).forEach(row => {
                row.deleteCell(lastColumnIndex);
            });
        }
    });
}

// var currentId = 1;
//
//   function addRow() {
//     var table = document.getElementById("myTable").getElementsByTagName('tbody')[0];
//     var newRow = table.insertRow();
//
//     // Create cells
//     var cellId = newRow.insertCell(0);
//     var cellName = newRow.insertCell(1);
//     // Other cells...
//
//     // Set cell content
//     cellId.innerHTML = currentId++;
//     cellName.innerHTML = "New Name"; // You can set the default value
//
//     // Add a button for row removal
//     var cellAction = newRow.insertCell(2);
//     var removeButton = document.createElement("button");
//     removeButton.innerHTML = "Remove";
//     removeButton.onclick = function () {
//       removeRow(newRow);
//     };
//     cellAction.appendChild(removeButton);
//   }
//
//   function removeRow(row) {
//     var table = document.getElementById("myTable").getElementsByTagName('tbody')[0];
//     var rowIndex = row.rowIndex;
//     table.deleteRow(rowIndex);
//
//     // Adjust IDs after removal
//     adjustIds();
//   }
//
//   function adjustIds() {
//     var table = document.getElementById("myTable").getElementsByTagName('tbody')[0];
//     var rows = table.getElementsByTagName("tr");
//
//     for (var i = 0; i < rows.length; i++) {
//       var cells = rows[i].getElementsByTagName("td");
//       if (cells.length > 0) {
//         cells[0].innerHTML = i + 1; // Assuming the ID is in the first cell
//       }
//     }
//   }