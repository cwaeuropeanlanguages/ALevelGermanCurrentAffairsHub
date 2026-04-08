const state = {
  themes: [],
  articles: [],
  selectedTheme: 'all',
  selectedSubtopic: 'all'
};

const themeGrid = document.getElementById('themeGrid');
const subtopicChips = document.getElementById('subtopicChips');
const articlesList = document.getElementById('articlesList');
const resultsLabel = document.getElementById('resultsLabel');
const lastUpdated = document.getElementById('lastUpdated');
const dialog = document.getElementById('articleDialog');
const dialogContent = document.getElementById('dialogContent');
const randomArticleBtn = document.getElementById('randomArticleBtn');
const clearFiltersBtn = document.getElementById('clearFiltersBtn');

async function loadData() {
  const cacheBust = `?v=${Date.now()}`;
  const [topicsRes, articlesRes] = await Promise.all([
    fetch(`data/topics.json${cacheBust}`),
    fetch(`data/articles.json${cacheBust}`)
  ]);

  const topics = await topicsRes.json();
  const articleData = await articlesRes.json();

  state.themes = topics.themes;
  state.articles = Array.isArray(articleData.articles) ? articleData.articles : [];

  renderThemes();
  renderSubtopics();
  renderArticles();
  renderLastUpdated(articleData.generatedAt);
}

function renderLastUpdated(generatedAt) {
  if (!generatedAt) {
    lastUpdated.textContent = 'No live articles yet. Run the GitHub Action once after upload.';
    return;
  }

  const date = new Date(generatedAt);
  const formatted = new Intl.DateTimeFormat('en-GB', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(date);
  lastUpdated.textContent = `Last updated: ${formatted}`;
}

function renderThemes() {
  const allCard = `
    <button class="theme-card ${state.selectedTheme === 'all' ? 'is-active' : ''}" data-theme="all">
      <p class="theme-card__short">All themes</p>
      <p class="theme-card__long">Show every article currently in the hub.</p>
    </button>
  `;

  const cards = state.themes.map(theme => `
    <button class="theme-card ${state.selectedTheme === theme.id ? 'is-active' : ''}" data-theme="${theme.id}">
      <p class="theme-card__short">${theme.shortLabel}</p>
      <p class="theme-card__long">${theme.label}</p>
    </button>
  `).join('');

  themeGrid.innerHTML = allCard + cards;

  themeGrid.querySelectorAll('[data-theme]').forEach(button => {
    button.addEventListener('click', () => {
      state.selectedTheme = button.dataset.theme;
      state.selectedSubtopic = 'all';
      renderThemes();
      renderSubtopics();
      renderArticles();
    });
  });
}

function renderSubtopics() {
  let subtopics = [];

  if (state.selectedTheme === 'all') {
    state.themes.forEach(theme => {
      subtopics.push(...theme.subtopics);
    });
  } else {
    const theme = state.themes.find(item => item.id === state.selectedTheme);
    subtopics = theme ? theme.subtopics : [];
  }

  const unique = Array.from(new Map(subtopics.map(item => [item.id, item])).values());

  subtopicChips.innerHTML = [
    `<button class="chip ${state.selectedSubtopic === 'all' ? 'is-active' : ''}" data-subtopic="all">All sub-topics</button>`,
    ...unique.map(subtopic => `
      <button class="chip ${state.selectedSubtopic === subtopic.id ? 'is-active' : ''}" data-subtopic="${subtopic.id}">${subtopic.label}</button>
    `)
  ].join('');

  subtopicChips.querySelectorAll('[data-subtopic]').forEach(button => {
    button.addEventListener('click', () => {
      state.selectedSubtopic = button.dataset.subtopic;
      renderSubtopics();
      renderArticles();
    });
  });
}

function getFilteredArticles() {
  return state.articles.filter(article => {
    const themeMatch = state.selectedTheme === 'all' || article.themeId === state.selectedTheme;
    const subtopicMatch = state.selectedSubtopic === 'all' || article.subtopicId === state.selectedSubtopic;
    return themeMatch && subtopicMatch;
  });
}

function renderArticles() {
  const filtered = getFilteredArticles();
  const sorted = [...filtered].sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));

  resultsLabel.textContent = `${sorted.length} article${sorted.length === 1 ? '' : 's'} shown`;

  if (!sorted.length) {
    articlesList.innerHTML = `
      <div class="empty-state">
        <p><strong>No articles are showing yet.</strong></p>
        <p>Try a different theme, or run the update workflow once after you upload the files to GitHub.</p>
      </div>
    `;
    return;
  }

  articlesList.innerHTML = sorted.map(article => `
    <article class="article-card">
      <div class="article-card__top">
        <div>
          <div class="meta">
            <span class="meta-pill">${escapeHtml(article.source)}</span>
            <span class="meta-pill">${escapeHtml(article.country)}</span>
            <span class="meta-pill">${formatDate(article.publishedAt)}</span>
          </div>
          <h3>${escapeHtml(article.title)}</h3>
        </div>
      </div>
      <div class="tags">
        <span class="tag">${escapeHtml(article.themeShortLabel)}</span>
        <span class="tag">${escapeHtml(article.subtopicLabel)}</span>
      </div>
      <p>${escapeHtml(article.summary)}</p>
      <div class="article-card__actions">
        <button class="button button--ghost button--small" data-open-dialog="${article.id}">View support</button>
        <a class="button button--primary button--small" href="${article.url}" target="_blank" rel="noopener noreferrer">Open article</a>
      </div>
    </article>
  `).join('');

  articlesList.querySelectorAll('[data-open-dialog]').forEach(button => {
    button.addEventListener('click', () => {
      const article = state.articles.find(item => item.id === button.dataset.openDialog);
      if (article) {
        openDialog(article);
      }
    });
  });
}

