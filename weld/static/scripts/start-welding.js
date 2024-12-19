document.addEventListener('DOMContentLoaded', () => {
    const startWeldingButton = document.getElementById("start-welding-button");
    const partNumber = document.getElementById("part-number");
    const leftWeldInput = document.getElementById('expected-left-welds');
    const rightWeldInput = document.getElementById('expected-right-welds');
    const totalWeldDisplay = document.getElementById('total-welds');
    const passwordModal = document.getElementById("password-modal");

    const errors = {
        partNumber: document.getElementById("error-part-number"),
    };

    const updateTotalWelds = () => {
        const leftWelds = parseInt(leftWeldInput.value, 10) || 0;
        const rightWelds = parseInt(rightWeldInput.value, 10) || 0;
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
            // Prevent form submission as we are not submitting a form
            event.preventDefault();
        });
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            // Prevent default behavior if the password modal is active
            if (passwordModal && passwordModal.style.display === "flex") {
                document.getElementById("submit-password").click(); // Trigger the password modal submission
            } else {
                const submitButton = document.querySelector('#start-welding-button');
                if (submitButton) {
                    submitButton.click();
                }
            }
        }
    });

    startWeldingButton.addEventListener("click", function (event) {
        // Prevent form submission if validation fails
        if (!validateFields()) {
            event.preventDefault();
        }
    });

    leftWeldInput.addEventListener('input', updateTotalWelds);
    rightWeldInput.addEventListener('input', updateTotalWelds);
});