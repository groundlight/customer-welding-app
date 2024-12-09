document.addEventListener("DOMContentLoaded", function () {
    const startShiftButton = document.getElementById("start-shift-button");
    const jigNumber = document.getElementById("jig-number");
    const shiftNumber = document.getElementById("shift-number");
    const leftWelder = document.getElementById("left-welder");
    const rightWelder = document.getElementById("right-welder");

    const errors = {
        jigNumber: document.getElementById("error-jig-number"),
        shiftNumber: document.getElementById("error-shift-number"),
        leftWelder: document.getElementById("error-left-welder"),
        rightWelder: document.getElementById("error-right-welder"),
    };

    function validateFields() {
        let isValid = true;

        // Reset error messages
        Object.values(errors).forEach((error) => {
            error.textContent = "";
        });

        // Check if Jig Number is selected
        if (!jigNumber.value) {
            errors.jigNumber.textContent = "Please select a Jig Number.";
            isValid = false;
        }

        // Check if Shift Number is selected
        if (!shiftNumber.value) {
            errors.shiftNumber.textContent = "Please select a Shift Number.";
            isValid = false;
        }

        // Check if Left Welder Name is entered
        if (!leftWelder.value.trim()) {
            errors.leftWelder.textContent = "Please enter the name of the Left Welder.";
            isValid = false;
        }

        // Check if Right Welder Name is entered
        if (!rightWelder.value.trim()) {
            errors.rightWelder.textContent = "Please enter the name of the Right Welder.";
            isValid = false;
        }

        return isValid;
    }

    startShiftButton.addEventListener("click", function (event) {
        // Prevent form submission if validation fails
        if (!validateFields()) {
            event.preventDefault();
        }
    });
});
