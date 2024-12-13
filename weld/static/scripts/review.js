document.addEventListener('DOMContentLoaded', () => {
    const printTagButton = document.getElementById("print-tag-button");
    const partNumber = document.getElementById("part-number");
    const leftWeldInput = document.getElementById('left-welds');
    const rightWeldInput = document.getElementById('right-welds');
    const totalWeldDisplay = document.getElementById('total-welds');
    const expectedLeftWeld = document.getElementById('expected-left-welds');
    const expectedRightWeld = document.getElementById('expected-right-welds');
    const expectedTotalWeld = document.getElementById('expected-total-welds');
    expectedTotalWeld.textContent = parseInt(expectedLeftWeld.textContent, 10) + parseInt(expectedRightWeld.textContent, 10);
    totalWeldDisplay.textContent = parseInt(leftWeldInput.value, 10) + parseInt(rightWeldInput.value, 10);

    const errors = {
        partNumber: document.getElementById("error-part-number"),
    };

    const updateTotalWelds = () => {
        const leftWelds = parseInt(leftWeldInput.value, 10);
        const rightWelds = parseInt(rightWeldInput.value, 10);
        totalWeldDisplay.textContent = leftWelds + rightWelds;
    };

    function validateFields() {
        let isValid = true;

        // Reset error messages
        Object.values(errors).forEach((error) => {
            error.textContent = "";
        });

        // Check if Part Number has value
        if (!partNumber.value) {
            errors.partNumber.textContent = "Please enter a Part Number.";
            isValid = false;
        }

        return isValid;
    }

    document.querySelectorAll('.increment, .decrement').forEach(button => {
        button.addEventListener('click', (event) => {
            const input = event.target.dataset.target === 'left' ? leftWeldInput : rightWeldInput;
            let currentValue = parseInt(input.value, 10) || 0;

            if (event.target.classList.contains('increment')) {
                if (currentValue < 200) currentValue++;
            } else if (event.target.classList.contains('decrement')) {
                if (currentValue > 0) currentValue--;
            }

            input.value = currentValue;
            updateTotalWelds();
            event.preventDefault();
        });
    });

    printTagButton.addEventListener("click", function (event) {
        // Prevent form submission if validation fails
        if (!validateFields()) {
            event.preventDefault();
        }
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent default form behavior
            const submitButton = document.querySelector('#print-tag-button');
            if (submitButton) {
                submitButton.click();
            }
        }
    });

    leftWeldInput.addEventListener('input', updateTotalWelds);
    rightWeldInput.addEventListener('input', updateTotalWelds);
});