// ======================================================
// WIZARD VARIABLES
// ======================================================

let currentStep = 1;
const totalSteps = 4;

const wizard = document.getElementById("eventWizard");

const nextBtn = document.getElementById("nextBtn");
const previousBtn = document.getElementById("previousBtn");

const ticketContainer = document.getElementById("ticketContainer");
const addTicketButton = document.getElementById("addTicket");

const ticketCountLabel = document.getElementById("ticketCount");
const capacityCount = document.getElementById("capacityCount");
// const highestPrice = document.getElementById("highestPrice");

const paymentMethodCount = document.getElementById("paymentMethodCount");
const registrationTypeSummary = document.getElementById("registrationTypeSummary");
const estimatedRevenue = document.getElementById("estimatedRevenue");

const freeNotice = document.getElementById("freeEventNotice");

// Free / Paid buttons from Step 1
const freeRadio = document.getElementById("registration_free");
const paidRadio = document.getElementById("registration_paid");

let paymentType = "free";

document.addEventListener("DOMContentLoaded", function () {

    initialiseWizard();

});

// ======================================================
// INITIALISE
// ======================================================

function initialiseWizard() {

    showStep(1);

    refreshTickets();

    initialiseRegistrationType();

    initialisePaymentCards();

    attachValidationEvents();

}
// ======================================================
// SHOW STEP
// ======================================================

function showStep(step) {

    document.querySelectorAll(".wizard-step").forEach(section => {

        section.classList.remove("active");

    });

    document.getElementById("step" + step).classList.add("active");

    currentStep = step;

    if (step === 4) {

        populateSummary();

    }

    updateButtons();

    updateProgress();

}

function updateButtons() {

    previousBtn.classList.toggle("hidden", currentStep === 1);

    if (paymentType === "free") {

        if (currentStep === 2) {

            nextBtn.textContent = "Create Event";

        } else {

            nextBtn.textContent = "Next";

        }

        return;

    }

    // Paid Event

    if (currentStep === totalSteps) {

        nextBtn.textContent = "Create Event";

    } else {

        nextBtn.textContent = "Next";

    }

}
function updateProgress() {

    for (let i = 1; i <= totalSteps; i++) {

        const circle = document.getElementById("circle" + i);

        if (i <= currentStep) {

            circle.classList.remove(
                "bg-gray-300",
                "text-gray-700"
            );

            circle.classList.add(
                "bg-indigo-600",
                "text-white"
            );

        } else {

            circle.classList.remove(
                "bg-indigo-600",
                "text-white"
            );

            circle.classList.add(
                "bg-gray-300",
                "text-gray-700"
            );

        }

    }

    document.getElementById("line1").style.width =
        currentStep > 1 ? "100%" : "0";

    document.getElementById("line2").style.width =
        currentStep > 2 ? "100%" : "0";

    document.getElementById("line3").style.width =
        currentStep > 3 ? "100%" : "0";

}

// ======================================================
// NEXT
// ======================================================

nextBtn.addEventListener("click", function () {

    if (!validateCurrentStep()) {

        return;

    }

    // -----------------------------
    // STEP 1 -> STEP 2
    // -----------------------------

    if (currentStep === 1) {

        showStep(2);

        return;

    }

    // -----------------------------
    // STEP 2
    // -----------------------------

    if (currentStep === 2) {

        // FREE EVENT
        if (paymentType === "free") {

            showStep(4);

        }

        // PAID EVENT
        else {

            showStep(3);

        }

        return;

    }

    // -----------------------------
    // STEP 3
    // -----------------------------

    if (currentStep === 3) {

        showStep(4);

        return;

    }

    // -----------------------------
    // STEP 4
    // -----------------------------
    showSubmittingState();

    wizard.submit();

});
// ======================================================
// PREVIOUS
// ======================================================

