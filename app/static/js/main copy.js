document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('upload-form');
    const uploadStatus = document.getElementById('upload-status');
    
    form.addEventListener('submit', function (e) {
        e.preventDefault(); // Prevent the default form submission
        
        const formData = new FormData(form); // Collect form data

        // Show upload status (optional)
        uploadStatus.style.display = 'block';
        uploadStatus.innerHTML = 'Uploading...';

        // Make the AJAX request to submit the form
        fetch('/upload_files', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                uploadStatus.innerHTML = 'Files uploaded successfully!';
            } else {
                uploadStatus.innerHTML = `Error: ${data.message}`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            uploadStatus.innerHTML = 'An error occurred while uploading the files.';
        });
    });

    // Handle the "Download" button click
    const downloadButton = document.getElementById('download-button');
    downloadButton.addEventListener('click', function () {
        window.location.href = '/download'; // Trigger the file download
    });
});
