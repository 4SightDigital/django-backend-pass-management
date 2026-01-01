// Function to check date mismatch and show/hide the message
function checkDateMismatch() {
    var portalDateFrom = document.getElementById('portal-date-from-box').value;
    var portalDateTo = document.getElementById('portal-date-to-box').value;
    var sheetDateFrom = document.getElementById('sheet-date-from-box').value;
    var sheetDateTo = document.getElementById('sheet-date-to-box').value;

    if (portalDateFrom !== "" && portalDateTo !== "" && sheetDateFrom !== "" && sheetDateTo !== "") {
        if (portalDateFrom !== sheetDateFrom || portalDateTo !== sheetDateTo) {
            var warningMessage = document.getElementById('date-mismatch-warning');
            warningMessage.innerHTML = "Dates are mismatched. Click on submit to continue";
            warningMessage.style.display = 'block';
        } else {
            document.getElementById('date-mismatch-warning').style.display = 'none';
        }
    } else {
        console.log("One or more date fields are empty.");
    }
}

// Handle 'portal-data' file input
document.getElementById('portal-data').addEventListener('change', function() {
    var formData = new FormData();
    formData.append('portal-data', this.files[0]);

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload-portal-data', true);
    xhr.setRequestHeader('X-CSRFToken', document.querySelector('[name=csrf_token]').value);

    xhr.onload = function() {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            document.getElementById('portal-date-from-box').value = response.B2B_date_from;
            document.getElementById('portal-date-to-box').value = response.B2B_date_to;
            document.getElementById('portal-date-from-box').classList.remove('gray-input');
            document.getElementById('portal-date-to-box').classList.remove('gray-input');

            checkDateMismatch(); // Check date mismatch after portal data upload
        }
    };

    xhr.send(formData);
});

// Handle 'sheet-data' file input
document.getElementById('sheet-data').addEventListener('change', function() {
    var formData = new FormData();
    formData.append('sheet-data', this.files[0]);

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload-sheet-data', true);
    xhr.setRequestHeader('X-CSRFToken', document.querySelector('[name=csrf_token]').value);

    xhr.onload = function() {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            document.getElementById('sheet-date-from-box').value = response.Tally_date_from;
            document.getElementById('sheet-date-to-box').value = response.Tally_date_to;
            document.getElementById('sheet-date-from-box').classList.remove('gray-input');
            document.getElementById('sheet-date-to-box').classList.remove('gray-input');

            checkDateMismatch(); // Check date mismatch after sheet data upload
        }
    };

    xhr.send(formData);
});

function updateProgressBar() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/get-progress', true);
    
    xhr.onload = function() {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            document.getElementById('file-progress').value = response.progress;
        }
    };

    xhr.send();
}

document.getElementById('submit-button').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent default form submission

    // Start polling for progress updates
    var progressInterval = setInterval(updateProgressBar, 1000);  // Every 1 second

    var formData = new FormData(document.getElementById('upload-form'));
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload', true);
    xhr.setRequestHeader('X-CSRFToken', document.querySelector('[name=csrf_token]').value);

    xhr.onload = function() {
        if (xhr.status === 200) {
            clearInterval(progressInterval);  // Stop polling once upload is done
            document.getElementById('file-progress').value = 100;
            alert('Processing complete');
            document.getElementById('download-button').disabled = false;
        } else {
            alert('An error occurred during file upload and processing.');
        }
    };

    xhr.onerror = function() {
        clearInterval(progressInterval);
        alert('An error occurred during the upload.');
    };

    xhr.send(formData);
});

document.getElementById('download-button').addEventListener('click', function(event) {
    event.preventDefault();

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/download', true);
    xhr.responseType = 'blob';
    xhr.setRequestHeader('X-CSRFToken', document.querySelector('[name=csrf_token]').value);

    xhr.onload = function() {
        if (xhr.status === 200) {
            var today = new Date();
            var dd = String(today.getDate()).padStart(2, '0');
            var mm = String(today.getMonth() + 1).padStart(2, '0');
            var yyyy = today.getFullYear();

            var currentDate = dd + '-' + mm + '-' + yyyy;

            var blob = new Blob([xhr.response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = 'output_' + currentDate + '.xlsx';  // Set the dynamic filename
            link.click();
            clearFileContent();

            // Reset form fields and UI elements
            document.getElementById('portal-data').value = '';
            document.getElementById('portal-date-from-box').value = '';
            document.getElementById('portal-date-to-box').value = '';
            document.getElementById('sheet-data').value = '';
            document.getElementById('sheet-date-from-box').value = '';
            document.getElementById('sheet-date-to-box').value = '';
            document.getElementById('file-progress').value = 0;
            document.getElementById('download-button').disabled = true;
        } else {
            alert('Error downloading file. Status: ' + xhr.status);
        }
    };

    xhr.onerror = function() {
        alert('An error occurred during the download process.');
    };

    xhr.send();
});

function clearFileContent() {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/clear-file', true);
    xhr.setRequestHeader('X-CSRFToken', document.querySelector('[name=csrf_token]').value);
    xhr.onload = function() {
        if (xhr.status === 200) {
            alert('File content cleared.');
        } else {
            alert('Error clearing file content.');
        }
    };
    xhr.onerror = function() {
        alert('An error occurred during the clear file operation.');
    };
    xhr.send();
}
