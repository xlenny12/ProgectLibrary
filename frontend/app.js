
const searchInput = document.getElementById('searchInput');
const genreSelect = document.getElementById('genreSelect');
const searchBtn = document.getElementById('searchBtn');
const booksGrid = document.getElementById('booksGrid');


async function fetchBooks() {
  
    const searchQuery = searchInput.value.trim();
    const genre = genreSelect.value;

    // Формуємо правильний URL
    // Увага: коли бекенд буде повністю готовий, розкоментуй ці рядки:
    /*
    try {
        const url = `/api/books?search=${searchQuery}&genre=${genre}`;
        const response = await fetch(url);
        const books = await response.json();
        renderBooks(books);
    } catch (error) {
        console.error("Помилка зв'язку з бекендом:", error);
    }
    */

    // ПОКИ БЕКЕНД НЕ ПІДКЛЮЧЕНО: імітуємо отримання даних
    console.log(`Імітація запиту: /api/books?search=${searchQuery}&genre=${genre}`);
    
    const mockData = [
        { title: "The Midnight Library", author: "Matt Haig", coverClass: "bc1", stars: "★★★★★" },
        { title: `Книга про ${searchQuery || 'щось'}`, author: "Unknown", coverClass: "bc2", stars: "★★★★☆" }
    ];
    renderBooks(mockData);
}

function filterByGenre(genre) {
  const buttons = document.querySelectorAll(".genre-btn");
  buttons.forEach((btn) => btn.classList.remove("active"));
  event.target.classList.add("active");
  loadBooks(genre);
}

// ========================================
// BORROW - CHECKOUT & RETURN
// ========================================

let currentBorrowBook = null;

function openBorrowModal(bookId, bookTitle) {
  if (!currentUser) {
    openModal("login");
    return;
  }

  currentBorrowBook = bookId;
  document.getElementById("borrow-modal-title").textContent = `Borrow "${bookTitle}"`;
  document.getElementById("borrow-qty").value = 1;
  document.getElementById("borrow-days").value = 14;
  updateBorrowPreview();
  document.getElementById("borrow-modal-overlay").style.display = "flex";
}

function closeBorrowModal() {
  document.getElementById("borrow-modal-overlay").style.display = "none";
  currentBorrowBook = null;
}

function updateBorrowPreview() {
  const days = parseInt(document.getElementById("borrow-days").value);
  const due = new Date();
  due.setDate(due.getDate() + days);
  document.getElementById("borrow-due-preview").textContent = `Due by ${due.toLocaleDateString()}`;
}

async function submitBorrow() {
  const qty = parseInt(document.getElementById("borrow-qty").value);
  const days = parseInt(document.getElementById("borrow-days").value);

  if (qty < 1 || days < 1) {
    alert("Invalid quantity or days");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/borrows`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${currentToken}`,
      },
      body: JSON.stringify({
        book_id: currentBorrowBook,
        quantity: qty,
        days: days,
      }),
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Borrow failed");
    }

    showToast("Book borrowed successfully!");
    closeBorrowModal();
    loadBooks();
    loadUserBorrows();
  } catch (error) {
    alert("Error: " + error.message);
  }
}

async function loadUserBorrows() {
  if (!currentUser) return;

  try {
    const res = await fetch(`${API_BASE}/borrows/me`, {
      headers: { Authorization: `Bearer ${currentToken}` },
    });

    if (!res.ok) throw new Error("Failed to load borrows");

    const borrows = await res.json();
    renderBorrowsList(borrows);
  } catch (error) {
    console.error("Error loading borrows:", error);
  }
}

