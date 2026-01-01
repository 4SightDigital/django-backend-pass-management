
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('upload-form');
    const uploadStatus = document.getElementById('upload-status');
    const downloadButton = document.getElementById('download-button');
    const bankbookColumnsDiv = document.getElementById('bankbook-columns');
    const bankstatementColumnsDiv = document.getElementById('bankstatement-columns');
    const columnNamesContainer = document.getElementById('column-names-container');
    const inputContainer = document.getElementById('inputContainer');

    // Counter for new input sections
    let inputSectionCount = 1;

    // Handle form submission
    form.addEventListener('submit', function (e) {
        e.preventDefault(); 
        
        const formData = new FormData(form);
        uploadStatus.style.display = 'block'; 
        uploadStatus.textContent = 'Uploading...';

        fetch('/upload_files', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                uploadStatus.textContent = data.message; 
                uploadStatus.style.color = 'green';

                // Clear previous column names
                bankbookColumnsDiv.querySelector('ul').innerHTML = '';
                bankstatementColumnsDiv.querySelector('ul').innerHTML = '';

                columnNamesContainer.style.display = 'block';

                // Display Bank Book column names
                if (data.columns['Bank Book']) {
                    data.columns['Bank Book'].forEach(column => {
                        createDraggableListItem(column, bankbookColumnsDiv.querySelector('ul'));
                    });
                }

                // Display Bank Statement column names
                if (data.columns['Bank Statement']) {
                    data.columns['Bank Statement'].forEach(column => {
                        createDraggableListItem(column, bankstatementColumnsDiv.querySelector('ul'));
                    });
                }

            } else {
                uploadStatus.textContent = `Upload failed: ${data.message}`;
                uploadStatus.style.color = 'red';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            uploadStatus.textContent = 'An error occurred during the upload.';
            uploadStatus.style.color = 'red';
        });
    });

    // Handle clear button click
    document.getElementById('clear-button').addEventListener('click', function () {
        form.reset(); // Reset form fields
        uploadStatus.style.display = 'none'; // Hide upload status
        uploadStatus.textContent = ''; // Clear status message
        columnNamesContainer.style.display = 'none'; // Hide column names container

        // Clear column names lists
        bankbookColumnsDiv.querySelector('ul').innerHTML = '';
        bankstatementColumnsDiv.querySelector('ul').innerHTML = '';
        
        // Clear any additional dynamic inputs
        inputContainer.innerHTML = ''; // Remove all dynamically added inputs
        inputSectionCount = 1; // Reset input section counter
    });

    // Handle file download
    downloadButton.addEventListener('click', function () {
        window.location.href = '/download';
        form.reset();
        uploadStatus.style.display = 'none'; 
        columnNamesContainer.style.display = 'none'; 
        bankbookColumnsDiv.querySelector('ul').innerHTML = '';
        bankstatementColumnsDiv.querySelector('ul').innerHTML = '';
    });

    function createDraggableListItem(column, parent) {
        const listItem = document.createElement('li');
        listItem.textContent = column;
        listItem.setAttribute('draggable', 'true');

        listItem.addEventListener('dragstart', function (e) {
            listItem.classList.add('dragging');
            e.dataTransfer.setData('text/plain', column); // Store the column name for drop
        });

        listItem.addEventListener('dragend', function () {
            listItem.classList.remove('dragging');
        });

        parent.appendChild(listItem);

        // Add event listeners to handle dropping
        parent.addEventListener('dragover', function (e) {
            e.preventDefault();
            const draggingItem = parent.querySelector('.dragging');
            const afterElement = getDragAfterElement(parent, e.clientY);
            if (afterElement) {
                parent.insertBefore(draggingItem, afterElement);
            } else {
                parent.appendChild(draggingItem);
            }
        });
    }

    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('li:not(.dragging)')];

        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    addButton.addEventListener('click', function() {
        const newInputs = document.createElement('div');
        newInputs.className = 'new-inputs';

        // Create a container for the row of input fields
        const rowContainer = document.createElement('div');
        rowContainer.className = 'row-container'; // For flexbox styling

        // Display the section number
        const sectionTitle = document.createElement('h3');
        sectionTitle.textContent = `${inputSectionCount++}`; // Increment section count
        sectionTitle.className = 'section-title'; // Add class for styling

        // Dropdown options
        const dropdown = document.createElement('select');
        dropdown.innerHTML = `<option value="">Select Option</option>
                            <option value="Option 1">Option 1</option>
                            <option value="Option 2">Option 2</option>`;
        
        // Enter Number Input
        const numberInput = document.createElement('input');
        numberInput.type = 'number';
        numberInput.placeholder = 'Enter No.';

        // Sheet Name Input
        const sheetNameInput = document.createElement('input');
        sheetNameInput.type = 'text';
        sheetNameInput.placeholder = 'Sheet Name';

        // Header Name Input
        const headerNameInput = document.createElement('input');
        headerNameInput.type = 'text';
        headerNameInput.placeholder = 'Header Name';

        // Input field for drag-and-drop
        const dragDropContainer = document.createElement('div');
        dragDropContainer.className = 'drag-drop-container';
        dragDropContainer.style.display = 'none'; // Initially hidden

        // Create a flex container for two columns
        const columnListContainer = document.createElement('div');
        columnListContainer.className = 'column-list-container';

        // Create Bankbook column
        const bankbookColumns = document.createElement('div');
        bankbookColumns.id = 'bankbook-columns';
        bankbookColumns.innerHTML = '<h4>Bankbook</h4>'; // Header for Bankbook

        // Create Bank Statement column
        const bankstatementColumns = document.createElement('div');
        bankstatementColumns.id = 'bankstatement-columns';
        bankstatementColumns.innerHTML = '<h4>Bank Statement</h4>'; // Header for Bank Statement

        // Event listener for number input
        numberInput.addEventListener('change', function() {
            const numberOfFields = parseInt(this.value); // Create number of fields based on input
            bankbookColumns.innerHTML = '<h4>Bankbook</h4>'; // Reset column content
            bankstatementColumns.innerHTML = '<h4>Bank Statement</h4>'; // Reset column content

            // Create drag fields for bankbook
            for (let i = 0; i < numberOfFields; i++) {
                const newField = document.createElement('li');
                newField.className = 'drag-field';
                newField.textContent = `Bankbook Columns Drag Here ${i + 1}`; // Placeholder text
                setupDragField(newField);
                bankbookColumns.appendChild(newField);
            }

            // Create drag fields for bank statement
            for (let i = 0; i < numberOfFields; i++) {
                const newField = document.createElement('li');
                newField.className = 'drag-field';
                newField.textContent = `Bank Statement Columns Drag Here ${i + 1}`; // Placeholder text
                setupDragField(newField);
                bankstatementColumns.appendChild(newField);
            }

            dragDropContainer.style.display = 'block'; // Show the drag-and-drop area
        });

        // Append the columns to the column list container
        columnListContainer.appendChild(bankbookColumns);
        columnListContainer.appendChild(bankstatementColumns);

        // Button to remove the input section
        const removeButton = document.createElement('button');
        removeButton.textContent = 'Remove';
        removeButton.className = 'remove-button'; // Add class for styling

        removeButton.addEventListener('click', function() {
            inputContainer.removeChild(newInputs); // Remove this section
            updateSectionNumbers(); // Update section numbers after removal
        });

        // Append all inputs to the newInputs div
        rowContainer.appendChild(sectionTitle);
        rowContainer.appendChild(dropdown);
        rowContainer.appendChild(numberInput);
        rowContainer.appendChild(sheetNameInput);
        rowContainer.appendChild(headerNameInput);
        rowContainer.appendChild(removeButton); // Add the remove button to the same row
        newInputs.appendChild(rowContainer); // Add the row container with title and inputs
        newInputs.appendChild(dragDropContainer); // Add the dragDropContainer
        dragDropContainer.appendChild(columnListContainer); // Append the column list container

        // Append newInputs to the inputContainer
        inputContainer.appendChild(newInputs);
    });

    // Function to set up drag fields
    function setupDragField(field) {
        field.setAttribute('draggable', 'true');

        field.addEventListener('dragover', function(e) {
            e.preventDefault();
        });

        field.addEventListener('drop', function(e) {
            const draggedColumn = e.dataTransfer.getData('text/plain');
            field.textContent = draggedColumn; // Set the dropped column name and keep it
        });
    }

    // Function to update section numbers
    function updateSectionNumbers() {
        const sections = document.querySelectorAll('.new-inputs');
        sections.forEach((section, index) => {
            const title = section.querySelector('.section-title');
            title.textContent = `${index + 1}`; // Update title to new section number
        });
    }

    const processDataButton = document.getElementById('processDataButton');

    processDataButton.addEventListener('click', function() {
        const inputSections = document.querySelectorAll('.new-inputs');
        const processedData = [];

        inputSections.forEach(section => {
            const dropdown = section.querySelector('select');
            const numberInput = section.querySelector('input[type="number"]');
            const sheetNameInput = section.querySelector('input[type="text"][placeholder="Sheet Name"]');
            const headerNameInput = section.querySelector('input[type="text"][placeholder="Header Name"]');
            const bankbookColumns = section.querySelector('#bankbook-columns');
            const bankstatementColumns = section.querySelector('#bankstatement-columns');

            // Get the selected option
            const selectedOption = dropdown.value;

            // Get the number input value
            const numberOfFields = numberInput.value;

            // Get the sheet and header names
            const sheetName = sheetNameInput.value;
            const headerName = headerNameInput.value;

            // Get the dragged items from bankbook and bank statement columns
            const bankbookData = [...bankbookColumns.querySelectorAll('li')].map(li => li.textContent);
            const bankstatementData = [...bankstatementColumns.querySelectorAll('li')].map(li => li.textContent);

            // Push the collected data into the processedData array
            processedData.push({
                selectedOption,
                numberOfFields,
                sheetName,
                headerName,
                bankbookData,
                bankstatementData,
            });
        });

        // Log the processed data or perform any action you need
        console.log(processedData);
        
        // Sending the processed data to the backend
        fetch('/process_data', {  // Make sure the URL is correct
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // Specify that we're sending JSON
                'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content') // Include CSRF token
            },
            body: JSON.stringify(processedData) // Send the processed data directly
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            alert('Data sent successfully!');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error sending the data.');
        });
        // Optionally, display the processed data in a user-friendly way
        // For example, showing it in an alert, or in a specific HTML element
        // alert(JSON.stringify(processedData, null, 2));
    });





});




