/**
 * Readly Library Management System - Frontend
 * Complete API integration for all user roles
 */

const isLocalFrontend = ["localhost", "127.0.0.1"].includes(window.location.hostname);
const API_BASE = isLocalFrontend
  ? `${window.location.protocol}//${window.location.hostname}:8000/api`
  : `${window.location.origin}/api`;
let currentUser = null;
let currentToken = null;
let refreshToken = null;
let editingBookId = null;
let allBooks = [];
let currentGenreFilter = "";
let currentSearchQuery = "";
let currentBorrowFilter = "active";

const ROLE_LABELS = {
  "Administrator": "Адміністратор",
  "Advanced user": "Розширений користувач",
  "User": "Користувач",
};

const BOOK_TYPE_LABELS = {
  fantasy: "Фентезі",
  criminal: "Кримінальна",
  drama: "Драма",
};

const COVER_COLORS = [
  "#245c73",
  "#3f7f5f",
  "#8f5f4a",
  "#5a6170",
  "#7a4f69",
  "#6e7345",
  "#4f6f8f",
  "#8b5e3c",
];

function isAdmin() {
  return currentUser?.role === "Administrator";
}

function canUseStaffPanel() {
  return currentUser?.role === "Administrator" || currentUser?.role === "Advanced user";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function escapeJsAttr(value) {
  return escapeHtml(String(value ?? "").replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/\r?\n/g, " "));
}

function formatApiError(data, fallback) {
  if (!data) return fallback;
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  }
  return fallback;
}

function roleLabel(role) {
  return ROLE_LABELS[role] || role;
}

function bookTypeLabel(type) {
  return BOOK_TYPE_LABELS[type] || type;
}

function formatDate(value) {
  return new Date(value).toLocaleDateString("uk-UA");
}

function looksLikeEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value || "").trim());
}

function coverColor(book, index) {
  const seed = String(book.id || book.title || index)
    .split("")
    .reduce((sum, char) => sum + char.charCodeAt(0), index);
  return COVER_COLORS[seed % COVER_COLORS.length];
}

async function ensureBooksLoaded() {
  if (allBooks.length > 0) return;

  const res = await fetch(`${API_BASE}/books`, {
    headers: currentToken ? { Authorization: `Bearer ${currentToken}` } : {},
  });

  if (!res.ok) throw new Error("Не вдалося завантажити каталог книг");
  allBooks = await res.json();
}

function findBookById(bookId) {
  return allBooks.find((book) => book.id === bookId);
}

// ========================================
// INITIALIZATION & LIFECYCLE
// ========================================

document.addEventListener("DOMContentLoaded", () => {
  loadUserSession();
  loadBooks();
  updateStats();
  setupEventListeners();
});

function loadUserSession() {
  const session = localStorage.getItem("readlySession");
  if (session) {
    try {
      const parsed = JSON.parse(session);
      currentUser = parsed.user;
      currentToken = parsed.access_token;
      refreshToken = parsed.refresh_token;
      updateAuthUI();
      if (canUseStaffPanel()) {
        loadAdminPanel();
      }
    } catch (e) {
      console.error("Failed to load session:", e);
      localStorage.removeItem("readlySession");
    }
  }
}

function saveUserSession(user, accessToken, refToken) {
  currentUser = user;
  currentToken = accessToken;
  refreshToken = refToken;
  localStorage.setItem(
    "readlySession",
    JSON.stringify({ user, access_token: accessToken, refresh_token: refToken })
  );
  updateAuthUI();
}

function logout() {
  currentUser = null;
  currentToken = null;
  refreshToken = null;
  localStorage.removeItem("readlySession");
  closeModal();
  showPanel("home");
  updateAuthUI();
  loadBooks();
  showToast("Ви вийшли з акаунта");
}

async function refreshAccessToken() {
  if (!refreshToken) return false;

  const res = await fetch(`${API_BASE}/auth/refresh?refresh_token=${encodeURIComponent(refreshToken)}`, {
    method: "POST",
  });

  if (!res.ok) return false;

  const tokens = await res.json();
  currentToken = tokens.access_token;
  refreshToken = tokens.refresh_token;
  localStorage.setItem(
    "readlySession",
    JSON.stringify({ user: currentUser, access_token: currentToken, refresh_token: refreshToken })
  );
  return true;
}