function renderBorrowsList(borrows) {
  const list = document.getElementById("borrows-list");
  list.innerHTML = "";

  if (borrows.length === 0) {
    list.innerHTML = "<p>You haven't borrowed any books yet.</p>";
    return;
  }

  borrows.forEach((borrow) => {
    const isOverdue = new Date() > new Date(borrow.due_date);
    const item = document.createElement("div");
    item.className = `borrow-item ${borrow.returned ? "returned" : ""} ${isOverdue ? "overdue" : ""}`;
    item.innerHTML = `
      <div class="borrow-info">
        <div class="borrow-title">${escapeHtml(borrow.book_type)} / ${escapeHtml(borrow.book_id)}</div>
        <div class="borrow-dates">
          Borrowed: ${new Date(borrow.date_taken).toLocaleDateString()} |
          Due: ${new Date(borrow.due_date).toLocaleDateString()}
          ${isOverdue ? " <span style='color: red;'>(OVERDUE)</span>" : ""}
        </div>
        <div class="borrow-qty">Qty: ${escapeHtml(borrow.quantity)}</div>
      </div>
      ${
        !borrow.returned
          ? `<button class="btn-small" onclick="submitReturnBook('${borrow.id}')">Return</button>`
          : `<span class="badge-returned">Returned</span>`
      }
    `;
    list.appendChild(item);
  });
}

async function submitReturnBook(borrowId) {
  try {
    const res = await fetch(`${API_BASE}/borrows/${borrowId}/return`, {
      method: "POST",
      headers: { Authorization: `Bearer ${currentToken}` },
    });

    if (!res.ok) throw new Error("Return failed");

    showToast("Book returned successfully!");
    loadUserBorrows();
    loadBooks();
  } catch (error) {
    alert("Error: " + error.message);
  }
}

// ========================================
// USER PROFILE
// ========================================

async function loadUserProfile() {
  if (!currentUser) return;

  const profileHtml = `
    <div style="padding: 20px;">
      <h3>Profile Information</h3>
      <p><strong>Name:</strong> ${escapeHtml(currentUser.full_name)}</p>
      <p><strong>Email:</strong> ${escapeHtml(currentUser.email)}</p>
      <p><strong>Phone:</strong> ${escapeHtml(currentUser.phone)}</p>
      <p><strong>Address:</strong> ${escapeHtml(currentUser.address)}</p>
      <p><strong>Date of Birth:</strong> ${escapeHtml(currentUser.date_of_birth)}</p>
      <p><strong>Role:</strong> <span class="role-badge">${escapeHtml(currentUser.role)}</span></p>
      <button class="btn-small" onclick="openEditProfile()">Edit Profile</button>
      <button class="btn-small" style="background: #dc3545;" onclick="confirmDeleteAccount()">Delete Account (GDPR)</button>
    </div>
  `;

  document.getElementById("profile-details").innerHTML = profileHtml;
  document.getElementById("profile-card").style.display = "block";
}

function openEditProfile() {
  document.getElementById("edit-name").value = currentUser.full_name;
  document.getElementById("edit-email").value = currentUser.email;
  document.getElementById("edit-phone").value = currentUser.phone;
  document.getElementById("edit-address").value = currentUser.address;
  document.getElementById("edit-dob").value = currentUser.date_of_birth;
  document.getElementById("edit-profile-overlay").style.display = "flex";
}

function closeEditProfile() {
  document.getElementById("edit-profile-overlay").style.display = "none";
}

async function submitEditProfile() {
  const updates = {
    full_name: document.getElementById("edit-name").value,
    phone: document.getElementById("edit-phone").value,
    address: document.getElementById("edit-address").value,
  };

  try {
    const res = await fetch(`${API_BASE}/users/me`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${currentToken}`,
      },
      body: JSON.stringify(updates),
    });

    if (!res.ok) throw new Error("Update failed");

    const updated = await res.json();
    saveUserSession(updated, currentToken, refreshToken);
    closeEditProfile();
    loadUserProfile();
    showToast("Profile updated successfully!");
  } catch (error) {
    alert("Error: " + error.message);
  }
}

function confirmDeleteAccount() {
  if (confirm("Are you sure you want to delete your account? This cannot be undone.")) {
    deleteAccount();
  }
}

async function deleteAccount() {
  try {
    const res = await fetch(`${API_BASE}/users/me`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${currentToken}` },
    });

    if (!res.ok) throw new Error("Deletion failed");

    showToast("Your account has been deleted.");
    logout();
  } catch (error) {
    alert("Error: " + error.message);
  }
}

