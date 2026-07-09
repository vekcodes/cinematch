let allMovies = [];
let userRatings = {};

document.addEventListener('DOMContentLoaded', async () => {
    await loadMovies();
    setupEventListeners();
});

async function loadMovies() {
    try {
        const response = await fetch('/api/movies');
        allMovies = await response.json();
        displayAllMovies();
    } catch (error) {
        console.error('Error loading movies:', error);
    }
}

function displayAllMovies() {
    const grid = document.getElementById('allMoviesGrid');
    if (allMovies.length === 0) {
        grid.innerHTML = '<p class="empty-msg">No movies yet. Add one to get started!</p>';
        return;
    }

    grid.innerHTML = allMovies.map(movie => `
        <div class="movie-card" onclick="showMovieDetail(${movie.id})">
            <div class="movie-poster-container">
                <img src="${movie.poster_url || 'https://via.placeholder.com/200x300?text=No+Image'}"
                     alt="${movie.title}" class="movie-poster">
                ${movie.rating_avg > 0 ? `<div class="rating-badge">${movie.rating_avg.toFixed(1)}</div>` : ''}
            </div>
            <div class="movie-info">
                <h3>${movie.title}</h3>
                <p class="genres">${movie.genres || 'N/A'}</p>
                <div class="stars">${'⭐'.repeat(Math.round(movie.rating_avg / 5 * 5) || 0)}</div>
            </div>
        </div>
    `).join('');
}

function setupEventListeners() {
    document.getElementById('searchQuery')?.addEventListener('keyup', debounce(searchTMDB, 300));
    document.getElementById('alpha')?.addEventListener('input', updateAlphaDisplay);
}

function debounce(func, delay) {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}

async function searchTMDB() {
    const query = document.getElementById('searchQuery').value;
    if (!query || query.length < 2) {
        document.getElementById('searchResults').innerHTML = '';
        return;
    }

    try {
        const response = await fetch('/api/tmdb/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        const results = await response.json();
        displaySearchResults(results);
    } catch (error) {
        console.error('Error searching TMDB:', error);
    }
}

function displaySearchResults(results) {
    const container = document.getElementById('searchResults');
    if (!results.length) {
        container.innerHTML = '<p style="color: #b0b0c0;">No movies found</p>';
        return;
    }

    container.innerHTML = results.map(movie => `
        <div class="search-result" onclick="selectTMDBMovie(${movie.tmdb_id})">
            <img src="${movie.poster_url}" alt="${movie.title}" onerror="this.src='https://via.placeholder.com/80x120?text=No+Image'">
            <div class="search-result-info">
                <h3>${movie.title}</h3>
                <p>${movie.release_date || 'N/A'}</p>
                <p style="font-size: 0.85em; color: #888;">${movie.overview.substring(0, 60)}...</p>
            </div>
        </div>
    `).join('');
}

async function selectTMDBMovie(tmdbId) {
    try {
        const response = await fetch(`/api/tmdb/details/${tmdbId}`);
        const details = await response.json();

        document.getElementById('manualTitle').value = details.title;
        document.getElementById('manualGenres').value = details.genres;
        document.getElementById('manualDirector').value = details.director;
        document.getElementById('manualCast').value = details.cast;
        document.getElementById('manualOverview').value = details.overview;
        document.getElementById('manualPosterUrl').value = details.poster_url;

        switchTab('manual');
    } catch (error) {
        console.error('Error fetching movie details:', error);
    }
}

async function addMovieManual() {
    const title = document.getElementById('manualTitle').value;
    const genres = document.getElementById('manualGenres').value;
    const director = document.getElementById('manualDirector').value;
    const cast = document.getElementById('manualCast').value;
    const overview = document.getElementById('manualOverview').value;
    const posterUrl = document.getElementById('manualPosterUrl').value;

    if (!title) {
        alert('Title is required');
        return;
    }

    try {
        const response = await fetch('/api/movies', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title, genres, director, cast, overview,
                poster_url: posterUrl,
                tmdb_id: null
            })
        });

        if (response.ok) {
            alert('Movie added successfully!');
            closeAddMovieModal();
            await loadMovies();
            document.getElementById('manualTitle').value = '';
            document.getElementById('manualGenres').value = '';
            document.getElementById('manualDirector').value = '';
            document.getElementById('manualCast').value = '';
            document.getElementById('manualOverview').value = '';
            document.getElementById('manualPosterUrl').value = '';
        }
    } catch (error) {
        console.error('Error adding movie:', error);
        alert('Failed to add movie');
    }
}

async function getRecommendations() {
    const mode = document.getElementById('recMode').value;
    const movieSelect = document.getElementById('recMovie');
    const alpha = document.getElementById('alpha')?.value || 0.5;

    const body = {
        mode,
        top_n: 10,
        alpha: parseFloat(alpha)
    };

    if (mode === 'content' && movieSelect.value) {
        body.movie_id = parseInt(movieSelect.value);
    }

    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await response.json();
        displayRecommendations(data.results);
    } catch (error) {
        console.error('Error getting recommendations:', error);
        document.getElementById('recResults').innerHTML = '<p style="color: #ff4444;">Error getting recommendations</p>';
    }
}