async function fetchWithAuth(url, options = {}, retry = true) {
  if (!currentToken) {
    throw new Error("Увійдіть у систему ще раз");
  }

  const headers = {
    ...(options.headers || {}),
    Authorization: `Bearer ${currentToken}`,
  };

  const response = await fetch(url, { ...options, headers });
  if (response.status !== 401 || !retry) {
    return response;
  }

  const refreshed = await refreshAccessToken();
  if (!refreshed) {
    currentUser = null;
    currentToken = null;
    refreshToken = null;
    localStorage.removeItem("readlySession");
    updateAuthUI();
    throw new Error("Сесію завершено. Увійдіть знову.");
  }

  return fetchWithAuth(url, options, false);
}

// ========================================
// AUTH - REGISTER & LOGIN
// ========================================

function handleAuthSubmit() {
  const isSignup = document.getElementById("mtab-signup").classList.contains("active");

  if (isSignup) {
    registerUser();
  } else {
    loginUser();
  }
}

async function registerUser() {
  const name = document.getElementById("field-name").value.trim();
  const dob = document.getElementById("field-dob").value;
  const address = document.getElementById("field-address").value.trim();
  const phone = document.getElementById("field-phone").value.trim();
  const email = document.getElementById("field-email").value.trim();
  const password = document.getElementById("field-password").value;
  const confirm = document.getElementById("field-confirm").value;

  if (!name || !dob || !address || !phone || !email || !password || !confirm) {
    showModalError("Заповніть усі поля");
    return;
  }

  if (password !== confirm) {
    showModalError("Паролі не збігаються");
    return;
  }

  if (password.length < 8) {
    showModalError("Пароль має містити щонайменше 8 символів");
    return;
  }

  if (!/[A-Z]/.test(password)) {
    showModalError("Пароль має містити велику літеру");
    return;
  }

  if (!/[0-9]/.test(password)) {
    showModalError("Пароль має містити цифру");
    return;
  }

  showModalLoading(true);

  try {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: name,
        date_of_birth: dob,
        address: address,
        phone: phone,
        email: email,
        password: password,
      }),
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(formatApiError(data, "Не вдалося зареєструватися"));
    }

    showToast("Акаунт створено. Увійдіть, щоб продовжити.");
    clearAuthForm();
    switchTab("login");
  } catch (error) {
    showModalError(error.message);
  } finally {
    showModalLoading(false);
  }
}

async function signInWithCredentials(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username: email, password }),
  });

  if (!res.ok) {
    const data = await res.json();
    throw new Error(formatApiError(data, "Не вдалося увійти"));
  }

  return finishLogin(await res.json());
}

async function finishLogin(tokens) {
  currentToken = tokens.access_token;
  refreshToken = tokens.refresh_token;
  const userRes = await fetchWithAuth(`${API_BASE}/users/me`);
  if (!userRes.ok) throw new Error("Не вдалося завантажити профіль");
  const user = await userRes.json();

  saveUserSession(user, tokens.access_token, tokens.refresh_token);
  return user;
}

async function loginUser() {
  const email = document.getElementById("field-email").value.trim();
  const password = document.getElementById("field-password").value;

  if (!email || !password) {
    showModalError("Вкажіть email і пароль");
    return;
  }

  showModalLoading(true);

  try {
    const user = await signInWithCredentials(email, password);
    closeModal();
    clearAuthForm();
    showToast(`Вітаємо, ${user.full_name}!`);
    loadBooks();

    if (canUseStaffPanel()) {
      loadAdminPanel();
    }
  } catch (error) {
    showModalError(error.message);
  } finally {
    showModalLoading(false);
  }
}

// ========================================
// BOOKS - LIST, FILTER, BORROW
// ========================================

