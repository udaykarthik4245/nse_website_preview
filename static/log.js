function filterLogs() {
    const input = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#logTableBody tr');
    let hasVisibleRow = false;

    rows.forEach(row => {
        const cells = row.getElementsByTagName('td');
        const action = cells[1].textContent.toLowerCase();
        if (action.includes(input)) {
            row.style.display = ""; // Show row
            hasVisibleRow = true;
        } else {
            row.style.display = "none"; // Hide row
        }
    });
    // Show or hide the no results message
    const noResultsMessage = document.getElementById('noResultsMessage');
    noResultsMessage.style.display = hasVisibleRow ? 'none' : 'block';
}