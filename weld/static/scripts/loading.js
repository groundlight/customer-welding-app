document.addEventListener('DOMContentLoaded', function () {
    // Variables
    var forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.onsubmit = function (event) {
            document.getElementById('loading').style.display = 'flex';
            document.getElementById('content').style.display = 'none';
        };
    });
});