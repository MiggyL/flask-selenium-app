document.addEventListener('DOMContentLoaded', function () {
    const automateButton = document.getElementById('automate-button');  // Get the reference to the automate button
    const rowInput = document.getElementById('row-number');  // Get the reference to the row input field

    // Check if the automate button exists
    if (automateButton) {
        // Add an event listener to the automate button for a click event
        automateButton.addEventListener('click', function () {
            console.log("Automate button clicked.");

            // Get the row number from the input field and trim any excess whitespace
            const rowNumber = rowInput.value.trim();

            // Ensure the row number input is not empty and is a valid number
            if (rowNumber !== '' && !isNaN(rowNumber)) {
                // Query the active tab to get its details
                chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
                    console.log("Executing script to get spreadsheet ID and active sheet.");

                    // Execute a script on the active tab to retrieve the sheet name and spreadsheet ID from Google Sheets
                    chrome.scripting.executeScript({
                        target: { tabId: tabs[0].id },
                        func: () => {
                            // Get the name of the active sheet by selecting the appropriate DOM element
                            const sheetElement = document.querySelector('.docs-sheet-tab.docs-sheet-active-tab .docs-sheet-tab-name');
                            const sheetName = sheetElement ? sheetElement.textContent : null;

                            // Get the current tab URL and extract the spreadsheet ID from the URL
                            const currentTabUrl = window.location.href;
                            const regex = /\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/;
                            const match = currentTabUrl.match(regex);
                            const spreadsheetId = match ? match[1] : null;

                            // Log the sheet name and spreadsheet ID to the console for debugging
                            console.log('Active sheet name:', sheetName);
                            console.log('Spreadsheet ID:', spreadsheetId);

                            // Return the sheet name and spreadsheet ID
                            return { sheetName, spreadsheetId };
                        }
                    }, function (results) {
                        // Check if the script successfully returned results
                        if (results && results[0].result) {
                            const { sheetName, spreadsheetId } = results[0].result;

                            // Ensure both the sheet name and spreadsheet ID were retrieved
                            if (sheetName && spreadsheetId) {
                                // Open a new tab for the "Add Card" page
                                chrome.tabs.create({
                                    url: "https://fifi-greetings-admin.firebaseapp.com/card/add"
                                }, function (tab) {
                                    // After opening the new tab, send the gathered data to the Flask backend
                                    fetch('http://127.0.0.1:5000/automate', {
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json'
                                        },
                                        body: JSON.stringify({
                                            sheet_name: sheetName,      // The name of the active sheet
                                            row_number: rowNumber,      // The row number input by the user
                                            spreadsheet_id: spreadsheetId  // The spreadsheet ID from the URL
                                        })
                                    })
                                    .then(response => {
                                        // Check if the response from the server is OK
                                        if (!response.ok) {
                                            throw new Error(`HTTP error! status: ${response.status}`);
                                        }
                                        return response.json();
                                    })
                                    .then(result => {
                                        // Log success message upon successful execution
                                        console.log('Success:', result);
                                    })
                                    .catch(error => {
                                        // Log any errors encountered during the process
                                        console.error('Error:', error);
                                    });
                                });
                            } else {
                                console.error('Failed to retrieve active sheet or spreadsheet ID.');
                            }
                        } else {
                            console.error('No results returned from executed script.');
                        }
                    });
                });
            } else {
                // Log an error if the row number input is invalid
                console.error('Invalid row number.');
            }
        });
    } else {
        // Log an error if the automate button element is not found
        console.error('Failed to retrieve the automate button element.');
    }
});