// ========================================
// ADMIN PANEL
// ========================================

async function loadAdminPanel() {
  if (!canUseStaffPanel()) return;

  document.getElementById("btn-add-user").style.display = isAdmin() ? "block" : "none";
  document.getElementById("btn-add-book").style.display = isAdmin() ? "block" : "none";
  document.getElementById("btn-notify-sms").style.display = "inline-flex";
  document.getElementById("btn-notify-email").style.display = "inline-flex";

  loadAdminUsers();
  loadAdminBooks();
  loadAdminOverdue();
}

async function loadAdminUsers() {
  try {
    const res = await fetch(`${API_BASE}/users`, {
      headers: { Authorization: `Bearer ${currentToken}` },
    });
    if (!res.ok) throw new Error();
    const users = await res.json();

    const list = document.getElementById("admin-users-list");
    list.innerHTML = "";
    users.forEach((user) => {
      const item = document.createElement("div");
      item.className = "admin-list-item";
      const deleteButton = isAdmin()
        ? `<button class="btn-danger-sm" onclick="adminDeleteUser('${escapeJsAttr(user.id)}')">Delete</button>`
        : "";
      item.innerHTML = `
        <div>
          <strong>User ID: ${escapeHtml(user.id)}</strong><br/>
          <small>Personal data hidden by policy</small><br/>
          <span class="role-badge">${escapeHtml(user.role)}</span>
        </div>
        ${deleteButton}
      `;
      list.appendChild(item);
    });
  } catch (error) {
    console.error("Error loading admin users:", error);
  }
}

async function loadAdminBooks() {
  try {
    const res = await fetch(`${API_BASE}/books`, {
      headers: { Authorization: `Bearer ${currentToken}` },
    });
    if (!res.ok) throw new Error();
    const books = await res.json();

    const list = document.getElementById("admin-books-list");
    list.innerHTML = "";
    books.forEach((book) => {
      const item = document.createElement("div");
      item.className = "admin-list-item";
      const editButton = isAdmin()
        ? `<button class="btn-small" onclick="openEditBookModal('${escapeJsAttr(book.id)}')">Edit</button>`
        : "";
      const deleteButton = isAdmin()
        ? `<button class="btn-danger-sm" onclick="adminDeleteBook('${escapeJsAttr(book.id)}')">Delete</button>`
        : "";
      item.innerHTML = `
        <div>
          <strong>${escapeHtml(book.title)}</strong> by ${escapeHtml(book.author)}<br/>
          <small>${escapeHtml(book.book_type)} | ${escapeHtml(book.available_qty)}/${escapeHtml(book.total_qty)}</small>
        </div>
        ${editButton}
        ${deleteButton}
      `;
      list.appendChild(item);
    });
  } catch (error) {
    console.error("Error loading admin books:", error);
  }
}

async function loadAdminOverdue() {
  try {
    const res = await fetch(`${API_BASE}/borrows/overdue`, {
      headers: { Authorization: `Bearer ${currentToken}` },
    });
    if (!res.ok) throw new Error();
    const borrows = await res.json();

    const list = document.getElementById("admin-overdue-list");
    list.innerHTML = "";
    if (borrows.length === 0) {
      list.innerHTML = "<p>No overdue books</p>";
      return;
    }
    borrows.forEach((borrow) => {
      const item = document.createElement("div");
      item.className = "admin-list-item overdue";
      item.innerHTML = `
        <div>
          <strong>${escapeHtml(borrow.book_type)} / ${escapeHtml(borrow.book_id)}</strong><br/>
          <small>User: ${escapeHtml(borrow.user_id)}</small><br/>
          <small>Due: ${new Date(borrow.due_date).toLocaleDateString()}</small>
        </div>
      `;
      list.appendChild(item);
    });
  } catch (error) {
    console.error("Error loading overdue:", error);
  }
}

