import math
from collections import defaultdict

class ContentBasedRecommender:
    def __init__(self, movie_dict):
        self.movies = movie_dict
        self.vectors = {}
        self._vectorize_all()

    def _make_soup(self, movie_id):
        m = self.movies.get(movie_id, {})
        soup = (m.get('genres', '') + " ") * 3 + m.get('director', '') + " " + m.get('cast', '') + " " + m.get('overview', '')
        return soup.lower().replace(",", " ").split()

    def _vectorize_all(self):
        all_soups = [self._make_soup(mid) for mid in self.movies]
        vocab = set()
        for soup in all_soups:
            vocab.update(soup)
        self.vocab = sorted(vocab)
        self.idf = {}
        N = len(self.movies)
        for word in self.vocab:
            df = sum(1 for soup in all_soups if word in soup)
            self.idf[word] = math.log((1 + N) / (1 + df)) + 1

        for mid in self.movies:
            soup = self._make_soup(mid)
            vec = {}
            total = len(soup)
            for word in set(soup):
                tf = soup.count(word) / total if total > 0 else 0
                vec[word] = tf * self.idf[word]
            self.vectors[mid] = vec

    def cosine_similarity(self, vec1, vec2):
        dot = sum(vec1.get(w, 0) * vec2.get(w, 0) for w in set(vec1) | set(vec2))
        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values())) if vec1 else 0
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values())) if vec2 else 0
        if norm1 == 0 or norm2 == 0:
            return 0
        return dot / (norm1 * norm2)

    def recommend(self, movie_title, top_n=5):
        seed_id = next((mid for mid in self.movies if self.movies[mid]['title'].lower() == movie_title.lower()), None)
        if seed_id is None:
            return []

        seed_vec = self.vectors.get(seed_id, {})
        scores = {}
        for mid in self.movies:
            if mid != seed_id:
                scores[mid] = self.cosine_similarity(seed_vec, self.vectors.get(mid, {}))

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

class CollaborativeFiltering:
    def __init__(self, ratings_dict):
        self.user_item = ratings_dict
        self.item_user = defaultdict(dict)
        for uid, movies in ratings_dict.items():
            for mid, rating in movies.items():
                self.item_user[mid][uid] = rating

    def cosine_similarity(self, vec1, vec2):
        common_keys = set(vec1) & set(vec2)
        if not common_keys:
            return 0
        dot = sum(vec1[k] * vec2[k] for k in common_keys)
        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values())) if vec1 else 0
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values())) if vec2 else 0
        if norm1 == 0 or norm2 == 0:
            return 0
        return dot / (norm1 * norm2)

    def recommend(self, user_id, top_n=5, k=5):
        if user_id not in self.user_item or not self.user_item[user_id]:
            return []

        user_ratings = self.user_item[user_id]
        all_movies = set(self.item_user.keys())
        unrated = {mid: None for mid in all_movies if mid not in user_ratings}

        if not unrated:
            return []

        scores = {}
        for movie_id in unrated:
            ratings = self.item_user.get(movie_id, {})
            similarities = []
            for other_uid in ratings:
                if other_uid != user_id and other_uid in self.user_item:
                    sim = self.cosine_similarity(user_ratings, self.user_item[other_uid])
                    if sim > 0:
                        similarities.append((sim, ratings[other_uid]))

            if similarities:
                similarities.sort(reverse=True)
                top_sims = similarities[:k]
                weighted_sum = sum(sim * rating for sim, rating in top_sims)
                sim_sum = sum(sim for sim, _ in top_sims)
                scores[movie_id] = weighted_sum / sim_sum if sim_sum > 0 else 0

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
