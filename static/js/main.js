/* ==========================================================================
   НЕЙРОСТАРТ — поведение страницы
   Тут четыре небольшие штуки:
   1) полоса прогресса при прокрутке;
   2) фон шапки после скролла;
   3) фильтр карточек;
   4) появление блоков + свечение под курсором.
   ========================================================================== */

/* --------------------------------------------------------------------------
   1. ПОЛОСА ПРОГРЕССА
   -------------------------------------------------------------------------- */
const progressBar = document.querySelector("#progressBar");

function updateProgress() {
  const pageHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progress = pageHeight > 0 ? window.scrollY / pageHeight : 0;

  // scaleX быстрее, чем изменение width
  progressBar.style.transform = `scaleX(${progress})`;
}

window.addEventListener("scroll", updateProgress, { passive: true });
window.addEventListener("resize", updateProgress);
updateProgress();


/* --------------------------------------------------------------------------
   2. ШАПКА: добавляем фон, когда страница прокручена
   -------------------------------------------------------------------------- */
const header = document.querySelector("#siteHeader");

function updateHeader() {
  header.classList.toggle("is-scrolled", window.scrollY > 12);
}

window.addEventListener("scroll", updateHeader, { passive: true });
updateHeader();


/* --------------------------------------------------------------------------
   3. ФИЛЬТР КАРТОЧЕК
   У каждой карточки в HTML есть data-category="tools" и т.д.
   Кнопка фильтра передаёт нужную категорию или "all".
   -------------------------------------------------------------------------- */
const filterButtons = document.querySelectorAll(".filter");
const cards = document.querySelectorAll(".card");
const cardsGrid = document.querySelector("#cardsGrid");
const visibleCount = document.querySelector("#visibleCount");
const emptyState = document.querySelector("#emptyState");

let filterTimer;

function applyFilter(filter) {
  // Плавно приглушаем сетку, затем меняем карточки
  cardsGrid.classList.add("is-switching");
  window.clearTimeout(filterTimer);

  filterTimer = window.setTimeout(() => {
    let shown = 0;

    cards.forEach((card) => {
      const matches = filter === "all" || card.dataset.category === filter;
      card.hidden = !matches;

      if (matches) {
        shown += 1;
      }
    });

    visibleCount.textContent = shown;
    emptyState.hidden = shown !== 0;
    cardsGrid.classList.remove("is-switching");
  }, 160);
}

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    filterButtons.forEach((other) => {
      other.classList.remove("is-active");
      other.setAttribute("aria-pressed", "false");
    });

    button.classList.add("is-active");
    button.setAttribute("aria-pressed", "true");

    applyFilter(button.dataset.filter);
  });
});


/* --------------------------------------------------------------------------
   4. ПОЯВЛЕНИЕ БЛОКОВ ПРИ ПРОКРУТКЕ
   -------------------------------------------------------------------------- */
const revealItems = document.querySelectorAll(".reveal");

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        const element = entry.target;
        element.classList.add("is-visible");

        // После анимации убираем служебные классы,
        // чтобы они не мешали hover-эффектам карточек.
        element.addEventListener(
          "animationend",
          (event) => {
            if (event.animationName === "revealUp" && event.target === element) {
              element.classList.remove("reveal", "is-visible");
            }
          },
          { once: true }
        );

        observer.unobserve(element);
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );

  revealItems.forEach((item) => observer.observe(item));
} else {
  // Старый браузер: просто показываем всё без анимации
  revealItems.forEach((item) => item.classList.remove("reveal"));
}


/* --------------------------------------------------------------------------
   5. СВЕЧЕНИЕ ПОД КУРСОРОМ
   Работает только там, где есть настоящая мышь.
   -------------------------------------------------------------------------- */
const canHover = window.matchMedia("(hover: hover)").matches;

if (canHover) {
  document.querySelectorAll(".card, .featured-card").forEach((card) => {
    card.addEventListener("pointermove", (event) => {
      const rect = card.getBoundingClientRect();

      card.style.setProperty("--mx", `${event.clientX - rect.left}px`);
      card.style.setProperty("--my", `${event.clientY - rect.top}px`);
    });
  });
}