previousBtn.addEventListener("click", function () {

    // Review Page

    if (currentStep === 4) {

        if (paymentType === "free") {

            showStep(2);

        } else {

            showStep(3);

        }

        return;

    }

    if (currentStep > 1) {

        showStep(currentStep - 1);

    }

});
// ================================================
// STEP VALIDATION
// ================================================

function validateCurrentStep() {

    switch (currentStep) {

        case 1:
            return validateStep1();

        case 2:
            return validateStep2();

        case 3:
            return validateStep3();

        default:
            return true;

    }

}
function validateStep1() {

    const title = document.getElementById("title");
    const eventType = document.getElementById("event_type");

    const startDate = document.getElementById("start_date");
    const endDate = document.getElementById("end_date");

    const registrationOpen = document.getElementById("registration_opens");
    const registrationClose = document.getElementById("registration_closes");

    if (title.value.trim() === "") {

        alert("Please enter an event title.");

        title.focus();

        return false;

    }

    if (eventType.value === "") {

        alert("Please select an event type.");

        eventType.focus();

        return false;

    }

    if (!startDate.value || !endDate.value) {

        alert("Please select both event start and end dates.");

        return false;

    }

    if (new Date(endDate.value) < new Date(startDate.value)) {

        alert("Event end date cannot be before the start date.");

        endDate.focus();

        return false;

    }

    if (!registrationOpen.value || !registrationClose.value) {

        alert("Please enter registration opening and closing dates.");

        return false;

    }

    if (new Date(registrationClose.value) <= new Date(registrationOpen.value)) {

        alert("Registration closing date must be after registration opening date.");

        registrationClose.focus();

        return false;

    }

    if (new Date(registrationClose.value) > new Date(endDate.value)) {

        alert("Registration cannot close after the event has ended.");

        registrationClose.focus();

        return false;

    }

    return true;

}
function attachValidationEvents() {

    [
        "start_date",
        "end_date",
        "registration_opens",
        "registration_closes"

    ].forEach(id => {

        const element = document.getElementById(id);

        if (element) {

            element.addEventListener("change", validateDates);

        }

    });

}
function validateDates() {

    const startDate = document.getElementById("start_date").value;

    const endDate = document.getElementById("end_date").value;

    const registrationOpen =
        document.getElementById("registration_opens").value;

    const registrationClose =
        document.getElementById("registration_closes").value;

    if (startDate && endDate) {

        if (new Date(endDate) < new Date(startDate)) {

            alert("Event end date cannot be before start date.");

            document.getElementById("end_date").value = "";

            return;

        }

    }

    if (registrationOpen && registrationClose) {

        if (new Date(registrationClose) <= new Date(registrationOpen)) {

            alert("Registration closing date must be after opening date.");

            document.getElementById("registration_closes").value = "";

            return;

        }

    }

    if (registrationClose && endDate) {

        if (new Date(registrationClose) > new Date(endDate)) {

            alert("Registration cannot close after the event ends.");

            document.getElementById("registration_closes").value = "";

            return;

        }

    }

}

// ======================================================
// STEP 2 - TICKETS
// ======================================================

// Add a new ticket
addTicketButton.addEventListener("click", addTicket);

function addTicket() {

    // Clone first ticket
    const newTicket = ticketContainer
        .querySelector(".ticket-card")
        .cloneNode(true);

    // Clear all values
    newTicket.querySelectorAll("input, textarea").forEach(field => {

        field.value = "";

    });

    // Remove previous validation styles if any
    newTicket.querySelectorAll("input, textarea").forEach(field => {

        field.classList.remove(
            "border-red-500",
            "ring-red-500"
        );

    });

    // Add ticket to container
    ticketContainer.appendChild(newTicket);

    // Refresh numbering and totals
    refreshTickets();

}

