# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ⚙️  GLOBAL CONFIGURATION — edit ONLY this cell before running         ║
# ╚══════════════════════════════════════════════════════════════════════════╝
import os
import pickle
import hashlib
import time
from pathlib import Path
from functools import wraps

# ── Paths ──────────────────────────────────────────────────────────────────
DATA_FOLDER = r"C:\Users\PC\Downloads\data_minig\ao3_scrape_files"   # ← CHANGE THIS
CACHE_DIR   = r"C:\Users\PC\Downloads\data_minig\full_cache"

# ── Sampling  (NLP + ML only — keeps runtime < 10 min on 840k works) ──────
NLP_SAMPLE_N = 30_000   # top-N works by kudos for NLP feature extraction
ML_SAMPLE_N  = 50_000   # top-N works by kudos for ML training + clustering

# ── Association Rule Mining ────────────────────────────────────────────────
ARM_TOP_TAGS       = 300    # restrict to top-N most frequent normalised tags
ARM_MIN_SUPPORT    = 0.01   # tag-set must appear in ≥ 1% of works in fandom
ARM_MIN_CONFIDENCE = 0.30
ARM_MIN_LIFT       = 1.50   # only surface rules with meaningful lift

# ── Machine Learning ───────────────────────────────────────────────────────
K_CLUSTERS       = 5     # K-Means archetypes per fandom
RF_N_ESTIMATORS  = 200
TOP_TAG_FEATURES = 100   # top normalised tags as binary ML features

# ── Focus fandom (None = all fandoms shown together) ──────────────────────
FANDOM_FOCUS = None

# ── Tag Normalisation Toggle ──────────────────────────────────────────────
ENABLE_TAG_COLLAPSE = True   # Set to True for full collapse (optimized now)
USE_CACHED_TAGS = True       # Use cached normalised tags if available

# ─── Keyword Groups for Tag Normalisation ────────────────────────────────
# Format:  "Canonical Name": ["keyword1", "keyword2", ...]
# A tag is renamed to the group whose keyword appears anywhere in it (case-insensitive).
# ORDER MATTERS — first matching group wins.
KEYWORD_GROUPS = {
    "Fluff":                ["fluff", "fluffy", "tooth-rotting", "warm and fuzzy",
                             "soft", "cute", "adorable", "wholesome"],
    "Angst":                ["angst", "angsty", "heartbreak", "heartache",
                             "grief", "sorrow", "tragedy", "sad", "depressing"],
    "Hurt/Comfort":         ["hurt/comfort", "hurt comfort", "h/c", "whump",
                             "comfort", "recovery", "healing"],
    "Romance":              ["romance", "romantic", "slow burn", "love",
                             "confession", "dating", "courtship", "marriage",
                             "established relationship"],
    "Smut / Explicit":      ["smut", "lemon", "nsfw", "porn", "erotic",
                             "sexual", "explicit content", "sex scene"],
    "Action / Adventure":   ["action", "adventure", "fight", "battle",
                             "war", "mission", "quest", "combat"],
    "Alternate Universe":   ["alternate universe", " au ", "modern au",
                             "coffee shop", "college au", "high school au",
                             "no powers", "canon divergence"],
    "Humor / Crack":        ["humor", "humour", "crack", "comedy", "funny",
                             "parody", "satire", "silly"],
    "Family / Friendship":  ["family", "friendship", "found family",
                             "platonic", "siblings", "parental", "brotp"],
    "Dark / Horror":        ["dark", "horror", "gore", "violence",
                             "disturbing", "death", "murder", "torture", "trauma"],
    "Mystery / Thriller":   ["mystery", "thriller", "detective", "crime",
                             "suspense", "investigation"],
    "Time Travel / Fix-It": ["time travel", "fix-it", "fixit", "second chance",
                             "do-over", "redo", "time loop"],
    "Character Study":      ["character study", "introspection",
                             "character exploration", "character development"],
    "Crossover":            ["crossover", "cross-over", "fusion", "multiverse"],
    "Original Characters":  ["original character", " oc ", "original protagonist",
                             "self-insert"],
    "Angst + Happy Ending": ["angst with a happy ending", "happy ending",
                             "bittersweet"],
    "Memory / Amnesia":     ["memory", "amnesia", "memory loss", "forgotten",
                             "forgetting"],
    "Enemies to Lovers":    ["enemies to lovers", "enemies-to-lovers",
                             "rivals to lovers", "hate to love"],
    "Fake Dating":          ["fake dating", "fake relationship",
                             "pretend", "fake marriage"],
    "Soulmate":             ["soulmate", "soul bond", "soulbond",
                             "destined", "fated"],
    # NSFW Content Filtering
    "Mature / Explicit":    ["mature", "explicit", "adult content", "adult themes"],
    "Violence / Gore":      ["violence", "gore", "blood", "torture", "death",
                             "murder", "killing", "blood and gore"],
    "Sexual Content":       ["sexual content", "sex", "intercourse", "penetration",
                             "oral sex", "anal sex", "vaginal sex", "hand job",
                             "blow job", "cunnilingus", "rimming", "masturbation"],
    "Underage":             ["underage", "underage sex", "underage character"],
    "Rape/Non-Con":         ["rape", "non-con", "nonconsensual", "dub-con", 
                             "dubious consent", "sexual assault"],
}

# NSFW tag markers for filtering
NSFW_TAG_MARKERS = [
    "smut", "explicit", "porn", "erotic", "sexual", "sex scene",
    "mature", "adult content", "violence", "gore", "blood", "torture",
    "oral sex", "anal sex", "vaginal sex", "blow job", "hand job",
    "cunnilingus", "rimming", "masturbation", "underage", "rape", "non-con",
    "dub-con", "dubious consent", "sexual assault", "incest", "kink",
    "bdsm", "bondage", "dominance", "submission", "spanking", "choking"
]

os.makedirs(CACHE_DIR, exist_ok=True)

# ── Caching Utility ────────────────────────────────────────────────────────
def cache_result(cache_name, force_recompute=False):
    """Decorator to cache function results to disk."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_path = Path(CACHE_DIR) / f"{cache_name}.pkl"
            
            if not force_recompute and cache_path.exists():
                print(f"  Loading cached: {cache_name}")
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            
            print(f"  Computing: {cache_name}...")
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"    Completed in {elapsed:.2f}s")
            
            with open(cache_path, 'wb') as f:
                pickle.dump(result, f)
            
            return result
        return wrapper
    return decorator

print("✓ Configuration loaded")
print(f"  DATA_FOLDER    = {DATA_FOLDER}")
print(f"  CACHE_DIR      = {CACHE_DIR}")
print(f"  NLP_SAMPLE_N   = {NLP_SAMPLE_N:,}  |  ML_SAMPLE_N = {ML_SAMPLE_N:,}")
print(f"  ARM top tags   = {ARM_TOP_TAGS}   |  min_support = {ARM_MIN_SUPPORT}")
print(f"  K_CLUSTERS     = {K_CLUSTERS}")
print(f"  FANDOM_FOCUS   = {FANDOM_FOCUS or 'All fandoms'}")
print(f"  Keyword groups = {len(KEYWORD_GROUPS)} defined")
print(f"  Caching enabled: {CACHE_DIR}")
