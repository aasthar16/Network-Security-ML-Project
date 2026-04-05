document.getElementById("uploadForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const fileInput = document.getElementById("fileInput");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch("/predict", {
        method: "POST",
        body: formData
    });

    const html = await response.text();
    document.getElementById("result").innerHTML = html;
});