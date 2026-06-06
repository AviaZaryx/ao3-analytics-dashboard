# AO3 Analytics Dashboard

An interactive dashboard for analyzing growth, engagement, and sentiment trends in fanfiction metadata from Archive of Our Own (AO3). 

Built with **Python**, **Shiny**, and **Plotly**, this tool provides deep insights into fandom evolution, tag correlations, and the emotional "fingerprint" of work summaries.

##  Key Features
- **Tag Analysis:** Discover the most successful tags by Hits, Kudos, Bookmarks, ...
- **Fandom Distribution:** Compare SFW vs. NSFW content splits across top fandoms.
- **Sentiment Profile:** Explore the dominant emotional tones of work summaries.
- **Impact Analysis:** Interactive correlation heatmaps showing which tags drive engagement.
- **Temporal Trends:** Visualize the growth of AO3 and fandom popularity shifts over the years.
- **Word Clouds:** View word clouds of top tags for any fandom selection.
- **Works Clustering:** Use ML techniques to create a cluster map of semanically related works

##  Data Notice & Setup
Due to GitHub's file size limits, the CSV data files are hosted externally.

### 1. Download the Data
Please download the necessary files from the official Google Drive folder:
 **[AO3 Dashboard Data Storage](https://drive.google.com/drive/folders/1gELVRVWjo3ZWNs25VXb_blhPvQYJDueZ?usp=drive_link)**

### 2. File Placement
```text
data/
├── nsfw/
│   └── nsfw_works.csv           # Cleaned NSFW dataset
├── raw data/                    # Original fandom-specific scrapes
│   ├── ao3_batman.csv
│   ├── ao3_good_omens.csv
│   ├── ao3_icenfire_final.csv
│   ├── ao3_jujutsu.csv
│   ├── ao3_mha_1_to_2000.csv
│   ├── ao3_mha_2001_to_5000.csv
│   ├── ao3_middle_earth.csv
│   ├── ao3_naruto.csv
│   ├── ao3_naruto_p2.csv
│   ├── ao3_sherlock.csv
│   └── ao3_star_wars.csv
├── sfw/
│   └── sfw_works.csv            # Cleaned SFW dataset
├── cleaned_ao3_data.csv         # Cleaned dataset
├── combined_all_works.csv       # Merged datase before cleaning
├── embeddings.npy               # Vector embeddings
├── pca_coords.npy               # Reduced dimensions 
└── work_clusters.csv            # Final data with assigned cluster labels

