(function () {
    const rows = document.querySelectorAll('.org-row');
    const previewAvatar = document.getElementById('preview-avatar');
    const previewName = document.getElementById('preview-name');
    const previewCode = document.getElementById('preview-code');
    const previewStatusBadge = document.getElementById('preview-status-badge');
    const previewStatusDot = document.getElementById('preview-status-dot');
    const previewStatusText = document.getElementById('preview-status-text');
    const previewUsers = document.getElementById('preview-users');
    const previewEvents = document.getElementById('preview-events');
    const previewAdmin = document.getElementById('preview-admin');
    const previewAdminEmail = document.getElementById('preview-admin-email');
    const previewEmail = document.getElementById('preview-email');
    const previewAddress = document.getElementById('preview-address');
    const previewCreated = document.getElementById('preview-created');
    const previewUpdated = document.getElementById('preview-updated');
    const previewManageBtn = document.getElementById('preview-manage-btn');
    const previewStatusBtn = document.getElementById('preview-status-btn');
    const emptyRow = document.getElementById('empty-search-row');

    function updatePreview(row) {
        const id = row.getAttribute('data-id') || '1';
        const name = row.getAttribute('data-name');
        const code = row.getAttribute('data-code');
        const initials = row.getAttribute('data-initials');
        const status = row.getAttribute('data-status');
        const users = row.getAttribute('data-users');
        const events = row.getAttribute('data-events');
        const admin = row.getAttribute('data-admin');
        const adminEmail = row.getAttribute('data-admin-email');
        const email = row.getAttribute('data-email');
        const address = row.getAttribute('data-address');
        const created = row.getAttribute('data-created');
        const updated = row.getAttribute('data-updated');

        previewAvatar.textContent = initials;
        previewName.textContent = name;
        previewCode.textContent = code;
        previewUsers.textContent = users;
        previewEvents.textContent = events;
        previewAdmin.textContent = admin;
        previewAdminEmail.textContent = adminEmail;
        previewEmail.textContent = email;
        previewAddress.textContent = address;
        previewCreated.textContent = created;
        previewUpdated.textContent = updated;
        previewManageBtn.href = '/organisations/' + id + '/';

        if (status === 'active') {
            previewStatusText.textContent = 'Active';
            previewStatusDot.className = 'w-1.5 h-1.5 rounded-full bg-secondary-container';
            previewStatusBadge.className = 'px-space-xs py-0.5 rounded-full bg-surface-container text-primary font-caption text-caption font-semibold flex items-center gap-1';
            previewStatusBtn.textContent = 'Deactivate Organisation';
        } else {
            previewStatusText.textContent = 'Inactive';
            previewStatusDot.className = 'w-1.5 h-1.5 rounded-full bg-outline';
            previewStatusBadge.className = 'px-space-xs py-0.5 rounded-full bg-surface-container-high text-on-surface-variant font-caption text-caption font-semibold flex items-center gap-1';
            previewStatusBtn.textContent = 'Activate Organisation';
        }
    }

    rows.forEach(row => {
        row.addEventListener('click', () => {
            rows.forEach(r => {
                r.classList.remove('bg-surface-container-low/70');
                r.classList.add('bg-surface-container-lowest');
            });
            row.classList.remove('bg-surface-container-lowest');
            row.classList.add('bg-surface-container-low/70');
            updatePreview(row);
        });
    });

    let currentFilter = 'all';
    const pills = document.querySelectorAll('.filter-status-pill');
    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            pills.forEach(p => {
                p.classList.remove('bg-surface-container-lowest', 'text-primary', 'shadow-xs', 'font-semibold');
                p.classList.add('text-on-surface-variant', 'font-medium');
            });
            pill.classList.add('bg-surface-container-lowest', 'text-primary', 'shadow-xs', 'font-semibold');
            pill.classList.remove('text-on-surface-variant', 'font-medium');
            currentFilter = pill.getAttribute('data-status');
            filterRows();
        });
    });

    const searchInput = document.getElementById('org-search');
    function filterRows() {
        const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
        let visibleCount = 0;

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const status = row.getAttribute('data-status');
            const matchesQuery = !query || text.includes(query);
            const matchesFilter = currentFilter === 'all' || status === currentFilter;

            if (matchesQuery && matchesFilter) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        if (emptyRow) {
            emptyRow.classList.toggle('hidden', visibleCount > 0);
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterRows);
    }
})();


