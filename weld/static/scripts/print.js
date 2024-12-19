document.addEventListener('DOMContentLoaded', () => {
    const passwordModal = document.getElementById("password-modal");

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            // Prevent default behavior if the password modal is active
            if (passwordModal && passwordModal.style.display === "flex") {
                document.getElementById("submit-password").click(); // Trigger the password modal submission
            } else {
                const submitButton = document.querySelector('#restart-button');
                if (submitButton) {
                    submitButton.click();
                }
            }
        }
    });

});