async function loadBooks(genre = "") {
  currentGenreFilter = genre;
  try {
    const res = await fetch(`${API_BASE}/books`, {
      headers: currentToken ? { Authorization: `Bearer ${currentToken}` } : {},
    });

    if (!res.ok) throw new Error("Не вдалося завантажити книги");

    allBooks = await res.json();

    renderBooksGrid(getFilteredBooks());
    updateStats();
  } catch (error) {
    console.error("Error loading books:", error);
    document.getElementById("books-grid").innerHTML =
      '<p style="grid-column: 1/-1;">Не вдалося завантажити книги. Спробуйте ще раз.</p>';
  }
}

function getFilteredBooks() {
  const query = currentSearchQuery.trim().toLowerCase();
  return allBooks.filter((book) => {
    const matchesGenre = currentGenreFilter ? book.book_type === currentGenreFilter : true;
    const searchable = [
      book.title,
      book.author,
      book.book_type,
      bookTypeLabel(book.book_type),
    ].join(" ").toLowerCase();
    const matchesSearch = query ? searchable.includes(query) : true;
    return matchesGenre && matchesSearch;
  });
}

function renderBooksGrid(books) {
  const grid = document.getElementById("books-grid");
  grid.innerHTML = "";

  if (books.length === 0) {
    grid.innerHTML = '<p style="grid-column: 1/-1;">Книг за цим запитом не знайдено.</p>';
    return;
  }

  books.forEach((book, index) => {
    const card = document.createElement("div");
    card.className = "book-card";
    card.innerHTML = `
      <div class="book-cover" style="background: ${coverColor(book, index)};">
        <div class="book-cover-title">${escapeHtml(book.title)}</div>
      </div>
      <div class="book-title">${escapeHtml(book.title)}</div>
      <div class="book-author">${escapeHtml(book.author)}</div>
      <div class="book-meta">
        <span>${escapeHtml(bookTypeLabel(book.book_type))}</span>
        <span>${escapeHtml(book.available_qty)}/${escapeHtml(book.total_qty)} доступно</span>
      </div>
      ${
        currentUser && book.available_qty > 0
          ? `<button class="btn-primary" onclick="openBorrowModal('${escapeJsAttr(book.id)}', '${escapeJsAttr(book.title)}')">Взяти</button>`
          : book.available_qty === 0
            ? `<button class="btn-primary" disabled>Недоступно</button>`
            : `<button class="btn-primary" onclick="openModal('login')">Увійдіть, щоб взяти</button>`
      }
    `;
    grid.appendChild(card);
  });
}

function filterByGenre(genre, btn) {
  currentGenreFilter = genre;
  const buttons = document.querySelectorAll(".genre-btn");
  buttons.forEach((button) => button.classList.remove("active"));
  if (btn) btn.classList.add("active");
  renderBooksGrid(getFilteredBooks());
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
  document.getElementById("borrow-modal-title").textContent = `Взяти "${bookTitle}"`;
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
  document.getElementById("borrow-due-preview").textContent = `Повернути до ${formatDate(due)}`;
}

async function submitBorrow() {
  const qty = parseInt(document.getElementById("borrow-qty").value);
  const days = parseInt(document.getElementById("borrow-days").value);

  if (qty < 1 || days < 1) {
    alert("Вкажіть коректну кількість і термін користування");
    return;
  }

  try {
    const res = await fetchWithAuth(`${API_BASE}/borrows`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        book_id: currentBorrowBook,
        quantity: qty,
        days: days,
      }),
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(formatApiError(data, "Не вдалося взяти книгу"));
    }

    showToast("Книгу успішно додано до ваших записів");
    closeBorrowModal();
    loadBooks();
    loadUserBorrows();
  } catch (error) {
    alert("Помилка: " + error.message);
  }
}

async function loadUserBorrows() {
  if (!currentUser) return;

  try {
    await ensureBooksLoaded();

    const res = await fetchWithAuth(`${API_BASE}/borrows/me`);

    if (!res.ok) throw new Error("Не вдалося завантажити список книг");

    const borrows = await res.json();
    renderBorrowsList(filterBorrowRecords(borrows));
  } catch (error) {
    console.error("Error loading borrows:", error);
  }
}