function attachEvents(card) {

    card.querySelectorAll("input, textarea").forEach(field => {

        field.addEventListener("input", updateRegistrationSummary);

    });

    const removeButton = card.querySelector(".removeTicket");

    if (removeButton) {

        removeButton.addEventListener("click", function () {

            card.remove();

            refreshTickets();

        });

    }

}
function refreshTickets() {

    const tickets = document.querySelectorAll(".ticket-card");

    ticketCountLabel.textContent = tickets.length;

    tickets.forEach((card, index) => {

        card.querySelector(".ticketTitle").textContent =
            "Ticket #" + (index + 1);

        const removeButton = card.querySelector(".removeTicket");

        if (removeButton) {

            removeButton.style.display =
                tickets.length === 1
                    ? "none"
                    : "inline-flex";

        }

        if (!card.dataset.initialized) {

            attachEvents(card);

            card.dataset.initialized = "true";

        }

    });

    updateRegistrationSummary();

}

function updateRegistrationSummary() {

    let totalCapacity = 0;

    let totalRevenue = 0;

    const tickets = document.querySelectorAll(".ticket-card");

    ticketCountLabel.textContent = tickets.length;

    tickets.forEach(ticket => {

        const capacity = Number(
            ticket.querySelector(".ticket-capacity")?.value || 0
        );

        const price = Number(
            ticket.querySelector(".ticket-price")?.value || 0
        );

        totalCapacity += capacity;

        if (paymentType === "paid") {

            totalRevenue += capacity * price;

        }

    });

    capacityCount.textContent =
        totalCapacity.toLocaleString();

    estimatedRevenue.textContent =
        "KES " + totalRevenue.toLocaleString();

}

document.addEventListener("input", function (e) {

    if (

        e.target.classList.contains("ticket-price") ||

        e.target.classList.contains("ticket-capacity")

    ) {

        updateRegistrationSummary();

    }

});

function validateStep2() {

    const tickets = document.querySelectorAll(".ticket-card");

    if (tickets.length === 0) {

        alert("Please add at least one ticket.");

        return false;

    }

    let totalCapacity = 0;

    const eventCapacity = parseInt(
        document.getElementById("capacity").value || 0
    );

    for (const ticket of tickets) {

        const name = ticket.querySelector(".ticket-name");

        const price = ticket.querySelector(".ticket-price");

        const capacity = ticket.querySelector(".ticket-capacity");

        // -------------------------
        // Ticket Name
        // -------------------------

        if (name.value.trim() === "") {

            alert("Please enter a ticket name.");

            name.focus();

            return false;

        }

        // -------------------------
        // FREE EVENT
        // -------------------------

        if (paymentType === "free") {

            if (Number(price.value) !== 0) {

                alert(
                    "This is a free event. Ticket prices must remain KES 0."
                );

                price.focus();

                return false;

            }

        }

        // -------------------------
        // PAID EVENT
        // -------------------------

        if (paymentType === "paid") {

            if (
                price.value === "" ||
                Number(price.value) <= 0
            ) {

                alert(
                    "Please enter a valid ticket price greater than KES 0."
                );

                price.focus();

                return false;

            }

        }

        // -------------------------
        // Capacity
        // -------------------------

        if (
            capacity.value === "" ||
            Number(capacity.value) <= 0
        ) {

            alert("Please enter a valid ticket capacity.");

            capacity.focus();

            return false;

        }

        totalCapacity += Number(capacity.value);

    }

    // -------------------------
    // Event Capacity Check
    // -------------------------

    if (
        eventCapacity > 0 &&
        totalCapacity > eventCapacity
    ) {

        alert(
            `The combined ticket capacity (${totalCapacity}) exceeds the event capacity (${eventCapacity}).`
        );

        return false;

    }

    return true;

}        // ======================================================
// STEP 3 - PAYMENT METHODS
// ======================================================

function initialisePaymentCards() {

    const cards = document.querySelectorAll(".payment-card");

    cards.forEach(card => {

        const checkbox = card.querySelector(".payment-checkbox");

        card.addEventListener("click", function () {

            checkbox.checked = !checkbox.checked;

            updatePaymentCards();

        });

    });

    updatePaymentCards();

}

