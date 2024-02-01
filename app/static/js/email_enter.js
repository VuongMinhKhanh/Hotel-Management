async function enterEmail(form) {
    // let emails = prompt("Hãy nhập email cần gửi")
    let emails = "2151050191khanh@ou.edu.vn, vminhkhoivy@gmail.com"
    emails = splitEmails(emails)
    if (checkEmails(emails)) {
        const path = await captureForm(form)
        // console.log("path " + (path))
        fetch("/api/send_emails", {
            method: "post",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                emails: emails,
                path: path
            })
        }).then(r => r.json());
        alert("Đã gửi thành công!")
    } else {
        alert("Email không phù hợp!")
    }
}

function splitEmails(emails) {
    if (emails.includes(",")) {
        array = emails.split(",");
        newArray = []
        for (let a of array) {
            newArray.push(a.trim())
        }
        return newArray
    }
    else {
        emails = [emails]
        return emails
    }
}

function checkEmails(emails) {
    for (e of emails) {
        if (!(e.includes("@gmail.com") || e.includes("@ou.edu.vn")))
            return false
    }
    return true
}