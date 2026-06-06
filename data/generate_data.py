"""
Synthetic Movie Dataset Generator
Generates 200+ realistic movie entries with diverse genres, directors, cast, and descriptions.
"""

import csv
import os
import random

# ── Seed for reproducibility ──────────────────────────────────────────────────
random.seed(42)

# ── Raw data pools ────────────────────────────────────────────────────────────

GENRES = [
    "Action", "Drama", "Comedy", "Thriller", "Sci-Fi",
    "Romance", "Horror", "Animation", "Adventure", "Crime",
]

DIRECTORS = [
    "James Cameron", "Christopher Nolan", "Steven Spielberg", "Martin Scorsese",
    "Quentin Tarantino", "Ridley Scott", "Denis Villeneuve", "David Fincher",
    "Greta Gerwig", "Jordan Peele", "Bong Joon-ho", "Wes Anderson",
    "Chloe Zhao", "Taika Waititi", "Kathryn Bigelow", "Ava DuVernay",
    "Alfonso Cuaron", "Guillermo del Toro", "Damien Chazelle", "Barry Jenkins",
    "Spike Lee", "Sam Mendes", "Alejandro Inarritu", "Paul Thomas Anderson",
    "Sofia Coppola", "Edgar Wright", "Ryan Coogler", "Patty Jenkins",
    "George Miller", "Yorgos Lanthimos", "Robert Eggers", "Rian Johnson",
    "Lulu Wang", "Emerald Fennell", "Celine Sciamma", "Park Chan-wook",
    "Wong Kar-wai", "Ang Lee", "Pedro Almodovar", "Hayao Miyazaki",
]

ACTORS = [
    "Leonardo DiCaprio", "Meryl Streep", "Robert Downey Jr.", "Scarlett Johansson",
    "Tom Hanks", "Cate Blanchett", "Denzel Washington", "Viola Davis",
    "Brad Pitt", "Natalie Portman", "Christian Bale", "Margot Robbie",
    "Joaquin Phoenix", "Florence Pugh", "Ryan Gosling", "Saoirse Ronan",
    "Timothee Chalamet", "Zendaya", "Oscar Isaac", "Lupita Nyong'o",
    "Adam Driver", "Emma Stone", "Michael B. Jordan", "Anya Taylor-Joy",
    "Daniel Kaluuya", "Ana de Armas", "Pedro Pascal", "Jenna Ortega",
    "Austin Butler", "Rachel McAdams", "Jake Gyllenhaal", "Tilda Swinton",
    "Idris Elba", "Charlize Theron", "Keanu Reeves", "Jennifer Lawrence",
    "Will Smith", "Salma Hayek", "Chris Evans", "Gal Gadot",
    "Tom Hardy", "Emily Blunt", "Rami Malek", "Awkwafina",
    "John Boyega", "Hailee Steinfeld", "Dev Patel", "Sandra Bullock",
    "Samuel L. Jackson", "Chadwick Boseman", "Robert Pattinson", "Daisy Ridley",
    "Benedict Cumberbatch", "Brie Larson", "Jason Momoa", "Melissa McCarthy",
    "Matt Damon", "Kate Winslet", "Al Pacino", "Morgan Freeman",
]

# ── Title building blocks ─────────────────────────────────────────────────────

