# AO3 Analytics Dashboard



An interactive dashboard for analyzing growth, engagement, and sentiment trends in fanfiction metadata from Archive of Our Own (AO3). 



Built with \*\*Python\*\*, \*\*Shiny\*\*, and \*\*Plotly\*\*, this tool provides deep insights into fandom evolution, tag correlations, and the emotional "fingerprint" of work summaries.



## Key Features

- \*\*Tag Analysis:\*\* Discover the most successful tags by Hits, Kudos, and Bookmarks.

- \*\*Fandom Distribution:\*\* Compare SFW vs. NSFW content splits across top fandoms.

- \*\*Sentiment Profile:\*\* Explore the dominant tones and emotional intensity of work summaries.

- \*\*Impact Analysis:\*\* Interactive correlation heatmaps showing which tags drive engagement.

- \*\*Temporal Trends:\*\* Visualize the growth of AO3 and fandom popularity shifts over 15+ years.

- \*\*High-Res Word Clouds:\*\* Generate and view interactive 4K word clouds for any fandom selection.



## 💾 Data Notice \& Setup

Due to GitHub's file size limits (the total dataset is \~3.2GB), the CSV data files are hosted externally.



### 1. Download the Data

Please download the necessary files from the official Google Drive folder:

*\*\[AO3 Dashboard Data Storage](https://drive.google.com/drive/folders/1gELVRVWjo3ZWNs25VXb\_blhPvQYJDueZ?usp=drive\_link)\*\*



### 2. File Placement

To run the dashboard locally, place the downloaded files in the following directory structure:

```text

/data/

&#x20; └── cleaned\_ao3\_data.csv

/data/nsfw/

&#x20; └── nsfw\_works.csv

