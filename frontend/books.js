/* ─────────────────────────────────────────────────────────────────────────
   books.js  —  data + dynamic rendering + genre filtering
   ───────────────────────────────────────────────────────────────────────── */

// ── 1. Data ────────────────────────────────────────────────────────────────
const booksData = [

  // FANTASY (10)
  { title: 'Тіні забутих предків',        author: 'Михайло Коцюбинський', genre: 'Fantasy',            stars: '★★★★★', img: 'https://ksd.ua/storage/products/gallery/medium_x2/952Pacgmr37BobeyPzaI0dQnnYyAF9xqZL91nXEm.jpg?v=1733324436'    },
  { title: 'Лісова пісня',                author: 'Леся Українка',        genre: 'Fantasy',            stars: '★★★★★', img: 'https://static.yakaboo.ua/media/cloudflare/product/webp/600x840/c/o/cover_858_1.jpg'    },
  { title: 'Місто',                        author: 'Валер\'ян Підмогильний',genre: 'Fantasy',           stars: '★★★★☆', img: 'https://atenabooks.com/upload/product/valeryan-pidmogilniy-misto/338.jpg'    },
  { title: 'Аргонавти',                   author: 'Михайло Коцюбинський', genre: 'Fantasy',            stars: '★★★★★', img: 'https://static.yakaboo.ua/media/cloudflare/product/webp/600x840/3/6/362807_8538589.jpg'    },
  { title: 'Захар Беркут',                author: 'Іван Франко',          genre: 'Fantasy',            stars: '★★★★★', img: 'https://static.yakaboo.ua/media/cloudflare/product/webp/600x840/1/3/1375_5.jpg'    },
  { title: 'Чорна рада',                  author: 'Пантелеймон Куліш',    genre: 'Fantasy',            stars: '★★★★☆', img: 'https://laboratory.ua/files/products/7b3ea608800543fe1eb99d0c1a541b87.480x710.jpg.webp'    },
  { title: 'Камінний хрест',              author: 'Василь Стефаник',      genre: 'Fantasy',            stars: '★★★★★', img: 'https://nashformat.ua/files/products/kaminnyj-hrest-novely-seriya-svitovyd-919194.270x390.jpeg'    },
  { title: 'Майстер корабля',             author: 'Юрій Яновський',       genre: 'Fantasy',            stars: '★★★★☆', img: 'https://static.yakaboo.ua/media/cloudflare/product/webp/600x840/i/m/img923_99.jpg'    },
  { title: 'Людина і зброя',              author: 'Олесь Гончар',         genre: 'Fantasy',            stars: '★★★★★', img: 'https://static.yakaboo.ua/media/catalog/product/c/o/cover_213_24.png'    },
  { title: 'Тигролови',                   author: 'Іван Багряний',        genre: 'Fantasy',            stars: '★★★★★', img: 'https://apriori-publishing.com/imagecdn/2397dd48-e986-4679-a5fe-e5ef4dcbff61-1080.jpg'   },

  // SCI-FI (10)
  { title: 'Зруйновані зорі',                  author: 'Олег Авраменко',       genre: 'Sci-Fi',             stars: '★★★★☆', img: 'https://static.yakaboo.ua/media/cloudflare/product/webp/600x840/i/m/img533_1_2.jpg'      },
  { title: 'Принц Галлії',              author: 'Олег Авраменко',       genre: 'Sci-Fi',             stars: '★★★★☆', img: 'https://book-ye.com.ua/media/catalog/product/cache/e6ab0fd5a5451515a63b8f521cf72c32/b/4/b4d78d94-8ee4-11e6-80c0-000c29ae1566_45b782c7-8e35-11e7-80cf-000c29ae1566.jpg'      },
  { title: 'Час смертохристів',           author: 'Марина та Сергій Дяченко', genre: 'Sci-Fi',         stars: '★★★★★', img: 'https://content2.rozetka.com.ua/goods/images/big/302544237.jpg'      },
  { title: 'Пандем',                      author: 'Марина та Сергій Дяченко', genre: 'Sci-Fi',         stars: '★★★★★', img: 'https://s1.livelib.ru/boocover/1012418324/200x305/ebfd/boocover.jpg'      },
  { title: 'Армагед-дом',                 author: 'Марина та Сергій Дяченко', genre: 'Sci-Fi',         stars: '★★★★☆', img: 'https://static.yakaboo.ua/media/catalog/product/1/_/1_11_338.jpg'      },
  { title: 'Чорний ворон',                author: 'Василь Шкляр',         genre: 'Sci-Fi',             stars: '★★★★★', img: 'https://static.yakaboo.ua/media/catalog/product/b/l/black_raven_front.jpg'      },
  { title: 'Залізна вода',                author: 'Олег Шинкаренко',      genre: 'Sci-Fi',             stars: '★★★★☆', img: 'images/scifi8.jpg'      },
  { title: 'Мавка',                       author: 'Леся Українка',        genre: 'Sci-Fi',             stars: '★★★★★', img: 'images/scifi9.jpg'      },
  { title: 'Рівне/Ровно',                 author: 'Олександр Ірванець',   genre: 'Sci-Fi',             stars: '★★★★☆', img: 'images/scifi10.jpg'     },

  // ROMANCE (10)
  { title: 'Солодка Даруся',              author: 'Марія Матіос',         genre: 'Romance',            stars: '★★★★★', img: 'images/romance1.jpg'    },
  { title: 'Нація',                       author: 'Ліна Костенко',        genre: 'Romance',            stars: '★★★★★', img: 'images/romance2.jpg'    },
  { title: 'Маруся Чурай',               author: 'Ліна Костенко',        genre: 'Romance',            stars: '★★★★★', img: 'images/romance3.jpg'    },
  { title: 'Щоденник страченої',          author: 'Марія Матіос',         genre: 'Romance',            stars: '★★★★☆', img: 'images/romance4.jpg'    },
  { title: 'Польові дослідження з українського сексу', author: 'Оксана Забужко', genre: 'Romance', stars: '★★★★★', img: 'images/romance5.jpg'    },
  { title: 'Записки українського самашедшого', author: 'Ліна Костенко',  genre: 'Romance',            stars: '★★★★★', img: 'images/romance6.jpg'    },
  { title: 'Аркан для лиходія',           author: 'Андрій Кокотюха',      genre: 'Romance',            stars: '★★★★☆', img: 'images/romance7.jpg'    },
  { title: 'Дванадцять обручів',          author: 'Юрій Андрухович',      genre: 'Romance',            stars: '★★★★★', img: 'images/romance8.jpg'    },
  { title: 'Музей покинутих секретів',    author: 'Оксана Забужко',       genre: 'Romance',            stars: '★★★★★', img: 'images/romance9.jpg'    },
  { title: 'Листи в одну сторону',        author: 'Люко Дашвар',          genre: 'Romance',            stars: '★★★★☆', img: 'images/romance10.jpg'   },

  // DETECTIVE / THRILLER (10)
  { title: 'Аркан для лиходія',           author: 'Андрій Кокотюха',      genre: 'Detective/Thriller', stars: '★★★★★', img: 'images/detective1.jpg'  },
  { title: 'Чорний ворон',                author: 'Василь Шкляр',         genre: 'Detective/Thriller', stars: '★★★★★', img: 'images/detective2.jpg'  },
  { title: 'Залізний хрест',              author: 'Андрій Кокотюха',      genre: 'Detective/Thriller', stars: '★★★★☆', img: 'images/detective3.jpg'  },
  { title: 'Агент лилик',                 author: 'Юрій Винничук',        genre: 'Detective/Thriller', stars: '★★★★★', img: 'images/detective4.jpg'  },
  { title: 'Хімія смерті',                author: 'Саймон Бекетт',        genre: 'Detective/Thriller', stars: '★★★★☆', img: 'images/detective5.jpg'  },
  { title: 'Темна вода',                  author: 'Андрій Кокотюха',      genre: 'Detective/Thriller', stars: '★★★★☆', img: 'images/detective6.jpg'  },
  { title: 'Де немає Бога',               author: 'Андрій Кокотюха',      genre: 'Detective/Thriller', stars: '★★★★★', img: 'images/detective7.jpg'  },
  { title: 'Смерть у столиці',            author: 'Андрій Кокотюха',      genre: 'Detective/Thriller', stars: '★★★★☆', img: 'images/detective8.jpg'  },
  { title: 'Слід рудої кішки',            author: 'Андрій Кокотюха',      genre: 'Detective/Thriller', stars: '★★★★★', img: 'images/detective9.jpg'  },
  { title: 'Необачність',                 author: 'Андрій Кокотюха',      genre: 'Detective/Thriller', stars: '★★★★☆', img: 'images/detective10.jpg' },

  // FICTION (10)
  { title: 'Місто',                        author: 'Валер\'ян Підмогильний',genre: 'Fiction',           stars: '★★★★★', img: 'images/fiction1.jpg'    },
  { title: 'Тигролови',                   author: 'Іван Багряний',        genre: 'Fiction',            stars: '★★★★★', img: 'images/fiction2.jpg'    },
  { title: 'Собор',                       author: 'Олесь Гончар',         genre: 'Fiction',            stars: '★★★★★', img: 'images/fiction3.jpg'    },
  { title: 'Перехресні стежки',           author: 'Іван Франко',          genre: 'Fiction',            stars: '★★★★★', img: 'images/fiction4.jpg'    },
  { title: 'Ворошиловград',               author: 'Сергій Жадан',         genre: 'Fiction',            stars: '★★★★★', img: 'images/fiction5.jpg'    },
  { title: 'Інтернат',                    author: 'Сергій Жадан',         genre: 'Fiction',            stars: '★★★★★', img: 'images/fiction6.jpg'    },
  { title: 'Депеш Мод',                   author: 'Сергій Жадан',         genre: 'Fiction',            stars: '★★★★☆', img: 'images/fiction7.jpg'    },
  { title: 'Рекреації',                   author: 'Юрій Андрухович',      genre: 'Fiction',            stars: '★★★★☆', img: 'images/fiction8.jpg'    },
  { title: 'Московіада',                  author: 'Юрій Андрухович',      genre: 'Fiction',            stars: '★★★★★', img: 'images/fiction9.jpg'    },
  { title: 'Перверзія',                   author: 'Юрій Андрухович',      genre: 'Fiction',            stars: '★★★★☆', img: 'images/fiction10.jpg'   },

  // NON-FICTION (10)
  { title: 'Ukraїna: a Trauma',           author: 'Тарас Прохасько',      genre: 'Non-fiction',        stars: '★★★★☆', img: 'images/nonfiction1.jpg' },
  { title: 'Нотатки з Голодомору',        author: 'Гарет Джонс',          genre: 'Non-fiction',        stars: '★★★★★', img: 'images/nonfiction2.jpg' },
  { title: 'Жовтий князь',                author: 'Василь Барка',         genre: 'Non-fiction',        stars: '★★★★★', img: 'images/nonfiction3.jpg' },
  { title: 'Чорна дошка',                 author: 'Андрій Мусієнко',      genre: 'Non-fiction',        stars: '★★★★☆', img: 'images/nonfiction4.jpg' },
  { title: 'Країна мрій',                 author: 'Андрій Курков',        genre: 'Non-fiction',        stars: '★★★★★', img: 'images/nonfiction5.jpg' },
  { title: 'Лексикон інтимних міст',      author: 'Юрій Андрухович',      genre: 'Non-fiction',        stars: '★★★★★', img: 'images/nonfiction6.jpg' },
  { title: 'Мій дядько найчесніших правил',author: 'Марія Матіос',        genre: 'Non-fiction',        stars: '★★★★☆', img: 'images/nonfiction7.jpg' },
  { title: 'Чотири пори року',            author: 'Тарас Прохасько',      genre: 'Non-fiction',        stars: '★★★★☆', img: 'images/nonfiction8.jpg' },
  { title: 'Схід і Захід',                author: 'Микола Рябчук',        genre: 'Non-fiction',        stars: '★★★★★', img: 'images/nonfiction9.jpg' },
  { title: 'Хто такі українці',           author: 'Микола Рябчук',        genre: 'Non-fiction',        stars: '★★★★☆', img: 'images/nonfiction10.jpg'},

  // CHILDREN'S BOOKS (10)
  { title: 'Пригоди Незнайки',            author: 'Микола Носов',         genre: "Children's books",   stars: '★★★★★', img: 'images/children1.jpg'   },
  { title: 'Королівство кривих дзеркал',  author: 'Віталій Губарєв',      genre: "Children's books",   stars: '★★★★★', img: 'images/children2.jpg'   },
  { title: 'Чарівний ліхтарик',           author: 'Всеволод Нестайко',    genre: "Children's books",   stars: '★★★★★', img: 'images/children3.jpg'   },
  { title: 'Тореадори з Васюківки',       author: 'Всеволод Нестайко',    genre: "Children's books",   stars: '★★★★★', img: 'images/children4.jpg'   },
  { title: 'Пригоди Барвінка',            author: 'Богдан Чалий',         genre: "Children's books",   stars: '★★★★☆', img: 'images/children5.jpg'   },
  { title: 'Маруся і таємний рецепт',     author: 'Зірка Мензатюк',       genre: "Children's books",   stars: '★★★★★', img: 'images/children6.jpg'   },
  { title: 'Київські казки',              author: 'Зірка Мензатюк',       genre: "Children's books",   stars: '★★★★★', img: 'images/children7.jpg'   },
  { title: 'Бешкетники з 6-Б',            author: 'Всеволод Нестайко',    genre: "Children's books",   stars: '★★★★☆', img: 'images/children8.jpg'   },
  { title: 'Привіт, я Бі',               author: 'Галина Вдовиченко',    genre: "Children's books",   stars: '★★★★★', img: 'images/children9.jpg'   },
  { title: 'Пеппі Довгапанчоха',          author: 'Астрід Ліндгрен',      genre: "Children's books",   stars: '★★★★★', img: 'images/children10.jpg'  },

  // HISTORY (10)
  { title: 'Україна: коротка історія',    author: 'Орест Субтельний',     genre: 'History',            stars: '★★★★★', img: 'images/history1.jpg'    },
  { title: 'Нарис історії України',       author: 'Микола Аркас',         genre: 'History',            stars: '★★★★★', img: 'images/history2.jpg'    },
  { title: 'Від Малоросії до України',    author: 'Микола Рябчук',        genre: 'History',            stars: '★★★★☆', img: 'images/history3.jpg'    },
  { title: 'Голокост в Україні',          author: 'Карел Беркхоф',        genre: 'History',            stars: '★★★★★', img: 'images/history4.jpg'    },
  { title: 'Тисячолітній Миколай',        author: 'Василь Шкляр',         genre: 'History',            stars: '★★★★★', img: 'images/history5.jpg'    },
  { title: 'Хрещатий яр',                author: 'Докія Гуменна',        genre: 'History',            stars: '★★★★★', img: 'images/history6.jpg'    },
  { title: 'Слово про Ігорів похід',      author: 'Невідомий автор',      genre: 'History',            stars: '★★★★★', img: 'images/history7.jpg'    },
  { title: 'Мазепа',                      author: 'Борис Крупницький',     genre: 'History',            stars: '★★★★☆', img: 'images/history8.jpg'    },
  { title: 'Іван Мазепа',                 author: 'Тетяна Таїрова-Яковлєва', genre: 'History',         stars: '★★★★★', img: 'images/history9.jpg'    },
  { title: 'Данило Галицький',            author: 'Роман Федорів',        genre: 'History',            stars: '★★★★☆', img: 'images/history10.jpg'   },
];

