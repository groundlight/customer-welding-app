document.addEventListener('DOMContentLoaded', () => {

    async function updateData() {
        try {
            const response = await fetch(weldStatusUrl); 
            const data = await response.json();
            const partNumber = document.getElementById('partNumber');
            const leftWeldCount = document.getElementById('leftWeldCount');
            const rightWeldCount = document.getElementById('rightWeldCount');
            const actualLeftWeldCount = document.getElementById('actual_left_welds');
            const actualRightWeldCount = document.getElementById('actual_right_welds');

            partNumber.textContent = data.partNumber || 'N/A';
            leftWeldCount.textContent = parseInt(data.leftWeldCount, 10);
            rightWeldCount.textContent = parseInt(data.rightWeldCount, 10);

            // Update the actual weld counts form value
            actualLeftWeldCount.value = parseInt(data.leftWeldCount, 10);
            actualRightWeldCount.value = parseInt(data.rightWeldCount, 10);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent default form behavior
            const submitButton = document.querySelector('#review-button');
            if (submitButton) {
                submitButton.click();
            }
        }
    });

    // Update data every 1 second
    setInterval(updateData, 1000);

    // Initial data load
    updateData();

});