document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("organisationModal");
    const form = document.getElementById("createOrganisationForm");
    const steps = [...document.querySelectorAll(".organisation-form-step")];
    const labels = [...document.querySelectorAll(".modal-step-label")];

    const openButton = document.getElementById("openOrganisationModal");
    const closeButton = document.getElementById("closeOrganisationModal");
    const cancelButton = document.getElementById("cancelOrganisationModal");
    const backButton = document.getElementById("previousOrganisationStep");
    const nextButton = document.getElementById("nextOrganisationStep");
    const submitButton = document.getElementById("submitOrganisation");

    let currentStep = 0;

    function showStep(index) {
        currentStep = index;

        steps.forEach((step, i) => {
            step.classList.toggle("hidden", i !== index);
        });

        labels.forEach((label, i) => {
            label.classList.toggle("border-indigo-600", i === index);
            label.classList.toggle("text-indigo-700", i === index);
            label.classList.toggle("font-semibold", i === index);

            label.classList.toggle("border-slate-200", i !== index);
            label.classList.toggle("text-slate-400", i !== index);
        });

        backButton.disabled = index === 0;
        backButton.classList.toggle("invisible", index === 0);

        nextButton.classList.toggle("hidden", index === steps.length - 1);
        submitButton.classList.toggle("hidden", index !== steps.length - 1);
    }

    function openModal() {
        modal.classList.remove("hidden");
        modal.classList.add("flex");
        showStep(0);
    }

    function closeModal() {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
    }

    function validateStep(index) {
        const fields = steps[index].querySelectorAll("input, textarea, select");

        for (const field of fields) {
            if (!field.checkValidity()) {
                field.reportValidity();
                return false;
            }
        }

        return true;
    }

    function fillReview() {
        const values = {
            reviewOrgName: document.getElementById("orgName").value,
            reviewOrgCode: document.getElementById("orgCode").value,
            reviewOrgEmail: document.getElementById("orgEmail").value || "Not provided",
            reviewOrgAddress: document.getElementById("orgAddress").value || "Not provided",
            reviewAdminName:
                document.getElementById("adminFirstName").value + " " +
                document.getElementById("adminLastName").value,
            reviewAdminEmail: document.getElementById("adminEmail").value,
            reviewAdminPhone: document.getElementById("adminPhone").value || "Not provided"
        };

        Object.entries(values).forEach(([id, value]) => {
            document.getElementById(id).textContent = value;
        });
    }

    openButton.addEventListener("click", openModal);
    closeButton.addEventListener("click", closeModal);
    cancelButton.addEventListener("click", closeModal);

    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && !modal.classList.contains("hidden")) {
            closeModal();
        }
    });

    nextButton.addEventListener("click", function () {
        if (!validateStep(currentStep)) {
            return;
        }

        if (currentStep < steps.length - 1) {
            if (currentStep === 1) {
                fillReview();
            }

            showStep(currentStep + 1);
        }
    });

    backButton.addEventListener("click", function () {
        if (currentStep > 0) {
            showStep(currentStep - 1);
        }
    });

    form.addEventListener("submit", function (event) {
        // Validate all steps before submitting the complete form.
        for (let i = 0; i < steps.length - 1; i++) {
            if (!validateStep(i)) {
                event.preventDefault();
                showStep(i);
                return;
            }
        }

        if (!validateStep(steps.length - 1)) {
            event.preventDefault();
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = "Creating...";
    });

    showStep(0);
});
