## Report Structure (≤ 6 pages, LaTeX)

Based on rubric criteria **2.15 (Content & Findings)**, **2.16 (Reflection & Justification)**, and **2.17 (Formatting)**.

---

### 1. Introduction & Motivation *(~0.5 page)*
**Headline:** *"AO3 at Scale: Understanding Fandom Culture Through Data"*

- What is Archive of Our Own (AO3), and why does it matter as a data source?
- Core research question: *What patterns in tags, sentiment, and fandom activity predict reader engagement?*
- Why this is a non-trivial visualization challenge: multi-dimensional tag data (hundreds of sparse tags per work), temporal drift, mixed content types (SFW/NSFW), and NLP-derived emotion signals across 300k+ works.

---

### 2. Dataset & Preprocessing *(~1 page)*
**Headline:** *"From Raw Scrapes to a Unified Analytics-Ready Dataset"*

- **Source**: Web-scraped AO3 metadata across 11 fandoms (Batman, MHA, Naruto, Jujutsu Kaisen, Good Omens, Game of Thrones, The Hobbit, Sherlock, Star Wars, Middle-Earth, etc.)
- **Structure**: Works with fields — `work_id`, `fandom`, `additional_tags`, `hits`, `kudos`, `bookmarks`, `comments`, `word_count`, `last_updated`, `rating`, `summary`
- **Pipeline** (`processing/`):
  1. **Merge** raw per-fandom CSVs → `combined_all_works.csv`
  2. **Clean** (`clean.py`): deduplication on `work_id`, fandom name canonicalization (strip media-type suffixes, normalize case), tag normalization, numeric coercion, date parsing
  3. **SFW/NSFW split** (`nsfw_split.py`): by AO3 rating field
  4. **Sentiment analysis** (`sentimental_analysis.py`): NRCLex (8-emotion lexicon), VADER (compound/pos/neg scores), TextBlob (subjectivity) applied per summary in 2,000-row chunks
  5. **ML embeddings** (`ml_pipeline.py`): SentenceTransformer → `.npy` + PCA coordinates → `work_clusters.csv`
- **Limitations**: no full-body text (summaries only for NLP); scrape reflects a point-in-time snapshot; tag sparsity is high.

---

### 3. Dashboard Design & Interactivity *(~1.5 pages)*
**Headline:** *"Seven Analytical Lenses on Fanfiction Metadata"*

#### 3.1 Layout & Navigation
- Python Shiny `page_sidebar` + `navset_tab` with 6 panels: Tag Analysis, Fandom Distribution, Word Cloud, Impact Analysis, Sentiment Profile, Temporal Trends, Clustering (ML)
- Global sidebar controls: fandom multi-select, date range slider, SFW/NSFW radio, metric dropdown (hits/kudos/bookmarks/comments/word count), Top-N sliders
- Summary stat cards always visible (Total Works, Clusters, Avg Hits, Largest Cluster)

#### 3.2 Charts & Interaction Decisions
| Panel | Chart | Why this type |
|---|---|---|
| Tag Analysis | Horizontal bar, color = avg hits | Ranks sparse multi-valued tags; dual encoding shows volume vs. efficiency |
| Fandom Distribution | Stacked bar ×2 (count + ratio) | Side-by-side shows absolute size vs. content-type composition |
| Word Cloud | Frequency word cloud (circle / AO3 logo mask) | Gives gestalt tag vocabulary at a glance |
| Impact Analysis | Correlation heatmap | Surfaces co-occurrence patterns among top tags and engagement |
| Sentiment Profile | Bar + Radar + Box plot | Three angles: prevalence, collective fingerprint, and success impact |
| Temporal Trends | Dual-axis bar+line + Stacked area | Volume vs. quality (hits) over time; fandom rise/fall storyline |
| Clustering (ML) | PCA scatter | Spatial separation of semantically related works |

- **Reactive filtering**: all charts re-render on any sidebar control change; percentage slider sub-samples the ML scatter for performance.
- **Interactivity**: Plotly hover tooltips on all charts; full-screen mode on all cards; brushing/zoom on scatter.

---

### 4. ML & Analytics Methods *(~0.75 page)*
**Headline:** *"Embedding Semantics and Emotion into the Visual Workflow"*

