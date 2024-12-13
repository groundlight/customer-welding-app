document.addEventListener('DOMContentLoaded', () => {

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent default form behavior
            const submitButton = document.querySelector('#restart-button');
            if (submitButton) {
                submitButton.click();
            }
        }
    });

});