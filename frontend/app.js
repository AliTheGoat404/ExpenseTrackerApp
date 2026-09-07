const API_URL = "http://127.0.0.1:5000";
let token = localStorage.getItem("access_token");
let authMode = "login";
let currentPage = 1;
let debounceTimer;

document.addEventListener("DOMContentLoaded", () => {
    if (token) showApp();
});

function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.getAttribute("data-theme") === "dark";
    html.setAttribute("data-theme", isDark ? "light" : "dark");
    document.getElementById("theme-icon").textContent = isDark ? "☀️" : "🌙";
    document.getElementById("theme-text").textContent = isDark ? "Light Mode" : "Dark Mode";
}

function switchAuthTab(mode) {
    authMode = mode;
    document.getElementById("tab-login").classList.toggle("active", mode === "login");
    document.getElementById("tab-register").classList.toggle("active", mode === "register");
    document.getElementById("auth-submit-btn").textContent = mode === "login" ? "Sign In" : "Register";
}

async function handleAuth(e) {
    e.preventDefault();
    const username = document.getElementById("auth-username").value.trim();
    const password = document.getElementById("auth-password").value;
    const alert = document.getElementById("auth-alert");

    alert.classList.add("hidden");

    try {
        const res = await fetch(`${API_URL}/${authMode}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.error || "Authentication failed");

        if (authMode === "register") {
            switchAuthTab("login");
            alert.textContent = "Registration successful! Please login.";
            alert.classList.remove("hidden");
        } else {
            token = data.access_token;
            localStorage.setItem("access_token", token);
            localStorage.setItem("user", username);
            showApp();
        }
    } catch (err) {
        alert.textContent = err.message;
        alert.classList.remove("hidden");
    }
}

function showApp() {
    document.getElementById("auth-screen").classList.add("hidden");
    document.getElementById("app-screen").classList.remove("hidden");
    document.getElementById("user-display").textContent = localStorage.getItem("user") || "User";
    loadTransactions(1);
}

function logout() {
    localStorage.clear();
    token = null;
    document.getElementById("app-screen").classList.add("hidden");
    document.getElementById("auth-screen").classList.remove("hidden");
}

function debouncedFetch() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => loadTransactions(1), 150); // Lowered delay for snappier UI
}

async function loadTransactions(page = 1) {
    currentPage = page;
    const category = document.getElementById("filter-category").value;
    const start_date = document.getElementById("filter-start-date").value;
    const end_date = document.getElementById("filter-end-date").value;

    let url = `${API_URL}/transactions?page=${page}&per_page=8`;
    if (category) url += `&category=${encodeURIComponent(category)}`;
    if (start_date) url += `&start_date=${start_date}`;
    if (end_date) url += `&end_date=${end_date}`;

    try {
        const res = await fetch(url, {
            headers: { Authorization: `Bearer ${token}` }
        });
        if (res.status === 401) return logout();

        const data = await res.json();
        renderTable(data.transactions);
        renderPagination(data.pagination);
    } catch (err) {
        console.error(err);
    }
}

function renderTable(transactions) {
    const tbody = document.getElementById("transaction-rows");
    if (!transactions || !transactions.length) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center">No transactions found.</td></tr>`;
        document.getElementById("metric-total").textContent = "$0.00";
        return;
    }

    let total = 0;
    // Fast string builder
    let rowsHtml = "";
    for (let i = 0; i < transactions.length; i++) {
        const t = transactions[i];
        total += t.amount;
        rowsHtml += `
            <tr>
                <td>${new Date(t.date).toLocaleDateString()}</td>
                <td><strong>${t.category}</strong></td>
                <td>${t.description || '-'}</td>
                <td>$${t.amount.toFixed(2)}</td>
                <td class="text-right">
                    <button class="btn btn-secondary" onclick="editModal(${t.id}, ${t.amount}, '${t.category}', '${t.description}')">Edit</button>
                    <button class="btn btn-danger" onclick="deleteTransaction(${t.id})">Delete</button>
                </td>
            </tr>
        `;
    }

    tbody.innerHTML = rowsHtml;
    document.getElementById("metric-total").textContent = `$${total.toFixed(2)}`;
}

function renderPagination(p) {
    document.getElementById("metric-count").textContent = p.total_records;
    document.getElementById("pagination-info").textContent = `Page ${p.current_page} of ${p.total_pages || 1}`;
    document.getElementById("btn-prev").disabled = !p.has_prev;
    document.getElementById("btn-next").disabled = !p.has_next;
}

function changePage(delta) {
    loadTransactions(currentPage + delta);
}

function resetFilters() {
    document.getElementById("filter-category").value = "";
    document.getElementById("filter-start-date").value = "";
    document.getElementById("filter-end-date").value = "";
    loadTransactions(1);
}

function openModal() {
    document.getElementById("edit-id").value = "";
    document.getElementById("modal-title").textContent = "Add Expense";
    document.getElementById("transaction-form").reset();
    document.getElementById("form-alert").classList.add("hidden");
    document.getElementById("modal").classList.remove("hidden");
}

function editModal(id, amount, category, description) {
    document.getElementById("edit-id").value = id;
    document.getElementById("modal-title").textContent = "Edit Expense";
    document.getElementById("tx-amount").value = amount;
    document.getElementById("tx-category").value = category;
    document.getElementById("tx-description").value = description;
    document.getElementById("form-alert").classList.add("hidden");
    document.getElementById("modal").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("modal").classList.add("hidden");
}

async function saveTransaction(e) {
    e.preventDefault();
    const id = document.getElementById("edit-id").value;
    const amount = parseFloat(document.getElementById("tx-amount").value);
    const category = document.getElementById("tx-category").value;
    const description = document.getElementById("tx-description").value;
    const alert = document.getElementById("form-alert");

    const method = id ? "PUT" : "POST";
    const url = id ? `${API_URL}/transactions/${id}` : `${API_URL}/transactions`;

    try {
        const res = await fetch(url, {
            method,
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ amount, category, description })
        });
        const data = await res.json();

        if (!res.ok) {
            const msg = data.errors ? Object.values(data.errors).flat().join(", ") : data.error;
            throw new Error(msg || "Validation error");
        }

        closeModal();
        loadTransactions(currentPage);
    } catch (err) {
        alert.textContent = err.message;
        alert.classList.remove("hidden");
    }
}

async function deleteTransaction(id) {
    if (!confirm("Are you sure you want to delete this expense?")) return;
    try {
        await fetch(`${API_URL}/transactions/${id}`, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` }
        });
        loadTransactions(currentPage);
    } catch (err) {
        console.error(err);
    }
}