function updatePaymentCards() {

    const cards = document.querySelectorAll(".payment-card");

    let selected = 0;

    cards.forEach(card => {

        const checkbox = card.querySelector(".payment-checkbox");

        if (checkbox.checked) {

            selected++;

            card.classList.add(
                "border-cyan-400",
                "ring-2",
                "ring-cyan-400",
                "bg-cyan-500/20",
                "scale-[1.02]"
            );

            card.classList.remove(
                "border-white/20"
            );

        }

        else {

            card.classList.remove(
                "border-cyan-400",
                "ring-2",
                "ring-cyan-400",
                "bg-cyan-500/20",
                "scale-[1.02]"
            );

            card.classList.add(
                "border-white/20"
            );

        }

    });

    paymentMethodCount.textContent = selected;

}
// ======================================================
// FREE / PAID
// ======================================================

function initialiseRegistrationType() {

    const freeCard = document.getElementById("freeCard");
    const paidCard = document.getElementById("paidCard");

    function updateType() {

        if (freeRadio.checked) {

            paymentType = "free";

            freeCard.classList.add(
                "border-cyan-400",
                "ring-2",
                "ring-cyan-400",
                "bg-cyan-500/20",
                "scale-[1.02]"
            );

            freeCard.classList.remove("border-white/20");

            paidCard.classList.remove(
                "border-cyan-400",
                "ring-2",
                "ring-cyan-400",
                "bg-cyan-500/20",
                "scale-[1.02]"
            );

            paidCard.classList.add("border-white/20");

            // Lock all ticket prices for free events
            document.querySelectorAll(".ticket-price").forEach(price => {

                price.value = 0;
                price.readOnly = true;

                price.classList.add(
                    "opacity-60",
                    "cursor-not-allowed"
                );

            });

        }

        else {

            paymentType = "paid";

            registrationTypeSummary.textContent = "PAID";

            paidCard.classList.add(
                "border-cyan-400",
                "ring-2",
                "ring-cyan-400",
                "bg-cyan-500/20",
                "scale-[1.02]"
            );

            paidCard.classList.remove("border-white/20");

            freeCard.classList.remove(
                "border-cyan-400",
                "ring-2",
                "ring-cyan-400",
                "bg-cyan-500/20",
                "scale-[1.02]"
            );

            freeCard.classList.add("border-white/20");

            // Enable ticket prices again
            document.querySelectorAll(".ticket-price").forEach(price => {

                price.readOnly = false;

                price.classList.remove(
                    "opacity-60",
                    "cursor-not-allowed"
                );

            });

        }

        updateRegistrationSummary();

        populateSummary();

        updateButtons();

    }

    freeRadio.addEventListener("change", updateType);
    paidRadio.addEventListener("change", updateType);

    updateType();

}

function validateStep3() {

    // Free event

    if (paymentType === "free") {

        return true;

    }

    const checked = document.querySelectorAll(

        ".payment-checkbox:checked"

    );

    if (checked.length === 0) {

        alert(

            "Please select at least one payment method."

        );

        return false;

    }

    return true;

}

function formatDate(value) {

    return new Date(value).toLocaleString("en-KE", {

        day: "numeric",

        month: "short",

        year: "numeric",

        hour: "2-digit",

        minute: "2-digit"

    });

}

