document.addEventListener('DOMContentLoaded', function () {
    // Variables
    const toggleLock = document.getElementById("toggle-lock");
    const iconUnlockPath = document.querySelector("#icon-unlock path");
    const iconLockedPath = document.querySelector("#icon-lock path");
    const passwordModal = document.getElementById("password-modal");
    const passwordInput = document.getElementById("password-input");
    const submitPasswordButton = document.getElementById("submit-password");
    const closeModal = document.getElementById("close-modal");
    const passwordError = document.getElementById("password-error");
    const url = document.getElementById('index-form').action;

    let isLocked = false;
    let passwordRequired = false;

    // Function to update the UI based on the lock status
    function updateLockUI(lockStatus) {
        isLocked = lockStatus;
        if (lockStatus) {
            iconLockedPath.setAttribute("fill", "#1976D2");
            iconUnlockPath.setAttribute("fill", "#808080");
            toggleLock.checked = true;
            console.log("Jig Lock Status: Locked");
        } else {
            iconUnlockPath.setAttribute("fill", "#1976D2");
            iconLockedPath.setAttribute("fill", "#808080");
            toggleLock.checked = false;
            console.log("Jig Lock Status: Unlocked");
        }
    }

    // Check if a password is required
    function checkPasswordRequired() {
        fetch(url + "api/password-required")
            .then((response) => response.json())
            .then((data) => {
                passwordRequired = data.password_required;
            })
            .catch((error) => console.error("Error checking password requirement:", error));
    }

    // Poll the /api/lock-status endpoint every 5 seconds
    function pollLockStatus() {
        fetch(url + "api/lock-status")
            .then((response) => response.json())
            .then((data) => {
                updateLockUI(data.is_locked);
            })
            .catch((error) => console.error("Error fetching lock status:", error));
    }

    // Handle lock toggle click
    toggleLock.addEventListener("change", function (event) {
        if (passwordRequired) {
            // Prevent the toggle from switching immediately
            event.preventDefault();
            event.stopPropagation();
            passwordModal.style.display = "flex";
        } else {
            updateLockStatus(!isLocked);
        }
    });

    // Handle password submission
    submitPasswordButton.addEventListener("click", function () {
        const password = passwordInput.value;
        updateLockStatus(!isLocked, password);
    });

    // Update lock status
    function updateLockStatus(lockState, password = null) {
        const requestData = { is_locked: lockState };
        if (password) {
            requestData.password = password;
        }

        fetch(url + "api/lock-status", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Incorrect password");
                }
                return response.json();
            })
            .then((data) => {
                updateLockUI(data.is_locked);
                if (passwordModal.style.display === "flex") {
                    passwordModal.style.display = "none";
                }
                passwordError.style.display = "none";
                passwordInput.value = "";
            })
            .catch((error) => {
                console.error("Error updating lock status:", error);
                if (password) {
                    passwordError.style.display = "block";
                }
            });
    }

    // Close modal
    closeModal.addEventListener("click", function () {
        passwordModal.style.display = "none";
    });

    // Initialize password check and lock status polling
    checkPasswordRequired();
    pollLockStatus();
    setInterval(pollLockStatus, 5000);
});