function openAddBookModal() {
  editingBookId = null;
  document.getElementById("add-book-error").style.display = "none";
  document.getElementById("add-book-modal-title").textContent = "Add Book";
  document.getElementById("book-title").value = "";
  document.getElementById("book-author").value = "";
  document.getElementById("book-genre").value = "fantasy";
  document.getElementById("book-total").value = 1;
  document.getElementById("book-available").value = 1;
  document.getElementById("add-book-modal-overlay").style.display = "flex";
}

function closeAddBookModal() {
  editingBookId = null;
  document.getElementById("add-book-modal-overlay").style.display = "none";
}

function showAddBookError(message) {
  const errorDiv = document.getElementById("add-book-error");
  errorDiv.textContent = message;
  errorDiv.style.display = "block";
}

async function openEditBookModal(bookId) {
  if (!isAdmin()) {
    showToast("Only administrators can edit books");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/books/${bookId}`, {
      headers: { Authorization: `Bearer ${currentToken}` },
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(formatApiError(data, "Failed to load book"));
    }

    const book = await res.json();
    editingBookId = book.id;
    document.getElementById("add-book-error").style.display = "none";
    document.getElementById("add-book-modal-title").textContent = "Edit Book";
    document.getElementById("book-title").value = book.title;
    document.getElementById("book-author").value = book.author;
    document.getElementById("book-genre").value = book.book_type;
    document.getElementById("book-total").value = book.total_qty;
    document.getElementById("book-available").value = book.available_qty;
    document.getElementById("add-book-modal-overlay").style.display = "flex";
  } catch (error) {
    showToast(error.message);
  }
}

function openCreateUserModal() {
  if (!isAdmin()) {
    showToast("Only administrators can create users");
    return;
  }
  document.getElementById("create-user-error").style.display = "none";
  document.getElementById("create-user-modal-overlay").style.display = "flex";
}

function closeCreateUserModal() {
  document.getElementById("create-user-modal-overlay").style.display = "none";
}

function showCreateUserError(message) {
  const errorDiv = document.getElementById("create-user-error");
  errorDiv.textContent = message;
  errorDiv.style.display = "block";
}

function clearCreateUserForm() {
  ["cu-name", "cu-dob", "cu-address", "cu-phone", "cu-email", "cu-password"].forEach((id) => {
    document.getElementById(id).value = "";
  });
  document.getElementById("cu-role").value = "User";
  document.getElementById("create-user-error").style.display = "none";
}

async function submitCreateUser() {
  if (!isAdmin()) return;

  const payload = {
    full_name: document.getElementById("cu-name").value.trim(),
    date_of_birth: document.getElementById("cu-dob").value,
    address: document.getElementById("cu-address").value.trim(),
    phone: document.getElementById("cu-phone").value.trim(),
    email: document.getElementById("cu-email").value.trim(),
    password: document.getElementById("cu-password").value,
    role: document.getElementById("cu-role").value,
  };

  if (!payload.full_name || !payload.date_of_birth || !payload.address || !payload.phone || !payload.email || !payload.password) {
    showCreateUserError("All fields are required");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/admin/users`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${currentToken}`,
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(formatApiError(data, "Failed to create user"));
    }

    showToast("User created");
    clearCreateUserForm();
    closeCreateUserModal();
    loadAdminUsers();
  } catch (error) {
    showCreateUserError(error.message);
  }
}

async function submitAddBook() {
  const title = document.getElementById("book-title").value.trim();
  const author = document.getElementById("book-author").value.trim();
  const genre = document.getElementById("book-genre").value;
  const total = parseInt(document.getElementById("book-total").value);
  const available = parseInt(document.getElementById("book-available").value);

  if (!title || !author || Number.isNaN(total) || Number.isNaN(available) || total < 1 || available < 0) {
    showAddBookError("Please fill in all required fields with valid quantities");
    return;
  }

  if (available > total) {
    showAddBookError("Available copies cannot exceed total copies");
    return;
  }

  try {
    const isEditing = Boolean(editingBookId);
    const res = await fetch(`${API_BASE}/books${isEditing ? `/${editingBookId}` : ""}`, {
      method: isEditing ? "PATCH" : "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${currentToken}`,
      },
      body: JSON.stringify({
        title,
        author,
        book_type: genre,
        total_qty: total,
        available_qty: available,
      }),
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(formatApiError(data, isEditing ? "Failed to update book" : "Failed to add book"));
    }

    showToast(isEditing ? "Book updated successfully!" : "Book added successfully!");
    closeAddBookModal();
    loadAdminBooks();
    loadBooks();

    document.getElementById("book-title").value = "";
    document.getElementById("book-author").value = "";
    document.getElementById("book-total").value = 1;
    document.getElementById("book-available").value = 1;
  } catch (error) {
    showAddBookError(error.message);
  }
}

