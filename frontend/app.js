const searchInput = document.getElementById('searchInput');
const genreSelect = document.getElementById('genreSelect');
const searchBtn = document.getElementById('searchBtn');
const booksGrid = document.getElementById('booksGrid');

async function fetchBooks() {
    const searchQuery = searchInput.value.trim().toLowerCase();
    const genre = genreSelect.value.toLowerCase();

    try {
     
        const response = await fetch('books.json');
        let books = await response.json();

     
        if (genre) {
            books = books.filter(book => book.genre.toLowerCase() === genre);
        }
        
        
        if (searchQuery) {
            books = books.filter(book => 
                book.title.toLowerCase().includes(searchQuery) || 
                book.author.toLowerCase().includes(searchQuery)
            );
        }

        
        renderBooks(books);

    } catch (error) {
        console.error("Error loading books from books.json:", error);
    }
}

function renderBooks(booksArray) {

    booksGrid.innerHTML = '';

    
    if (booksArray.length === 0) {
        booksGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; font-size: 1.2rem;">Unfortunately, nothing was found for your query.</p>';
        return;
    }

   
    booksArray.forEach(book => {
        const bookHTML = `
            <div class="book-card">
                <div class="book-cover ${book.cover_color}">
                    <span class="book-cover-title">${book.title}</span>
                </div>
                <div class="book-title">${book.title}</div>
                <div class="book-author">${book.author}</div>
                <div class="book-stars">★★★★★</div>
            </div>
        `;
       
        booksGrid.insertAdjacentHTML('beforeend', bookHTML);
    });
}


searchBtn.addEventListener('click', fetchBooks);
genreSelect.addEventListener('change', fetchBooks);


searchInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        fetchBooks();
    }
});


window.addEventListener('DOMContentLoaded', fetchBooks);