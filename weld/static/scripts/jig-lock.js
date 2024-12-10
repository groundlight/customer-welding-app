document.addEventListener('DOMContentLoaded', function () {
    // Variables
    const toggleLock = document.getElementById("toggle-lock");
    const iconUnlockPath = document.querySelector("#icon-unlock path");
    const iconLockedPath = document.querySelector("#icon-lock path");
    
    // Function to update the UI based on the lock status
    function updateLockUI(isLocked) {
        if (isLocked) {
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

    // Poll the /api/lock-status endpoint every 5 seconds
    function pollLockStatus() {
        fetch(getLockStatusUrl)
            .then((response) => response.json())
            .then((data) => {
                updateLockUI(data.is_locked);
            })
            .catch((error) => console.error("Error fetching lock status:", error));
    }

    // Send a request to update the lock status
    toggleLock.addEventListener("change", function () {
        const isLocked = toggleLock.checked;
        fetch(lockStatusUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ is_locked: isLocked }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Failed to update lock status");
                }
                return response.json();
            })
            .then((data) => {
                if (isLocked) {
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
                console.log(data.message);
            })
            .catch((error) => {
                console.error("Error updating lock status:", error);
            });
    });

    // Start polling for lock status
    pollLockStatus();
    setInterval(pollLockStatus, 5000);
});