function populateEventDetails() {

    // ==========================
    // Event Title
    // ==========================

    document.getElementById("summaryTitle").textContent =
        document.getElementById("title").value || "-";

    // ==========================
    // Event Type
    // ==========================

    const eventType = document.getElementById("event_type");

    document.getElementById("summaryEventType").textContent =
        eventType.options[eventType.selectedIndex].text;

    // ==========================
    // Venue
    // ==========================

    const location = document.getElementById("location");

    document.getElementById("summaryVenue").textContent =
        location && location.value.trim() !== ""
            ? location.value
            : "Not specified";

    // ==========================
    // Registration Type
    // ==========================

    document.getElementById("summaryRegistration").textContent =
        paymentType.toUpperCase();

    // ==========================
    // Event Dates
    // ==========================

    const start =
        document.getElementById("start_date").value;

    const end =
        document.getElementById("end_date").value;

    document.getElementById("summaryDates").textContent =

        start && end

            ? `${formatDate(start)}  →  ${formatDate(end)}`

            : "-";

    // ==========================
    // Registration Dates
    // ==========================

    const open =
        document.getElementById("registration_opens").value;

    const close =
        document.getElementById("registration_closes").value;

    document.getElementById("summaryRegistrationDates").textContent =

        open && close

            ? `${formatDate(open)}  →  ${formatDate(close)}`

            : "-";

}

function populateTicketSummary() {

    const table =
        document.getElementById("summaryTicketTable");

    table.innerHTML = "";

    document.querySelectorAll(".ticket-card").forEach(ticket => {

        const name =
            ticket.querySelector(".ticket-name").value;

        const price =
            Number(ticket.querySelector(".ticket-price").value || 0);

        const capacity =
            Number(ticket.querySelector(".ticket-capacity").value || 0);

        const row = document.createElement("tr");

        row.className = "hover:bg-white/5";

        row.innerHTML = `

            <td class="px-5 py-4 text-white">

                ${name}

            </td>

            <td class="px-5 py-4 text-center text-cyan-200">

                ${paymentType === "free"

                ? "FREE"

                : "KES " + price.toLocaleString()
            }

            </td>

            <td class="px-5 py-4 text-center text-white">

                ${capacity.toLocaleString()}

            </td>

        `;

        table.appendChild(row);

    });

}

function populatePaymentSummary() {

    const container = document.getElementById("summaryPayments");

    container.innerHTML = "";

    // --------------------------------
    // FREE EVENT
    // --------------------------------

    if (paymentType === "free") {

        container.innerHTML = `

            <div class="rounded-xl border border-green-400/30 bg-green-500/10 px-5 py-4">

                <span class="text-green-200">

                    ✓ No payment required

                </span>

            </div>

        `;

        return;

    }

    // --------------------------------
    // PAID EVENT
    // --------------------------------

    document.querySelectorAll(".payment-checkbox:checked")
        .forEach(checkbox => {

            const card = checkbox.closest(".payment-card");

            const name = card.querySelector("h4").textContent.trim();

            container.innerHTML += `

                <div class="rounded-xl border border-cyan-400/30 bg-cyan-500/10 px-5 py-4">

                    <span class="text-cyan-200">

                        ✓ ${name}

                    </span>

                </div>

            `;

        });

}


function populateTotals() {

    let tickets = 0;

    let capacity = 0;

    let revenue = 0;

    document.querySelectorAll(".ticket-card").forEach(ticket => {

        tickets++;

        const cap =
            Number(ticket.querySelector(".ticket-capacity").value || 0);

        const price =
            Number(ticket.querySelector(".ticket-price").value || 0);

        capacity += cap;

        if (paymentType === "paid") {

            revenue += cap * price;

        }

    });

    document.getElementById("summaryTicketCount").textContent =
        tickets;

    document.getElementById("summaryCapacity").textContent =
        capacity.toLocaleString();

    document.getElementById("summaryRevenue").textContent =

        paymentType === "free"

            ? "FREE"

            : "KES " + revenue.toLocaleString();

}

function showSubmittingState() {

    nextBtn.disabled = true;

    nextBtn.classList.add(
        "opacity-70",
        "cursor-not-allowed"
    );

    nextBtn.innerHTML = `

        <svg
            class="animate-spin h-5 w-5 inline mr-2"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24">

            <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4">
            </circle>

            <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v4l3-3-3-3v4A10 10 0 002 12h2z">
            </path>

        </svg>

        Creating Event...

    `;

}

function populateSummary() {

    populateEventDetails();

    populateTicketSummary();

    populatePaymentSummary();

    populateTotals();

}
