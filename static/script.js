let allMovies = [];
let allUsers = [];

document.addEventListener('DOMContentLoaded', function() {
    loadMoviesAndUsers();
    setupTabs();
    setupHybridSlider();
});

function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');

            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            this.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        });
    });
}

function setupHybridSlider() {
    const slider = document.getElementById('hybrid-alpha');
    const display = document.querySelector('.alpha-display');

    slider.addEventListener('input', function() {
        const alpha = parseFloat(this.value);
        const label = alpha === 1 ? 'content-heavy' : alpha === 0 ? 'collaborative-heavy' : 'balanced';
        display.innerHTML = `Alpha: <strong>${alpha.toFixed(1)}</strong> (${label})`;
    });
}

async function loadMoviesAndUsers() {
    try {
        const moviesRes = await fetch('/api/movies');
        allMovies = await moviesRes.json();

        const usersRes = await fetch('/api/users');
        allUsers = await usersRes.json();

        populateSelects();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

function populateSelects() {
    const selects = [
        { id: 'content-movie', data: allMovies, attr: 'title' },
        { id: 'hybrid-movie', data: allMovies, attr: 'title' },
        { id: 'collab-user', data: allUsers, attr: null },
        { id: 'hybrid-user', data: allUsers, attr: null }
    ];

    selects.forEach(({ id, data, attr }) => {
        const select = document.getElementById(id);
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = attr ? item[attr] : item;
            option.textContent = attr ? item[attr] : `User #${item}`;
            select.appendChild(option);
        });
    });
}

async function recommendContent() {
    const movieTitle = document.getElementById('content-movie').value;
    if (!movieTitle) {
        alert('Please select a movie');
        return;
    }

    const resultsDiv = document.getElementById('content-results');
    resultsDiv.innerHTML = '<p class="loading">Loading recommendations...</p>';

    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mode: 'content',
                title: movieTitle,
                top_n: 5
            })
        });

        const data = await response.json();
        displayResults(data.results, resultsDiv);
    } catch (error) {
        resultsDiv.innerHTML = `<p class="empty-message">Error: ${error.message}</p>`;
    }
}

async function recommendCollab() {
    const userId = parseInt(document.getElementById('collab-user').value);
    if (!userId) {
        alert('Please select a user');
        return;
    }

    const resultsDiv = document.getElementById('collab-results');
    resultsDiv.innerHTML = '<p class="loading">Loading recommendations...</p>';

    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mode: 'collaborative',
                user_id: userId,
                top_n: 5
            })
        });

        const data = await response.json();
        displayResults(data.results, resultsDiv);
    } catch (error) {
        resultsDiv.innerHTML = `<p class="empty-message">Error: ${error.message}</p>`;
    }
}

async function recommendHybrid() {
    const movieTitle = document.getElementById('hybrid-movie').value;
    const userId = parseInt(document.getElementById('hybrid-user').value) || null;
    const alpha = parseFloat(document.getElementById('hybrid-alpha').value);

    if (!movieTitle && !userId) {
        alert('Please select at least a movie or a user');
        return;
    }

    const resultsDiv = document.getElementById('hybrid-results');
    resultsDiv.innerHTML = '<p class="loading">Loading recommendations...</p>';

    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mode: 'hybrid',
                title: movieTitle || null,
                user_id: userId,
                alpha: alpha,
                top_n: 5
            })
        });

        const data = await response.json();
        displayResults(data.results, resultsDiv);
    } catch (error) {
        resultsDiv.innerHTML = `<p class="empty-message">Error: ${error.message}</p>`;
    }
}

function displayResults(results, container) {
    if (!results || results.length === 0) {
        container.innerHTML = '<p class="empty-message">No recommendations found. Try a different selection.</p>';
        return;
    }

    container.innerHTML = results.map(movie => `
        <div class="result-card">
            <h3>${movie.title}</h3>
            <p><strong>Genres:</strong> ${movie.genres}</p>
            <p><strong>Director:</strong> ${movie.director}</p>
            <p><strong>Cast:</strong> ${movie.cast}</p>
            <p><strong>Overview:</strong> ${movie.overview}</p>
            <div class="score-bar">
                <span class="score-label">Match:</span>
                <div class="bar">
                    <div class="bar-fill" style="width: ${Math.min(movie.score * 100, 100)}%"></div>
                </div>
                <span class="score-value">${(movie.score * 100).toFixed(0)}%</span>
            </div>
        </div>
    `).join('');
}