TITLE_TEMPLATES = {
    "Action": [
        "The {adj} {noun}", "Operation {noun}", "{noun} Protocol",
        "Code {noun}", "Strike {noun}", "{adj} Force", "The Last {noun}",
        "{noun} Rising", "Dark {noun}", "Blood {noun}",
        "Iron {noun}", "Thunder {noun}", "The {noun} Files",
    ],
    "Drama": [
        "The {noun} of {place}", "A {adj} Life", "Between {noun} and {noun2}",
        "{noun} Street", "The Weight of {noun}", "Echoes of {noun}",
        "Silent {noun}", "The {adj} Garden", "After the {noun}",
        "Letters from {place}", "Still {noun}", "Broken {noun}",
    ],
    "Comedy": [
        "My {adj} {noun}", "The {adj} Club", "How to {verb} a {noun}",
        "Accidentally {adj}", "{noun} Night", "The {noun} Incident",
        "Seriously {adj}", "Lucky {noun}", "Plan {noun}",
        "The Art of {noun}", "Totally {adj}", "Operation {noun}",
    ],
    "Thriller": [
        "The {adj} Game", "No {noun}", "Behind the {noun}",
        "The {noun} Conspiracy", "{adj} Waters", "The Ninth {noun}",
        "Shattered {noun}", "The {noun} Witness", "Unseen {noun}",
        "Before {noun}", "The {adj} Hour", "Pale {noun}",
    ],
    "Sci-Fi": [
        "{noun} Horizon", "Beyond {noun}", "The {adj} Signal",
        "Quantum {noun}", "Nebula {noun}", "Project {noun}",
        "The {noun} Paradox", "Singularity {noun}", "Zero {noun}",
        "Stellar {noun}", "The {adj} Frontier", "Void {noun}",
    ],
    "Romance": [
        "Love in {place}", "The {noun} of Us", "A {adj} Heart",
        "Forever {adj}", "Under the {noun}", "Two {noun}",
        "The Last {noun}", "Moonlit {noun}", "Paper {noun}",
        "Written in {noun}", "Dear {noun}", "The {adj} Promise",
    ],
    "Horror": [
        "The {noun} Below", "Whispers of {noun}", "{adj} Hollow",
        "The {noun} House", "Night of the {noun}", "Crimson {noun}",
        "The Haunting of {noun}", "Beneath the {noun}", "Black {noun}",
        "They {verb} at Night", "The {adj} Mirror", "Hollow {noun}",
    ],
    "Animation": [
        "The {adj} Kingdom", "{noun} Tales", "The Legend of {noun}",
        "Adventures of {noun}", "The {adj} World", "Little {noun}",
        "{noun} and the Magic {noun2}", "The {adj} Forest", "Sky {noun}",
        "Dream {noun}", "Whispering {noun}", "The {noun} Voyage",
    ],
    "Adventure": [
        "The {adj} Expedition", "Quest for {noun}", "Beyond the {noun}",
        "The {noun} Treasure", "Uncharted {noun}", "The {adj} Journey",
        "Into the {noun}", "The Lost {noun}", "{noun} of the Deep",
        "Voyage of {noun}", "The {adj} Trail", "Wild {noun}",
    ],
    "Crime": [
        "The {noun} Syndicate", "City of {noun}", "The {adj} Heist",
        "Under the {noun}", "The {noun} Connection", "Dirty {noun}",
        "{noun} Alley", "The Last {noun}", "Double {noun}",
        "Crooked {noun}", "The {adj} Ring", "Vice {noun}",
    ],
}

ADJECTIVES = [
    "crimson", "silent", "eternal", "broken", "wild", "fallen", "golden",
    "sacred", "frozen", "burning", "electric", "velvet", "savage", "twisted",
    "hollow", "radiant", "shadow", "neon", "ancient", "infinite", "lost",
    "bitter", "fearless", "reckless", "quiet", "fading", "hidden", "cursed",
    "shining", "desperate", "gentle", "cruel", "brave", "weary", "dark",
    "bright", "cold", "warm", "mysterious", "final", "distant", "forgotten",
]

NOUNS = [
    "storm", "river", "shadow", "dawn", "blade", "crown", "veil", "flame",
    "tide", "ghost", "wolf", "cipher", "mirror", "throne", "spark", "dust",
    "valley", "eagle", "ember", "horizon", "oracle", "lotus", "titan",
    "serpent", "beacon", "arrow", "fortress", "orchid", "raven", "compass",
    "harbor", "legend", "echo", "phoenix", "silence", "moon", "sun",
    "stone", "bridge", "mask", "dream", "whisper", "star", "cage", "fate",
]

NOUNS2 = [
    "light", "truth", "ashes", "dreams", "hope", "rain", "fire",
    "steel", "silk", "bones", "roses", "thunder", "glass", "ice",
    "sand", "wind", "gold", "tears", "smoke", "snow", "petals",
]

PLACES = [
    "Paris", "Tokyo", "New York", "Venice", "Prague", "Istanbul",
    "Barcelona", "Cairo", "Vienna", "Havana", "Mumbai", "Buenos Aires",
    "Lisbon", "Marrakech", "Dublin", "Kyoto", "Casablanca", "Florence",
    "Montreal", "Santiago",
]

