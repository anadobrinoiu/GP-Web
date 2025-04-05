document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("appointmentForm");
    const timeInput = document.getElementById("time");
    const timeDropdown = document.getElementById("timeDropdown");

    if (form) {
        form.addEventListener("submit", function () {
            // This alert will show immediately when the form is submitted.
            alert("Appointment booked! Confirmation email sent.");
        });
    }

    // Prevent selecting past dates
    let today = new Date().toISOString().split("T")[0];
    let dateInput = document.getElementById("date");

    if (dateInput) {
        dateInput.setAttribute("min", today);
    }

    // Enforce working hours if using native time input
    if (timeInput && timeInput.type === "time") {
        timeInput.addEventListener("input", function () {
            const value = timeInput.value;
            if (value < "08:30" || value > "18:00") {
                alert("Please choose a time between 08:30 and 18:00.");
                timeInput.value = "";
            }
        });
    }

    // Handle time selection dropdown (if you're still using the custom dropdown)
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
    let openingHour = 8; // 8:00 AM
    let closingHour = 18; // 6:00 PM
    let interval = 15; // 15-minute intervals
    let times = [];

    dropdown.innerHTML = ""; // Clear existing options

    for (let hour = openingHour; hour < closingHour; hour++) {
        for (let min = 0; min < 60; min += interval) {
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
            input.value = displayTime;
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
    const notification = document.createElement("div");
    notification.classList.add("custom-notification");
    notification.innerHTML = `<span>${message}</span>`;

    document.body.appendChild(notification);

    // Show animation
    setTimeout(() => {
        notification.classList.add("show");
    }, 100);

    // Remove after 4 seconds
    setTimeout(() => {
        notification.classList.remove("show");
        setTimeout(() => notification.remove(), 500);
    }, 4000);
}
