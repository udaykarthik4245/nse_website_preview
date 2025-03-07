document.getElementById('download-btn').addEventListener('click', function () {
    const startDate = document.getElementById('start-date');
    const Date = startDate.value;
    const formatSelect = document.getElementById('data-format');
    const format = formatSelect.value;
    /// Disable button to avoid multiple requests
    const button = this;
    button.disabled = true;

    if (!Date || !format) {
        alert('Please fill in all fields');
        button.disabled = false;
        return;
    }

    fetch('/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ Date, format })
    })

    .then(response => {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            return response.json().then(data => {
                throw new Error(data.message || 'Failed to download report.');
            });
        }
        return response.blob();
    })

    .then(blob => {
        // Create a link element to trigger the download
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `merged_reports_${Date}.${format}`;  // Set the default filename
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);  // Release memory

        setTimeout(() => {
            alert('Downloaded successfully!');
        }, 5000);
    })

    .catch(error => {
        alert('Error: ' + error.message);
        button.disabled = false;
    })

    .finally(() => {
        formatSelect.selectedIndex = 0;
        startDate.value = '';
        this.disabled = false;
    });
});

function updateDownloadTime() {
    const now = new Date();
    const nextDownload = new Date();
    nextDownload.setHours(18, 10, 0);

    // If it's already past 5 PM, schedule for the next day
    if (now > nextDownload) {
        nextDownload.setDate(nextDownload.getDate() + 1);
    }

    document.getElementById('nextDownload').textContent = nextDownload.toLocaleString();
}

// Run updateDownloadTime on page load
window.onload = updateDownloadTime;