VERBS = ["steal", "find", "lose", "save", "break", "chase", "watch", "come"]

# ── Overview templates by genre ───────────────────────────────────────────────

OVERVIEW_TEMPLATES = {
    "Action": [
        "A {role} must navigate a dangerous world of {threat} to save {stakes}. "
        "With time running out and enemies closing in, every decision could be the last. "
        "An explosive tale of survival and redemption.",
        "When a {threat} threatens to destabilize an entire region, a seasoned {role} is called back for one final mission. "
        "Allies become enemies and the line between right and wrong blurs in this high-octane thriller.",
        "After surviving a devastating {event}, a former {role} seeks vengeance against those who destroyed everything. "
        "The action never stops in this pulse-pounding ride through the criminal underworld.",
    ],
    "Drama": [
        "A deeply moving portrait of {character} struggling to find meaning after {event}. "
        "Set against the backdrop of {setting}, the film explores themes of loss, hope, and human connection. "
        "A powerful story that stays with you long after the credits roll.",
        "Spanning three decades, this intimate drama follows {character} through triumph and heartbreak. "
        "As family secrets unravel, the true cost of ambition comes to light. "
        "An unforgettable exploration of what it means to truly belong.",
        "In the quiet corners of {setting}, {character} confronts a past that refuses to stay buried. "
        "Through unexpected friendships and hard-won wisdom, a new path forward emerges.",
    ],
    "Comedy": [
        "When {character} accidentally {event}, chaos and hilarity ensue in this laugh-out-loud comedy. "
        "Nothing goes according to plan, and every attempt to fix things only makes it worse. "
        "A feel-good film that will leave you smiling.",
        "A mismatched group of {characters} must work together to pull off the impossible before the deadline. "
        "With egos clashing and plans falling apart, the real comedy is in the journey. "
        "Heartwarming, witty, and endlessly entertaining.",
        "{character} thought retirement would be peaceful, but a series of absurd events pulls them back into the spotlight. "
        "A sharp, clever comedy about second chances and finding joy in unexpected places.",
    ],
    "Thriller": [
        "Nothing is as it seems when {character} uncovers a conspiracy that reaches the highest levels of power. "
        "Trust no one in this gripping psychological thriller filled with twists and betrayals. "
        "The truth may be the most dangerous weapon of all.",
        "A seemingly perfect {setting} hides dark secrets that {character} is determined to expose. "
        "As the investigation deepens, the hunter becomes the hunted. "
        "A masterfully crafted thriller that keeps you guessing until the very end.",
        "After receiving a cryptic message from a dead colleague, {character} is drawn into a web of deception. "
        "Every clue leads to more questions, and the clock is ticking. "
        "An edge-of-your-seat thriller with a devastating finale.",
    ],
    "Sci-Fi": [
        "In a future where {concept}, humanity faces its greatest challenge yet. "
        "A brilliant {role} discovers a truth that could change everything, but powerful forces want it buried. "
        "A thought-provoking sci-fi epic about the cost of progress.",
        "When a mysterious {anomaly} appears, a team of scientists races to understand its origins. "
        "What they find challenges everything we know about {concept}. "
        "Visually stunning and intellectually thrilling.",
        "Decades after the great collapse, {character} embarks on a perilous journey across a transformed Earth. "
        "Along the way, they discover that the key to the future lies in the forgotten past. "
        "A sweeping sci-fi adventure with heart.",
    ],
    "Romance": [
        "Two strangers from different worlds find an unexpected connection in {setting}. "
        "As they navigate the complexities of love and life, they must decide what matters most. "
        "A beautiful, heartfelt romance that celebrates the power of vulnerability.",
        "When {character} returns to their hometown, old feelings resurface and new possibilities emerge. "
        "Against the odds and despite past wounds, love finds a way. "
        "A tender, emotionally rich love story.",
        "A chance encounter on a rainy evening in {setting} sparks a connection that neither expected. "
        "Through letters, phone calls, and stolen moments, two souls discover that distance is no match for destiny.",
    ],
    "Horror": [
        "A group of friends ventures into {setting}, unaware of the ancient evil that lurks beneath. "
        "As night falls and the terror begins, survival becomes the only goal. "
        "A chilling horror film that will haunt your dreams.",
        "After moving into a seemingly perfect {location}, {character} begins experiencing disturbing phenomena. "
        "The house has a history, and it is not done claiming victims. "
        "A slow-burn horror masterpiece dripping with dread.",
        "Something is watching from the darkness in {setting}. "
        "When people start disappearing, {character} must face an unimaginable terror to save those they love. "
        "Atmospheric and relentless, this horror film redefines fear.",
    ],
    "Animation": [
        "In a magical world where {concept}, a young {character} embarks on an extraordinary adventure. "
        "Along the way, they discover the true meaning of courage and friendship. "
        "A visually breathtaking animated masterpiece for all ages.",
        "When their homeland is threatened by a dark force, an unlikely hero must journey across fantastical lands. "
        "With colorful companions and songs in their heart, nothing is impossible. "
        "A joyful, dazzling animated adventure.",
        "A curious {character} stumbles into a hidden realm filled with wonder and danger. "
        "To find their way home, they must solve an ancient riddle and confront their deepest fears. "
        "A stunning animated film with a powerful message about self-discovery.",
    ],
    "Adventure": [
        "An intrepid {role} sets out on a quest to find the legendary {artifact} before it falls into the wrong hands. "
        "Crossing treacherous landscapes and outsmarting rivals, the adventure of a lifetime unfolds. "
        "A thrilling ride from start to finish.",
        "When a map to an uncharted {location} surfaces, a ragtag crew of explorers assembles for the journey. "
        "But they are not the only ones seeking what lies at the end. "
        "An epic adventure filled with wonder and peril.",
        "Stranded in the wilderness after a catastrophic {event}, {character} must use every skill to survive. "
        "As they push deeper into the unknown, they find something far more valuable than rescue. "
        "An awe-inspiring adventure about resilience and discovery.",
    ],
    "Crime": [
        "In the gritty underbelly of {setting}, a detective pursues a mastermind who is always one step ahead. "
        "Loyalties are tested and the price of justice is high. "
        "A gripping crime saga with unforgettable characters.",
        "A meticulous heist goes wrong, and the crew must navigate betrayal and suspicion to survive. "
        "With the police closing in and trust crumbling, every second counts. "
        "A slick, tense crime thriller that never lets up.",
        "When {character} witnesses something they should not have, they are drawn into a criminal empire's deadly inner circle. "
        "The only way out is to bring it all down from the inside. "
        "A riveting crime drama with jaw-dropping twists.",
    ],
}