function openDialog(article) {
  dialogContent.innerHTML = `
    <div>
      <div class="meta">
        <span class="meta-pill">${escapeHtml(article.source)}</span>
        <span class="meta-pill">${escapeHtml(article.country)}</span>
        <span class="meta-pill">${formatDate(article.publishedAt)}</span>
      </div>
      <h2>${escapeHtml(article.title)}</h2>
      <p>${escapeHtml(article.summary)}</p>
      <p><a class="button button--primary button--small" href="${article.url}" target="_blank" rel="noopener noreferrer">Open article</a></p>
    </div>

    <section class="dialog__section">
      <h4>AQA link</h4>
      <p>${escapeHtml(article.themeLabel)} → ${escapeHtml(article.subtopicLabel)}</p>
    </section>

    <section class="dialog__section">
      <h4>Key vocabulary</h4>
      <div class="tags">
        ${article.keywords.map(word => `<span class="tag">${escapeHtml(word)}</span>`).join('')}
      </div>
    </section>

    <section class="dialog__section">
      <h4>Discussion prompts</h4>
      <ul>
        ${article.discussionQuestions.map(question => `<li>${escapeHtml(question)}</li>`).join('')}
      </ul>
    </section>
  `;
  dialog.showModal();
}

function formatDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value || 'Unknown date';
  return new Intl.DateTimeFormat('en-GB', { dateStyle: 'medium' }).format(date);
}

function escapeHtml(value = '') {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

randomArticleBtn.addEventListener('click', () => {
  const pool = getFilteredArticles();
  if (!pool.length) return;
  const article = pool[Math.floor(Math.random() * pool.length)];
  openDialog(article);
});

clearFiltersBtn.addEventListener('click', () => {
  state.selectedTheme = 'all';
  state.selectedSubtopic = 'all';
  renderThemes();
  renderSubtopics();
  renderArticles();
});

loadData().catch(error => {
  console.error(error);
  lastUpdated.textContent = 'Something went wrong while loading the tool.';
  articlesList.innerHTML = `
    <div class="empty-state">
      <p><strong>The page could not load the data files.</strong></p>
      <p>Check that <code>data/topics.json</code> and <code>data/articles.json</code> are in the correct folders.</p>
    </div>
  `;
});
