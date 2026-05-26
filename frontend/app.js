
const searchInput = document.getElementById('searchInput');
const genreSelect = document.getElementById('genreSelect');
const searchBtn = document.getElementById('searchBtn');
const booksGrid = document.getElementById('booksGrid');

const translations = {
    en: {
        logo: "Readly",
        nav_browse: "Browse",
        hero_title: "Your Literary World"
    },
    uk: {
        logo: "Readly (укр)",
        nav_browse: "Каталог",
        hero_title: "Ваш літературний світ"
    }
};

function applyLanguage(lang) {
    localStorage.setItem('lang', lang);
    
    // Знаходимо всі елементи, що мають атрибут data-i18n
    const elements = document.querySelectorAll('[data-i18n]');
    
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            el.textContent = translations[lang][key];
        }
    });
}

// Застосовуємо при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('lang') || 'en';
    applyLanguage(savedLang);
});

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

function renderBooks(booksArray) {
    // Спочатку повністю очищаємо сітку від старих книг
    booksGrid.innerHTML = '';

    // Якщо книг немає, показуємо повідомлення
    if (booksArray.length === 0) {
        booksGrid.innerHTML = '<p>На жаль, за вашим запитом нічого не знайдено.</p>';
        return;
    }

    // Проходимось по масиву книг і для кожної генеруємо HTML-картку
    booksArray.forEach(book => {
        const bookHTML = `
            <div class="book-card">
                <div class="book-cover ${book.coverClass}">
                    <span class="book-cover-title">${book.title}</span>
                </div>
                <div class="book-title">${book.title}</div>
                <div class="book-author">${book.author}</div>
                <div class="book-stars">${book.stars}</div>
            </div>
        `;
        // Вставляємо згенерований код в наш контейнер
        booksGrid.insertAdjacentHTML('beforeend', bookHTML);
    });
}

// 4. Вказуємо, коли саме потрібно запускати пошук
searchBtn.addEventListener('click', fetchBooks);
genreSelect.addEventListener('change', fetchBooks); // Оновлюємо щоразу, коли змінюється жанр