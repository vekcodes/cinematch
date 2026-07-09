import csv
import random
from pathlib import Path

random.seed(42)

movies = [
    ("Galaxy Horizon", "Sci-Fi,Adventure", "Christopher Nolan", "Matthew McConaughey,Anne Hathaway", "Explorers venture into a black hole"),
    ("Midnight Echo", "Thriller,Mystery", "David Fincher", "Rami Malek,Cate Blanchett", "A detective chases a cryptic serial killer"),
    ("Autumn Leaves", "Drama,Romance", "Greta Gerwig", "Timothée Chalamet,Saoirse Ronan", "Two strangers meet in a small town"),
    ("Code Red", "Action,Sci-Fi", "Denis Villeneuve", "Tom Hardy,Oscar Isaac", "Special ops team races to stop a cyberattack"),
    ("Neon Dreams", "Drama,Music", "Barry Jenkins", "Childish Gambino,Zendaya", "A producer chases musical stardom"),
    ("Silent Witness", "Crime,Drama", "Martin Scorsese", "Leonardo DiCaprio,Al Pacino", "Mob witness enters protection program"),
    ("Castle in the Sky", "Fantasy,Adventure", "Hayao Miyazaki", "Anne Hathaway,Joseph Gordon-Levitt", "Children discover a floating island"),
    ("Red Canyon", "Western,Drama", "Quentin Tarantino", "Brad Pitt,Christoph Waltz", "Outlaws hunted across the desert"),
    ("Last Light", "Sci-Fi,Horror", "Alex Garland", "Domhnall Gleeson,Ava DuVernay", "Humanity's final space mission fails"),
    ("Ocean Blue", "Adventure,Drama", "Werner Herzog", "Oscar Isaac,Tilda Swinton", "Submarine crew discovers underwater city"),
    ("Iron Heart", "Action,Drama", "John Wick director", "Keanu Reeves,Charlize Theron", "Retired soldier pulled back into action"),
    ("Whisper Room", "Thriller,Horror", "Ari Aster", "Florence Pugh,Jack Reynor", "Guests trapped in haunted mansion"),
    ("Cold Case", "Mystery,Crime", "Denis Villeneuve", "Jake Gyllenhaal,Meryl Streep", "Detective reopens a 20-year-old murder"),
    ("Fire and Ice", "Fantasy,Romance", "Peter Jackson", "Timothée Chalamet,Florence Pugh", "Two kingdoms at war discover love"),
    ("Echoes of Tomorrow", "Sci-Fi,Drama", "Christopher Nolan", "Tenet cast reunion", "Time-traveling agent saves the world"),
    ("Shadow Play", "Thriller,Drama", "Ari Aster", "Saoirse Ronan,Dev Patel", "Photographer uncovers dark conspiracy"),
    ("Golden Hour", "Drama,Romance", "Greta Gerwig", "Saoirse Ronan,Timothée Chalamet", "Artist and musician fall in love"),
    ("Danger Zone", "Action,Thriller", "Chad Stahelski", "Charlize Theron,Tom Cruise", "Spies on international heist"),
    ("Forgotten Path", "Drama,Fantasy", "Guillermo del Toro", "Benedict Cumberbatch,Emma Stone", "A man discovers his mysterious past"),
    ("Last Stand", "Action,Western", "Taika Waititi", "Oscar Isaac,Chris Hemsworth", "Cowboys defend small town"),
    ("Midnight City", "Crime,Drama", "Michael Mann", "Al Pacino,Robert De Niro", "Cop and criminal cat-and-mouse game"),
    ("Storm Rising", "Action,Adventure", "Kathryn Bigelow", "Charlize Theron,Oscar Isaac", "Pilot survives impossible hurricane"),
    ("Whispers in Dark", "Horror,Thriller", "Ari Aster", "Florence Pugh,Jack Reynor", "Family haunted by malevolent spirit"),
    ("Sunset Boulevard", "Drama,Crime", "Martin Scorsese", "Leonardo DiCaprio,Margot Robbie", "Wealthy con artist meets his match"),
    ("Rise of Legends", "Fantasy,Adventure", "Peter Jackson", "Henry Cavill,Cate Blanchett", "Warriors unite against dark forces"),
    ("Blue Horizon", "Sci-Fi,Adventure", "Denis Villeneuve", "Oscar Isaac,Zendaya", "Space colonists explore alien world"),
    ("Dark Mirror", "Thriller,Sci-Fi", "Alex Garland", "Domhnall Gleeson,Ava DuVernay", "AI becomes sentient and dangerous"),
    ("Crimson Trail", "Western,Action", "Quentin Tarantino", "Brad Pitt,Samuel L. Jackson", "Bounty hunters on collision course"),
    ("Heart of Steel", "Drama,Action", "Christopher Nolan", "Christian Bale,Marion Cotillard", "Industrial revolution spy thriller"),
    ("Lost Island", "Adventure,Fantasy", "Werner Herzog", "Oscar Isaac,Tilda Swinton", "Explorers shipwrecked on mysterious island"),
    ("Neural Link", "Sci-Fi,Thriller", "Alex Garland", "Alicia Vikander,Domhnall Gleeson", "Human consciousness uploaded to network"),
    ("Summer of '77", "Drama,Music", "Barry Jenkins", "Timothée Chalamet,Florence Pugh", "Young musicians discover themselves"),
    ("Clockwork Angel", "Fantasy,Adventure", "Guillermo del Toro", "Benedict Cumberbatch,Tilda Swinton", "Steampunk world on brink of revolution"),
    ("Frost Bite", "Horror,Thriller", "Ari Aster", "Florence Pugh,Oscar Isaac", "Research team in arctic finds something"),
    ("Velocity", "Action,Sci-Fi", "Chad Stahelski", "Tom Cruise,Oscar Isaac", "Racer hijacked for dangerous heist"),
    ("Echo Protocol", "Thriller,Sci-Fi", "Denis Villeneuve", "Jake Gyllenhaal,Zendaya", "Secret government experiment exposed"),
    ("Dancing Shadows", "Drama,Romance", "Greta Gerwig", "Saoirse Ronan,Dev Patel", "Dancers pursue their dreams"),
    ("Venom Strike", "Action,Thriller", "John Wick director", "Keanu Reeves,Oscar Isaac", "Black ops team hunts terrorist"),
    ("Ancient Curse", "Horror,Fantasy", "Guillermo del Toro", "Benedict Cumberbatch,Emma Stone", "Archaeologist awakens ancient evil"),
    ("Thunder Road", "Drama,Crime", "Michael Mann", "Oscar Isaac,Matthew McConaughey", "Smuggler turned informant"),
    ("Frozen Heart", "Drama,Romance", "Barry Jenkins", "Timothée Chalamet,Saoirse Ronan", "Couple surviving arctic expedition"),
    ("Savage Lands", "Action,Western", "Taika Waititi", "Oscar Isaac,Henry Cavill", "Frontier justice in wild west"),
    ("Terminal Velocity", "Action,Sci-Fi", "Kathryn Bigelow", "Charlize Theron,Tom Hardy", "Pilot in zero-gravity dogfight"),
    ("Sacred Ground", "Drama,Fantasy", "Werner Herzog", "Oscar Isaac,Tilda Swinton", "Mystical journey through ancient lands"),
    ("Vortex", "Sci-Fi,Thriller", "Christopher Nolan", "Matthew McConaughey,Anne Hathaway", "Gravitational anomaly threatens Earth"),
    ("Silent Night", "Thriller,Crime", "David Fincher", "Rami Malek,Cate Blanchett", "Serial killer strikes on Christmas"),
    ("Midnight Requiem", "Drama,Music", "Barry Jenkins", "Oscar Isaac,Florence Pugh", "Jazz musician's final performance"),
    ("Crimson Skies", "Action,Adventure", "Kathryn Bigelow", "Oscar Isaac,Charlize Theron", "Aerial dogfights over war zone"),
    ("Beyond the Stars", "Sci-Fi,Drama", "Denis Villeneuve", "Oscar Isaac,Zendaya", "Stranded astronauts find home planet"),
    ("Void", "Horror,Sci-Fi", "Alex Garland", "Ava DuVernay,Domhnall Gleeson", "Deep space station loses oxygen"),
]

genres_list = ["Sci-Fi", "Adventure", "Thriller", "Mystery", "Drama", "Romance", "Action", "Crime", "Fantasy", "Western", "Horror", "Music"]
directors = ["Christopher Nolan", "David Fincher", "Greta Gerwig", "Denis Villeneuve", "Barry Jenkins", "Martin Scorsese", "Hayao Miyazaki", "Quentin Tarantino", "Alex Garland", "Werner Herzog", "John Wick director", "Ari Aster", "Peter Jackson", "Guillermo del Toro", "Taika Waititi", "Michael Mann", "Kathryn Bigelow", "Chad Stahelski"]

Path("data").mkdir(exist_ok=True)

with open("data/movies.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "title", "genres", "director", "cast", "overview"])
    for i, (title, genres, director, cast, overview) in enumerate(movies, 1):
        writer.writerow([i, title, genres, director, cast, overview])

with open("data/ratings.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["user_id", "movie_id", "rating"])
    for user_id in range(1, 46):
        for _ in range(random.randint(8, 18)):
            movie_id = random.randint(1, 50)
            rating = random.choice([1, 2, 3, 4, 5])
            writer.writerow([user_id, movie_id, rating])

print("Data generated: 50 movies, 45 users with ratings")