OVERVIEW_FILLS = {
    "role": ["soldier", "detective", "agent", "operative", "scientist", "pilot", "journalist", "hacker"],
    "threat": ["terrorism", "corruption", "a criminal empire", "an arms dealer", "a rogue state", "a powerful cartel"],
    "stakes": ["innocent lives", "a nation", "their family", "the world", "their city", "an entire generation"],
    "event": ["betrayal", "accident", "explosion", "disappearance", "scandal", "crisis", "natural disaster"],
    "character": ["a young woman", "a retired professor", "an ambitious lawyer", "a struggling artist",
                   "a single parent", "a war veteran", "a small-town teacher", "a brilliant surgeon"],
    "characters": ["strangers", "colleagues", "neighbours", "old friends", "rivals", "siblings"],
    "setting": ["a small coastal town", "1960s New York", "modern-day Berlin", "rural Ireland",
                 "post-war London", "the Australian outback", "a Mediterranean island", "downtown Chicago"],
    "concept": ["memories can be traded", "AI governs society", "time flows backward",
                 "parallel worlds overlap", "emotions are currency", "gravity can be controlled"],
    "anomaly": ["signal from deep space", "rift in spacetime", "alien artifact", "quantum anomaly"],
    "location": ["Victorian mansion", "remote cabin", "abandoned hospital", "island estate"],
    "artifact": ["Sunstone", "Crown of Aetheris", "Heart of the Void", "Codex Eternum", "Eye of Orion"],
}

