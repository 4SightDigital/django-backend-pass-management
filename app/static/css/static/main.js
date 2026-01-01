document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload-form');
    const uploadStatus = document.getElementById('upload-status');
    const portalDataInput = document.getElementById('portal-data');
    const sheetDataInput = document.getElementById('sheet-data');
    const submitButton = document.getElementById('submit-button');
    const downloadButton = document.getElementById('download-button');
    const progressBar = document.getElementById('file-progress');
    const clearButton = document.getElementById('clear-button'); // Add reference to Clear button

    form.reset();
    uploadStatus.style.display = 'none';
    progressBar.value = 0;
    downloadButton.disabled = true;

    portalDataInput.addEventListener('change', handleFileUpload);
    sheetDataInput.addEventListener('change', handleFileUpload);

    clearButton.addEventListener('click', function() {
        // Reset form fields
        form.reset();

        // Clear status message and hide
        uploadStatus.textContent = '';
        uploadStatus.style.color = '';
        uploadStatus.style.display = 'none';

        // Disable download button
        downloadButton.disabled = true;

        // Reset progress bar
        progressBar.value = 0;
    });

    let portalDates = {};
    let sheetDates = {};

    function handleFileUpload(event) {
        const inputElement = event.target;

        if (!inputElement.files.length) {
            return;  // Do not proceed if no file is selected
        }

        const formData = new FormData();
        formData.append(inputElement.name, inputElement.files[0]);

        fetch("/upload_files", {
            method: "POST",
            body: formData,
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === "success") {
                const { B2B_date_from, B2B_date_to, Tally_date_from, Tally_date_to } = data.data;

                if (inputElement === portalDataInput) {
                    // Update portal date fields
                    if (B2B_date_from || B2B_date_to) {
                        document.getElementById("portal-date-from-box").classList.remove("gray-input");
                        document.getElementById("portal-date-to-box").classList.remove("gray-input");
                        document.getElementById("portal-date-from-box").value = B2B_date_from || "";
                        document.getElementById("portal-date-to-box").value = B2B_date_to || "";
                    }
                    portalDates = { from: B2B_date_from, to: B2B_date_to };
                } else if (inputElement === sheetDataInput) {
                    // Update sheet date fields
                    if (Tally_date_from || Tally_date_to) {
                        document.getElementById("sheet-date-from-box").classList.remove("gray-input");
                        document.getElementById("sheet-date-to-box").classList.remove("gray-input");
                        document.getElementById("sheet-date-from-box").value = Tally_date_from || "";
                        document.getElementById("sheet-date-to-box").value = Tally_date_to || "";
                    }
                    sheetDates = { from: Tally_date_from, to: Tally_date_to };
                }

                // Check date mismatch
                if (portalDates.from && sheetDates.from && portalDates.to && sheetDates.to) {
                    if (portalDates.from !== sheetDates.from || portalDates.to !== sheetDates.to) {
                        uploadStatus.textContent = 'Dates are mismatched. Click on Submit to Continue';
                        uploadStatus.style.color = 'red';
                    } else {
                        uploadStatus.textContent = 'Upload successful!';
                        uploadStatus.style.color = 'green';
                    }
                }
            } else {
                uploadStatus.textContent = 'Error: ' + (data.message || 'Unknown error');
                uploadStatus.style.color = 'red';
            }
            uploadStatus.style.display = 'block';
        })
        .catch((error) => {
            console.error("Error:", error);
            uploadStatus.textContent = 'Error: ' + error.message;
            uploadStatus.style.color = 'red';
            uploadStatus.style.display = 'block';
        });
    }

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission behavior
    
        // Clear any previous status messages
        uploadStatus.textContent = '';
        uploadStatus.style.color = '';
        uploadStatus.style.display = 'none';
    
        const formData = new FormData(form);
        const xhr = new XMLHttpRequest();
    
        xhr.open('POST', form.action, true);
    
        // Event listener for progress bar
        xhr.upload.addEventListener('progress', function(event) {
            if (event.lengthComputable) {
                const percentComplete = (event.loaded / event.total) * 100;
                progressBar.value = percentComplete;
            }
        });
    
        xhr.onload = function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
    
                if (response.status === 'success') {
                    uploadStatus.textContent = 'Processing Complete';
                    uploadStatus.style.color = 'green';
                    downloadButton.disabled = false;  // Enable download button
    
                    // Provide the download link if needed
                    const downloadLink = document.getElementById('download-link');
                    downloadLink.href = `/path_to_output/${response.file}`;
                    downloadLink.style.display = 'block';
    
                } else {
                    uploadStatus.textContent = 'Error: ' + (response.message || 'Unknown error');
                    uploadStatus.style.color = 'red';
                }
                uploadStatus.style.display = 'block';
            } else {
                uploadStatus.textContent = 'Error: ' + xhr.statusText;
                uploadStatus.style.color = 'red';
                uploadStatus.style.display = 'block';
            }
        };
    
        xhr.onerror = function() {
            uploadStatus.textContent = 'Error: Failed to upload the files.';
            uploadStatus.style.color = 'red';
            uploadStatus.style.display = 'block';
        };
    
        xhr.onloadend = function() {
            progressBar.value = 100;  // Ensure progress bar is set to 100% when done
        };
    
        xhr.send(formData);
    });
    
});