function filterBorrowRecords(borrows) {
  if (currentBorrowFilter === "returned") {
    return borrows.filter((borrow) => borrow.returned);
  }

  if (currentBorrowFilter === "active") {
    return borrows.filter((borrow) => !borrow.returned);
  }

  return borrows;
}

function renderBorrowsList(borrows) {
  const list = document.getElementById("borrows-list");
  list.innerHTML = "";

  if (borrows.length === 0) {
    const emptyMessage = currentBorrowFilter === "returned"
      ? "У вас ще немає повернених книг."
      : currentBorrowFilter === "active"
        ? "У вас немає активних книг."
        : "Ви ще не брали книги.";
    list.innerHTML = `<p>${emptyMessage}</p>`;
    return;
  }

  borrows.forEach((borrow) => {
    const book = findBookById(borrow.book_id);
    const bookTitle = book?.title || `Книга ${borrow.book_id.slice(0, 8)}`;
    const bookAuthor = book?.author || "Дані книги недоступні";
    const bookIdMeta = book ? "" : `<div class="borrow-id">ID книги: ${escapeHtml(borrow.book_id)}</div>`;
    const isOverdue = new Date() > new Date(borrow.due_date);
    const item = document.createElement("div");
    item.className = `borrow-item ${borrow.returned ? "returned" : ""} ${isOverdue ? "overdue" : ""}`;
    item.innerHTML = `
      <div class="borrow-info">
        <div class="borrow-title">${escapeHtml(bookTitle)}</div>
        <div class="book-author">${escapeHtml(bookAuthor)}</div>
        <div class="borrow-book-meta">
          ${escapeHtml(bookTypeLabel(borrow.book_type))} |
          Термін: ${escapeHtml(borrow.days)} дн. |
          Кількість: ${escapeHtml(borrow.quantity)}
        </div>
        <div class="borrow-dates">
          Взято: ${formatDate(borrow.date_taken)} |
          Повернути до: ${formatDate(borrow.due_date)}
          ${isOverdue ? " <span style='color: red;'>(прострочено)</span>" : ""}
        </div>
        ${bookIdMeta}
      </div>
      ${
        !borrow.returned
          ? `<button class="btn-small" onclick="submitReturnBook('${borrow.id}')">Повернути</button>`
          : `<span class="badge-returned">Повернено</span>`
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

    if (!res.ok) throw new Error("Не вдалося повернути книгу");

    showToast("Книгу повернено");
    loadUserBorrows();
    loadBooks();
  } catch (error) {
    alert("Помилка: " + error.message);
  }
}

// ========================================
// USER PROFILE
// ========================================

async function loadUserProfile() {
  if (!currentUser) return;

  const profileHtml = `
    <p><strong>ПІБ:</strong> ${escapeHtml(currentUser.full_name)}</p>
    <p><strong>Email:</strong> ${escapeHtml(currentUser.email)}</p>
    <p><strong>Телефон:</strong> ${escapeHtml(currentUser.phone)}</p>
    <p><strong>Адреса:</strong> ${escapeHtml(currentUser.address)}</p>
    <p><strong>Дата народження:</strong> ${escapeHtml(currentUser.date_of_birth)}</p>
    <p><strong>Роль:</strong> <span class="role-badge">${escapeHtml(roleLabel(currentUser.role))}</span></p>
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
    email: document.getElementById("edit-email").value,
    phone: document.getElementById("edit-phone").value,
    address: document.getElementById("edit-address").value,
    date_of_birth: document.getElementById("edit-dob").value,
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

    if (!res.ok) throw new Error("Не вдалося оновити профіль");

    const updated = await res.json();
    saveUserSession(updated, currentToken, refreshToken);
    closeEditProfile();
    loadUserProfile();
    showToast("Профіль оновлено");
  } catch (error) {
    alert("Помилка: " + error.message);
  }
}

function confirmDeleteAccount() {
  if (confirm("Ви точно хочете видалити акаунт? Цю дію неможливо скасувати.")) {
    deleteAccount();
  }
}

async function deleteAccount() {
  try {
    const res = await fetch(`${API_BASE}/users/me`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${currentToken}` },
    });

    if (!res.ok) throw new Error("Не вдалося видалити акаунт");

    showToast("Ваш акаунт видалено.");
    logout();
  } catch (error) {
    alert("Помилка: " + error.message);
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
        ? `<button class="btn-danger-sm" onclick="adminDeleteUser('${escapeJsAttr(user.id)}')">Видалити</button>`
        : "";
      item.innerHTML = `
        <div>
          <strong>ID користувача: ${escapeHtml(user.id)}</strong><br/>
          <small>Персональні дані приховано політикою доступу</small><br/>
          <span class="role-badge">${escapeHtml(roleLabel(user.role))}</span>
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
        ? `<button class="btn-small" onclick="openEditBookModal('${escapeJsAttr(book.id)}')">Редагувати</button>`
        : "";
      const deleteButton = isAdmin()
        ? `<button class="btn-danger-sm" onclick="adminDeleteBook('${escapeJsAttr(book.id)}')">Видалити</button>`
        : "";
      item.innerHTML = `
        <div>
          <strong>${escapeHtml(book.title)}</strong>, ${escapeHtml(book.author)}<br/>
          <small>${escapeHtml(bookTypeLabel(book.book_type))} | ${escapeHtml(book.available_qty)}/${escapeHtml(book.total_qty)}</small>
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
      list.innerHTML = "<p>Немає прострочених книг</p>";
      return;
    }
    borrows.forEach((borrow) => {
      const item = document.createElement("div");
      item.className = "admin-list-item overdue";
      item.innerHTML = `
        <div>
          <strong>${escapeHtml(bookTypeLabel(borrow.book_type))} / ${escapeHtml(borrow.book_id)}</strong><br/>
          <small>Користувач: ${escapeHtml(borrow.user_id)}</small><br/>
          <small>Повернути до: ${formatDate(borrow.due_date)}</small>
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
  document.getElementById("add-book-modal-title").textContent = "Додати книгу";
  document.getElementById("book-submit-btn").textContent = "Додати книгу";
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
    showToast("Редагувати книги може тільки адміністратор");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/books/${bookId}`, {
      headers: { Authorization: `Bearer ${currentToken}` },
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(formatApiError(data, "Не вдалося завантажити книгу"));
    }

    const book = await res.json();
    editingBookId = book.id;
    document.getElementById("add-book-error").style.display = "none";
    document.getElementById("add-book-modal-title").textContent = "Редагувати книгу";
    document.getElementById("book-submit-btn").textContent = "Зберегти зміни";
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
    showToast("Створювати користувачів може тільки адміністратор");
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
    showCreateUserError("Заповніть усі поля");
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
      throw new Error(formatApiError(data, "Не вдалося створити користувача"));
    }

    showToast("Користувача створено");
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
    showAddBookError("Заповніть усі поля та вкажіть коректну кількість");
    return;
  }

  if (available > total) {
    showAddBookError("Доступна кількість не може бути більшою за загальну");
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
      throw new Error(formatApiError(data, isEditing ? "Не вдалося оновити книгу" : "Не вдалося додати книгу"));
    }

    showToast(isEditing ? "Книгу оновлено" : "Книгу додано");
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
    showToast("Нагадування може надсилати тільки персонал");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/admin/notify/overdue?use_sms=${useSms}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${currentToken}` },
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(formatApiError(data, "Не вдалося надіслати нагадування"));
    }

    const data = await res.json();
    showToast(`Опрацьовано прострочених записів: ${data.notified}`);
    loadAdminOverdue();
    updateStats();
  } catch (error) {
    showToast(error.message);
  }
}

