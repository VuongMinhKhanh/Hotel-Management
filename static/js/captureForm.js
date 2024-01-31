async function captureForm(form) {
    let path; // This will hold the path string once the promise is resolved
    await html2canvas(form).then(async function (canvas) {
        // Convert the canvas to a data URL
        var imgData = canvas.toDataURL('image/png');
        try {
            // Send this data URL to the server using fetch
            const response = await fetch('/api/save_form_image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ imgData: imgData })
            });
            const data = await response.json();
            path = data; // Assuming the server responds with the path in a field named 'path'
            // console.log("data" + data)
        } catch (error) {
            console.error('Error:', error);
        }
    });
    return path; // Only after all awaits are done, path is returned
}