async function sendOverdueNotifications(useSms) {
  if (!canUseStaffPanel()) {
    showToast("Only staff roles can send reminders");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/admin/notify/overdue?use_sms=${useSms}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${currentToken}` },
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(formatApiError(data, "Failed to send reminders"));
    }

    const data = await res.json();
    showToast(`${data.notified} overdue reminder record(s) processed`);
    loadAdminOverdue();
    updateStats();
  } catch (error) {
    showToast(error.message);
  }
}

async function adminDeleteUser(userId) {
  if (!confirm("Are you sure you want to delete this user?")) return;

  try {
    const res = await fetch(`${API_BASE}/admin/users/${userId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${currentToken}` },
    });

    if (!res.ok) throw new Error();
    showToast("User deleted");
    loadAdminUsers();
  } catch (error) {
    alert("Error: " + error.message);
  }
}

async function adminDeleteBook(bookId) {
  if (!confirm("Are you sure you want to delete this book?")) return;

  try {
    const res = await fetch(`${API_BASE}/books/${bookId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${currentToken}` },
    });

    if (!res.ok) throw new Error();
    showToast("Book deleted");
    loadAdminBooks();
    loadBooks();
  } catch (error) {
    alert("Error: " + error.message);
  }
}

// ========================================
// UI HELPERS
// ========================================

function updateAuthUI() {
  const loginBtn = document.getElementById("nav-auth-btn");
  const logoutBtn = document.getElementById("nav-logout-btn");
  const userName = document.getElementById("nav-user-name");
  const roleBadge = document.getElementById("nav-role-badge");
  const myBorrowsNav = document.getElementById("nav-my-borrows");
  const adminNav = document.getElementById("nav-admin");

  if (currentUser) {
    loginBtn.style.display = "none";
    logoutBtn.style.display = "block";
    userName.textContent = currentUser.full_name;
    userName.style.display = "inline";
    roleBadge.textContent = currentUser.role;
    roleBadge.style.display = "inline-block";
    myBorrowsNav.style.display = "block";

    if (canUseStaffPanel()) {
      adminNav.querySelector("a").textContent = isAdmin() ? "Admin" : "Staff";
      adminNav.style.display = "block";
    } else {
      adminNav.style.display = "none";
    }

    loadUserBorrows();
    loadUserProfile();
  } else {
    loginBtn.style.display = "block";
    logoutBtn.style.display = "none";
    userName.style.display = "none";
    roleBadge.style.display = "none";
    myBorrowsNav.style.display = "none";
    adminNav.style.display = "none";
  }
}

function openModal(type) {
  if (type === "login") {
    document.getElementById("mtab-login").classList.add("active");
    document.getElementById("mtab-signup").classList.remove("active");
    document.getElementById("modal-title").textContent = "Welcome back";
    document.getElementById("modal-sub").textContent = "Sign in to your Readly account.";
    document.getElementById("modal-submit-btn").textContent = "Sign In";
    document.querySelectorAll(".signup-only").forEach((el) => (el.style.display = "none"));
    document.getElementById("m-remember-row").style.display = "flex";
  } else {
    document.getElementById("mtab-login").classList.remove("active");
    document.getElementById("mtab-signup").classList.add("active");
    document.getElementById("modal-title").textContent = "Create Account";
    document.getElementById("modal-sub").textContent = "Join Readly to start borrowing.";
    document.getElementById("modal-submit-btn").textContent = "Create Account";
    document.querySelectorAll(".signup-only").forEach((el) => (el.style.display = "block"));
    document.getElementById("m-remember-row").style.display = "none";
  }

  document.getElementById("modal-overlay").style.display = "flex";
}

function closeModal() {
  document.getElementById("modal-overlay").style.display = "none";
  document.getElementById("modal-error").style.display = "none";
}

function switchTab(tab) {
  const tabs = document.querySelectorAll(".modal-tab");
  tabs.forEach((t) => t.classList.remove("active"));
  document.getElementById("mtab-" + tab).classList.add("active");
  openModal(tab);
}

function handleOverlayClick(e) {
  if (e.target.id === "modal-overlay") {
    closeModal();
  }
}

function clearAuthForm() {
  document.getElementById("field-name").value = "";
  document.getElementById("field-dob").value = "";
  document.getElementById("field-address").value = "";
  document.getElementById("field-phone").value = "";
  document.getElementById("field-email").value = "";
  document.getElementById("field-password").value = "";
  document.getElementById("field-confirm").value = "";
  document.getElementById("modal-error").style.display = "none";
}

function showModalError(message) {
  const errorDiv = document.getElementById("modal-error");
  errorDiv.textContent = message;
  errorDiv.style.display = "block";
}

function showModalLoading(show) {
  document.getElementById("modal-loading").style.display = show ? "flex" : "none";
  document.getElementById("modal-submit-btn").disabled = show;
}

function showToast(message) {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

function showPanel(panelName) {
  const panels = ["home", "borrows", "admin"];
  panels.forEach((p) => {
    const el = document.getElementById(`panel-${p}`);
    if (el) el.style.display = p === panelName ? "block" : "none";
  });

  document.querySelectorAll(".home-section").forEach((el) => {
    el.style.display = panelName === "home" ? "" : "none";
  });

  if (panelName === "home") {
    document.getElementById("hero-section").style.display = "grid";
  } else {
    document.getElementById("hero-section").style.display = "none";
  }

  if (panelName === "borrows" && currentUser) {
    loadUserBorrows();
  }

  if (panelName === "admin" && canUseStaffPanel()) {
    loadAdminPanel();
  }
}

function filterBorrows(filter, btn) {
  const buttons = document.querySelectorAll(".borrow-tab");
  buttons.forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  loadUserBorrows();
}

async function updateStats() {
  try {
    const booksRes = await fetch(`${API_BASE}/books`);
    const books = await booksRes.json();

    const borrowsRes = await fetch(`${API_BASE}/borrows/overdue`, {
      headers: currentToken ? { Authorization: `Bearer ${currentToken}` } : {},
    });
    const borrowCount = borrowsRes.ok ? (await borrowsRes.json()).length : 0;

    document.getElementById("stat-books").textContent = books.length;
    document.getElementById("stat-borrows").textContent = borrowCount;
  } catch (error) {
    console.error("Error updating stats:", error);
  }
}

function setupEventListeners() {
  document.getElementById("borrow-days").addEventListener("change", updateBorrowPreview);
  document.getElementById("searchBtn")?.addEventListener("click", () => {
    const query = document.getElementById("searchInput")?.value || "";
    loadBooks();
  });
}