function displayRecommendations(results) {
    const container = document.getElementById('recResults');

    if (!results.length) {
        container.innerHTML = '<p style="color: #b0b0c0;">No recommendations found</p>';
        return;
    }

    container.innerHTML = results.map(movie => `
        <div class="rec-result">
            <img src="${movie.poster_url || 'https://via.placeholder.com/80x120?text=No+Image'}"
                 alt="${movie.title}">
            <div class="rec-result-info">
                <h3>${movie.title}</h3>
                <p><strong>Genres:</strong> ${movie.genres}</p>
                <p><strong>Director:</strong> ${movie.director}</p>
                <p><span class="match-score">Match: ${(movie.score * 100).toFixed(0)}%</span></p>
                <div style="margin-top: 10px;">
                    <button class="btn" style="padding: 6px 12px; width: auto;" onclick="showMovieDetail(${movie.id})">View Details</button>
                </div>
            </div>
        </div>
    `).join('');
}

function showMovieDetail(movieId) {
    const movie = allMovies.find(m => m.id === movieId);
    if (!movie) return;

    const userRating = userRatings[movieId] || 0;

    const modalContent = `
        <div class="movie-detail-header">
            <div class="movie-detail-poster">
                <img src="${movie.poster_url || 'https://via.placeholder.com/150x225?text=No+Image'}"
                     alt="${movie.title}">
            </div>
            <div class="movie-detail-info">
                <h2>${movie.title}</h2>
                <p><strong>Genres:</strong> ${movie.genres || 'N/A'}</p>
                <p><strong>Director:</strong> ${movie.director || 'N/A'}</p>
                <p><strong>Cast:</strong> ${movie.cast || 'N/A'}</p>
                <p><strong>Release Date:</strong> ${movie.release_date || 'N/A'}</p>
                <p><strong>Average Rating:</strong> ${movie.rating_avg ? movie.rating_avg.toFixed(1) + '/5' : 'Not rated'}</p>
            </div>
        </div>

        <div>
            <h3 style="color: #ff6b35; margin-bottom: 10px;">Overview</h3>
            <p>${movie.overview || 'No overview available'}</p>
        </div>

        <div class="rating-input">
            <span style="color: #e0e0e0;">Your Rating:</span>
            <div class="stars-input" id="starRating">
                ${[1,2,3,4,5].map(i => `
                    <span class="star ${i <= userRating ? 'active' : ''}" onclick="rateMovie(${movieId}, ${i})">★</span>
                `).join('')}
            </div>
        </div>
    `;

    document.getElementById('movieDetailContent').innerHTML = modalContent;
    document.getElementById('movieDetailModal').classList.add('active');
}

async function rateMovie(movieId, rating) {
    try {
        const response = await fetch('/api/rate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ movie_id: movieId, rating })
        });

        if (response.ok) {
            userRatings[movieId] = rating;
            await loadMovies();
            const stars = document.querySelectorAll('.star');
            stars.forEach((star, i) => {
                if (i + 1 <= rating) {
                    star.classList.add('active');
                } else {
                    star.classList.remove('active');
                }
            });
        }
    } catch (error) {
        console.error('Error rating movie:', error);
    }
}

function updateRecommendationForm() {
    const mode = document.getElementById('recMode').value;
    const movieSelect = document.getElementById('movieSelect');
    const alphaSlider = document.getElementById('alphaSlider');

    if (mode === 'content') {
        movieSelect.style.display = 'block';
        alphaSlider.style.display = 'none';
        populateMovieSelect();
    } else if (mode === 'collaborative') {
        movieSelect.style.display = 'none';
        alphaSlider.style.display = 'none';
    } else {
        movieSelect.style.display = 'block';
        alphaSlider.style.display = 'block';
        populateMovieSelect();
    }
}

function populateMovieSelect() {
    const select = document.getElementById('recMovie');
    select.innerHTML = '<option value="">-- Optional: Select a movie --</option>' +
        allMovies.map(m => `<option value="${m.id}">${m.title}</option>`).join('');
}

function updateAlphaDisplay() {
    const alpha = parseFloat(document.getElementById('alpha').value);
    const contentPct = (alpha * 100).toFixed(0);
    const collabPct = ((1 - alpha) * 100).toFixed(0);
    document.getElementById('alphaValue').textContent = `${contentPct}% Your Taste / ${collabPct}% Collaborative`;
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tabName + 'Tab').classList.add('active');
    event.target.classList.add('active');
}

function openAddMovieModal() {
    document.getElementById('addMovieModal').classList.add('active');
    updateRecommendationForm();
}

function closeAddMovieModal() {
    document.getElementById('addMovieModal').classList.remove('active');
}

function openRecommendationModal() {
    document.getElementById('recommendationModal').classList.add('active');
    updateRecommendationForm();
}

function closeRecommendationModal() {
    document.getElementById('recommendationModal').classList.remove('active');
}

function closeMovieDetailModal() {
    document.getElementById('movieDetailModal').classList.remove('active');
}

document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});
