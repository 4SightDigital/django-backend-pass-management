document.getElementById('clear-button').addEventListener('click', function () {
    console.log("Clear button clicked"); // Debugging: Check if the event listener is triggered

    // Clear input fields
    document.getElementById('portal-data').value = '';
    document.getElementById('sheet-data').value = '';

    // Reset progress bar
    document.getElementById('file-progress').value = 0;

    // Disable download button
    document.getElementById('download-button').disabled = true;

    // Clear the date mismatch warning message
    var warningMessage = document.getElementById('date-mismatch-warning');
    console.log("Mismatch message visibility:", warningMessage.style.display); // Debugging: Check visibility state
    warningMessage.style.display = 'none';
    console.log("Mismatch message cleared"); // Debugging: Confirm it was cleared
});