KEYWORD_POOLS = {
    "Action": ["explosion", "chase", "combat", "military", "weapons", "survival", "rescue", "mission", "undercover", "mercenary"],
    "Drama": ["family", "loss", "redemption", "relationships", "identity", "grief", "ambition", "secrets", "coming-of-age", "sacrifice"],
    "Comedy": ["funny", "misunderstanding", "absurd", "slapstick", "wit", "satire", "awkward", "prank", "wedding", "road-trip"],
    "Thriller": ["suspense", "mystery", "conspiracy", "deception", "paranoia", "investigation", "serial-killer", "stalker", "espionage", "double-cross"],
    "Sci-Fi": ["space", "alien", "technology", "dystopia", "AI", "time-travel", "cyberpunk", "robot", "virtual-reality", "genetic-engineering"],
    "Romance": ["love", "heartbreak", "reunion", "soulmate", "wedding", "long-distance", "forbidden-love", "chemistry", "passion", "devotion"],
    "Horror": ["ghost", "haunted", "demon", "curse", "supernatural", "slasher", "possession", "nightmare", "isolation", "occult"],
    "Animation": ["magic", "friendship", "quest", "fairy-tale", "talking-animals", "enchanted", "hero", "colorful", "musical", "fantasy"],
    "Adventure": ["treasure", "exploration", "jungle", "pirates", "map", "expedition", "discovery", "wilderness", "ancient-ruins", "quest"],
    "Crime": ["heist", "detective", "mafia", "corruption", "noir", "underworld", "smuggling", "informant", "gang", "investigation"],
}


def _fill_template(template: str) -> str:
    """Fill a template string with random values, handling {noun2} separately."""
    result = template
    while "{" in result:
        for key in ["adj", "noun2", "noun", "place", "verb"]:
            placeholder = "{" + key + "}"
            while placeholder in result:
                pool = {
                    "adj": ADJECTIVES,
                    "noun": NOUNS,
                    "noun2": NOUNS2,
                    "place": PLACES,
                    "verb": VERBS,
                }[key]
                result = result.replace(placeholder, random.choice(pool), 1)
        # Break if nothing was replaced (safety)
        if "{" in result:
            break
    return result


def _fill_overview(template: str) -> str:
    """Fill an overview template with contextual words."""
    result = template
    for key, pool in OVERVIEW_FILLS.items():
        placeholder = "{" + key + "}"
        while placeholder in result:
            result = result.replace(placeholder, random.choice(pool), 1)
    return result


def generate_movies(n: int = 220) -> list[dict]:
    """Generate *n* synthetic movie records."""
    movies = []
    used_titles: set[str] = set()

    for _ in range(n):
        # Pick 1-3 genres (primary determines templates)
        num_genres = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
        chosen_genres = random.sample(GENRES, num_genres)
        primary_genre = chosen_genres[0]

        # Title
        template = random.choice(TITLE_TEMPLATES[primary_genre])
        title = _fill_template(template)
        # Ensure unique title
        attempt = 0
        while title in used_titles and attempt < 20:
            template = random.choice(TITLE_TEMPLATES[primary_genre])
            title = _fill_template(template)
            attempt += 1
        if title in used_titles:
            title = title + " " + str(random.randint(2, 9))
        used_titles.add(title)

        # Director
        director = random.choice(DIRECTORS)

        # Cast (3-4 unique actors)
        cast = random.sample(ACTORS, random.randint(3, 4))

        # Overview
        overview_template = random.choice(OVERVIEW_TEMPLATES[primary_genre])
        overview = _fill_overview(overview_template)

        # Keywords (4-7 from genre pools)
        kw_pool: list[str] = []
        for g in chosen_genres:
            kw_pool.extend(KEYWORD_POOLS[g])
        keywords = random.sample(list(set(kw_pool)), min(random.randint(4, 7), len(set(kw_pool))))

        # Rating & year
        rating = round(random.uniform(4.0, 9.5), 1)
        year = random.randint(1990, 2024)

        movies.append({
            "title": title,
            "genres": ", ".join(chosen_genres),
            "director": director,
            "cast": ", ".join(cast),
            "overview": overview,
            "keywords": ", ".join(keywords),
            "rating": rating,
            "year": year,
        })

    return movies


def save_to_csv(movies: list[dict], filepath: str | None = None) -> str:
    """Write movie records to CSV and return the filepath."""
    if filepath is None:
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "movies.csv")

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fieldnames = ["title", "genres", "director", "cast", "overview", "keywords", "rating", "year"]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(movies)

    return filepath


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("[*] Generating synthetic movie dataset ...")
    data = generate_movies(220)
    path = save_to_csv(data)
    print(f"[+] {len(data)} movies saved to {path}")