// ── 2. Render ──────────────────────────────────────────────────────────────
/**
 * Clears #books-grid and populates it with cards matching `filter`.
 * @param {string} filter  Genre string, or 'All' to show everything.
 */
function renderBooks(filter) {
  const grid = document.getElementById('books-grid');

  const filtered = filter === 'All'
    ? booksData
    : booksData.filter(b => b.genre === filter);

  // Build all cards in one innerHTML write — avoids repeated reflows
  grid.innerHTML = filtered.map((book, index) => `
    <div class="book-card fade-in" style="--i:${index}">
      <div class="book-cover">
        <img
          src="${book.img}"
          alt="${book.title}"
          class="book-img"
          loading="lazy"
          onerror="this.style.display='none'"
        />
      </div>
      <div class="book-title">${book.title}</div>
      <span class="book-author">${book.author}</span>
      <div class="book-stars">${book.stars}</div>
    </div>
  `).join('');
}

// ── 3. Filter event listeners ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

  // Render all books on first load
  renderBooks('All');

  // ── Filter bar inside #books section ──────────────────────────────────
  const filterBar = document.getElementById('genre-filter');
  filterBar.addEventListener('click', e => {
    const pill = e.target.closest('[data-genre]');
    if (!pill) return;

    // Update active state
    filterBar.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');

    renderBooks(pill.dataset.genre);
  });

  // ── Category section pills also trigger the book filter ───────────────
  const catsGrid = document.querySelector('.categories-section .cats-grid');
  if (catsGrid) {
    catsGrid.addEventListener('click', e => {
      const pill = e.target.closest('[data-genre]');
      if (!pill) return;

      // Sync the active pill in the filter bar
      filterBar.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
      const match = filterBar.querySelector(`[data-genre="${pill.dataset.genre}"]`);
      if (match) match.classList.add('active');

      renderBooks(pill.dataset.genre);

      // Scroll smoothly to the books section
      document.getElementById('books').scrollIntoView({ behavior: 'smooth' });
    });
  }
});