async function adminDeleteUser(userId) {
  if (!confirm("Ви точно хочете видалити цього користувача?")) return;

  try {
    const res = await fetch(`${API_BASE}/admin/users/${userId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${currentToken}` },
    });

    if (!res.ok) throw new Error("Не вдалося видалити користувача");
    showToast("Користувача видалено");
    loadAdminUsers();
  } catch (error) {
    alert("Помилка: " + error.message);
  }
}

async function adminDeleteBook(bookId) {
  if (!confirm("Ви точно хочете видалити цю книгу?")) return;

  try {
    const res = await fetch(`${API_BASE}/books/${bookId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${currentToken}` },
    });

    if (!res.ok) throw new Error("Не вдалося видалити книгу");
    showToast("Книгу видалено");
    loadAdminBooks();
    loadBooks();
  } catch (error) {
    alert("Помилка: " + error.message);
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
  const profileNav = document.getElementById("nav-profile");
  const adminNav = document.getElementById("nav-admin");
  const heroSignupBtn = document.getElementById("hero-signup-btn");

  if (currentUser) {
    loginBtn.style.display = "none";
    logoutBtn.style.display = "block";
    if (heroSignupBtn) heroSignupBtn.style.display = "none";
    userName.textContent = currentUser.full_name;
    userName.style.display = "inline";
    roleBadge.textContent = roleLabel(currentUser.role);
    roleBadge.style.display = "inline-block";
    myBorrowsNav.style.display = "block";
    if (profileNav) profileNav.style.display = "block";

    if (canUseStaffPanel()) {
      adminNav.querySelector("a").textContent = isAdmin() ? "Адмін" : "Персонал";
      adminNav.style.display = "block";
    } else {
      adminNav.style.display = "none";
    }

    loadUserBorrows();
    loadUserProfile();
  } else {
    loginBtn.style.display = "block";
    logoutBtn.style.display = "none";
    if (heroSignupBtn) heroSignupBtn.style.display = "";
    userName.style.display = "none";
    roleBadge.style.display = "none";
    myBorrowsNav.style.display = "none";
    if (profileNav) profileNav.style.display = "none";
    adminNav.style.display = "none";
  }
}

