document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("appointmentForm");
    const timeInput = document.getElementById("time");
    const timeDropdown = document.getElementById("timeDropdown");

    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault(); // Prevent default form submission

            const timeValue = document.getElementById("timeValue").value;
            if (!timeValue) {
                const errorContainer = document.getElementById("errorAlertContainer");
                if (errorContainer) {
                    errorContainer.innerHTML = `
                        <div class="alert alert-warning alert-dismissible fade show" role="alert">
                            <strong>Please select a time.</strong>
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    `;
                }
                return;
            }

            const formData = new FormData(form);
            const payload = new URLSearchParams(formData);

            try {
                const res = await fetch("/appointments", {
                    method: "POST",
                    body: payload
                });

                const result = await res.json();

                if (res.ok) {
                    // Success: show confirmation
                    showNotification(result.message);
                    setTimeout(() => {
                        window.location.reload();
                    }, 3000);
                } else {
                    // Slot taken or other error – show Bootstrap alert in the page
                    const errorContainer = document.getElementById("errorAlertContainer");
                    if (errorContainer) {
                        errorContainer.innerHTML = `
                            <div class="alert alert-warning alert-dismissible fade show" role="alert">
                                <strong>${result.error || "Slot already taken."}</strong> Please try another time or date.
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            </div>
                        `;
                    }
                }
                
            } catch (err) {
                console.error("Something went wrong while submitting the form:", err);
            }
        });
    }

    // Prevent selecting past dates
    let today = new Date().toISOString().split("T")[0];
    let dateInput = document.getElementById("date");

    if (dateInput) {
        dateInput.setAttribute("min", today);
    }

    // Handle time selection dropdown
    if (timeInput && timeDropdown) {
        timeInput.addEventListener("click", function () {
            console.log("Time input clicked");
            timeDropdown.classList.toggle("show");
        });

        document.addEventListener("click", function (event) {
            if (!timeInput.contains(event.target) && !timeDropdown.contains(event.target)) {
                timeDropdown.classList.remove("show");
            }
        });

        populateTimeDropdown(timeDropdown, timeInput);
    }
});

/**
 * Populates the time dropdown with looping times
 */
function populateTimeDropdown(dropdown, input) {
    let openingHour = 8;
    let closingHour = 18;
    let interval = 15;
    let times = [];

    dropdown.innerHTML = ""; // Clear existing options

    // Start at 8:30 AM
    for (let hour = openingHour; hour < closingHour; hour++) {
        for (let min = (hour === openingHour ? 30 : 0); min < 60; min += interval) {
            if (hour === closingHour - 1 && min > 0) break; // Stop at 18:00
            let timeValue = `${String(hour).padStart(2, "0")}:${String(min).padStart(2, "0")}`;
            let displayTime = formatTimeForDisplay(hour, min);
            times.push({ timeValue, displayTime });
        }
    }

    // Populate the dropdown with times
    times.forEach(({ timeValue, displayTime }) => {
        let timeOption = document.createElement("div");
        timeOption.classList.add("time-option");
        timeOption.textContent = displayTime;
        timeOption.dataset.value = timeValue;

        timeOption.addEventListener("click", function () {
            input.value = displayTime; // Display 12-hour format
            document.getElementById("timeValue").value = timeValue; // Store 24-hour format
            dropdown.classList.remove("show");
        });

        dropdown.appendChild(timeOption);
    });
}

/**
 * Formats time into a user-friendly 12-hour format with AM/PM.
 */
function formatTimeForDisplay(hours, mins) {
    let suffix = hours >= 12 ? "PM" : "AM";
    let formattedHours = hours > 12 ? hours - 12 : hours;
    if (formattedHours === 0) formattedHours = 12;
    return `${formattedHours}:${String(mins).padStart(2, "0")} ${suffix}`;
}

/**
 * Creates a sleek notification when an appointment is booked.
 */
function showNotification(message) {
    const notification = document.getElementById("notification");
    if (!notification) return; // Fallback if not found

    notification.querySelector("p").textContent = message; // Update existing <p>

    // Show animation
    notification.classList.add("show");
    setTimeout(() => {
        notification.classList.remove("show");
    }, 4000); // Hide after 4 seconds
}