#### 4.1 NLP Sentiment Pipeline
- **VADER** → polarity scores on summaries (fast, rule-based, good for short social text)
- **TextBlob** → subjectivity score
- **NRCLex** (NRC Emotion Lexicon) → 8-dimensional emotion vector per summary (fear, anger, trust, surprise, sadness, disgust, joy, anticipation) + `top_emotion` label
- Justification: three complementary tools capture valence, subjectivity, and categorical emotion — no single tool is sufficient for short, stylized fanfiction summaries.

#### 4.2 Works Clustering (Unsupervised ML)
- `SentenceTransformer` (`all-MiniLM-L6-v2`) encodes concatenated `fandom + additional_tags` text → 384-dim dense embeddings
- `PCA` (2 components) for 2D visualization
- `KMeans` (k=8, random_state=42) on PCA coordinates for cluster labels
- Justification: semantic embeddings capture tag meaning (not just co-occurrence); PCA + KMeans is interpretable and renders in the browser at scale via a percentage sample slider.

---

### 5. Key Findings *(~1 page)*
**Headline:** *"What the Data Reveals About Fandom Behavior"*

- **Tag efficiency gap**: "Fluff" and "Hurt/Comfort" dominate by total hits (~70M), but niche character-specific tags like "Bamf Midoriya Izuku" and "Quirkless Midoriya Izuku" have the *highest average hits per work* (darkest red on the bar chart) — volume ≠ quality signal.
- **SFW dominates volume, NSFW varies by fandom**: MHA and Naruto are ~55% SFW; some Tolkien sub-fandoms (A Knight of the Seven Kingdoms) skew heavily NSFW (>75%). Content culture differs sharply by fandom.
- **Emotional fingerprint of AO3**: "Trust" is the dominant emotion (~107k works), closely followed by "Fear" (~104k) — suggesting fanfiction is largely wish-fulfillment and high-stakes drama. "Disgust" is the rarest primary tone.
- **Sentiment does not strongly predict hits**: Box plots show overlapping distributions across all 8 emotions; "disgust"-tagged works show slightly higher median hits — possibly due to dark/taboo content driving curiosity.
- **Fandom temporal dynamics**: Sherlock dominated 2010–2015; My Hero Academia exploded post-2018 and peaked ~2021 (COVID effect on content creation); most fandoms show production decline post-2022.
- **Platform growth paradox** (dual-axis chart): Work volume has grown steadily since 2010, but average hits per work peaked ~2021 and is declining — more content is competing for the same reader attention.

---

### 6. Challenges & Future Work *(~0.5 page)*
**Headline:** *"Limitations and What Comes Next"*

**Challenges:**
- Tag sparsity: the tag matrix is extremely wide; correlation heatmap is only reliable for the top N tags
- Sentiment on summaries only — full body NLP would require a different scraping approach
- Rendering performance: 300k-point scatter required a sample slider to remain interactive
- NSFW classification is rating-based (not content-based), so edge cases exist

**Future work:**
- Time-series forecasting of fandom popularity peaks
- Cross-fandom tag recommendation system
- Character-level relationship network analysis
- Full-text NLP using work excerpts
- User-contributed tagging trend analysis (community signal vs. author signal)

---

## Top 3 Most Resourceful & Remarkable Charts

### 1. Fandom Landscape Shift (Stacked Area — [img/Fandom_Landscape_Shift.png](img/Fandom_Landscape_Shift.png))
The most narratively powerful chart. It shows 25 years of fandom culture compressed into a single view — Sherlock's rise and fall, MHA's explosive post-2018 growth peaking at ~40k works/year around 2021, the quiet persistence of Naruto. Each colored band is a cultural moment. This is your strongest "data story" visual.

### 2. Emotional Fingerprint Radar (Radar Chart — [img/Emotional_fingerprint.png](img/Emotional_fingerprint.png))
The most analytically distinctive chart. The spider/radar shape gives each fandom a literal "fingerprint" — trust and anticipation dominate the shape, fear juts outward, joy and disgust recede. It's the chart that can't be replicated by a bar chart and immediately communicates the collective atmosphere. Excellent for the reflection section (justifies why radar over bar for a multi-axis emotion profile).

### 3. Top Tags by Hits with Avg Hits Color Encoding (Horizontal Bar — [img/Top_tags_by_hits.png](img/Top_tags_by_hits.png))
The most analytically rich single chart. Dual encoding (bar length = total hits, color = avg hits per work) reveals the volume-vs-efficiency insight: "Fluff" and "Hurt/Comfort" dominate volume but are pale yellow (low avg hits), while niche MHA tags like "Bamf Midoriya Izuku" are deep red (high avg hits per work). This chart alone tells the most actionable finding in the project.