function openModal(type) {
  if (type === "login") {
    document.getElementById("mtab-login").classList.add("active");
    document.getElementById("mtab-signup").classList.remove("active");
    document.getElementById("modal-title").textContent = "Вхід";
    document.getElementById("modal-sub").textContent = "Увійдіть у свій акаунт Readly.";
    document.getElementById("modal-submit-btn").textContent = "Увійти";
    document.querySelectorAll(".signup-only").forEach((el) => (el.style.display = "none"));
    document.getElementById("m-remember-row").style.display = "flex";
  } else {
    document.getElementById("mtab-login").classList.remove("active");
    document.getElementById("mtab-signup").classList.add("active");
    document.getElementById("modal-title").textContent = "Створити акаунт";
    document.getElementById("modal-sub").textContent = "Зареєструйтеся, щоб брати книги.";
    document.getElementById("modal-submit-btn").textContent = "Створити акаунт";
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
  const panels = ["home", "borrows", "profile", "admin"];
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

  if (panelName === "profile" && currentUser) {
    loadUserProfile();
  }

  if (panelName === "admin" && canUseStaffPanel()) {
    loadAdminPanel();
  }
}

function filterBorrows(filter, btn) {
  currentBorrowFilter = filter;
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
  document.getElementById("borrow-days")?.addEventListener("change", updateBorrowPreview);
  const searchInput = document.getElementById("search-input");
  if (!searchInput) return;

  function clearSearchIfAutofilled() {
    if (!looksLikeEmail(searchInput.value)) return;
    searchInput.value = "";
    currentSearchQuery = "";
    renderBooksGrid(getFilteredBooks());
  }

  currentSearchQuery = "";
  searchInput.value = "";
  searchInput.name = `catalog_filter_${Date.now()}`;
  searchInput.setAttribute("autocomplete", "off");
  searchInput.addEventListener("pointerdown", () => searchInput.removeAttribute("readonly"), { once: true });
  searchInput.addEventListener("keydown", () => searchInput.removeAttribute("readonly"), { once: true });
  [50, 250, 800, 1600].forEach((delay) => setTimeout(clearSearchIfAutofilled, delay));
  searchInput.addEventListener("input", (event) => {
    if (looksLikeEmail(event.target.value)) {
      clearSearchIfAutofilled();
      return;
    }
    currentSearchQuery = event.target.value;
    renderBooksGrid(getFilteredBooks());
  });
}
