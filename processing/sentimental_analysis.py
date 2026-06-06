import pandas as pd
import os
import re
import html
from tqdm import tqdm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from nrclex import NRCLex

# Paths
DATA_DIR = r"D:\Downloads\DataVisProj2\data"
INPUT_FILE = os.path.join(DATA_DIR, "cleaned_ao3_data.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "cleaned_ao3_data.csv")


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'http\S+', '', text)
    return text.strip()


def process_chunk(chunk, analyzer):
    results = []

    emotion_list = ['fear', 'anger', 'trust', 'surprise', 'sadness', 'disgust', 'joy', 'anticipation']

    for summary in chunk['summary']:
        clean = clean_text(summary)

        row_metrics = {
            'sent_compound': 0.5,
            'sent_pos': 0.0,
            'sent_neg': 0.0,
            'sent_subjectivity': 0.0,
            'top_emotion': 'neutral'
        }

        for e in emotion_list:
            row_metrics[f'emo_{e}'] = 0.0

        if clean and len(clean) > 2:
            # 1. VADER metrics
            vs = analyzer.polarity_scores(clean)
            row_metrics['sent_compound'] = (vs['compound'] + 1) / 2
            row_metrics['sent_pos'] = vs['pos']
            row_metrics['sent_neg'] = vs['neg']

            # 2. TextBlob Subjectivity
            try:
                row_metrics['sent_subjectivity'] = TextBlob(clean).sentiment.subjectivity
            except:
                pass

            # 3. NRCLex Emotions
            try:
                emotion = NRCLex(clean)
                freqs = emotion.affect_frequencies

                for e in emotion_list:
                    val = freqs.get(e, 0.0)
                    if e == 'anticip' or e == 'anticipation':
                        val = max(freqs.get('anticip', 0), freqs.get('anticipation', 0))
                    row_metrics[f'emo_{e}'] = val

                refined = {k: v for k, v in freqs.items() if k in emotion_list}
                if refined and max(refined.values()) > 0:
                    row_metrics['top_emotion'] = max(refined, key=refined.get)
            except:
                pass

        results.append(row_metrics)

    return pd.DataFrame(results)


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"File not found: {INPUT_FILE}")
        return

    if os.path.exists(OUTPUT_FILE):
        try:
            os.rename(OUTPUT_FILE, OUTPUT_FILE)
        except OSError:
            print(f"CRITICAL: Close {OUTPUT_FILE} in Excel before running!")
            return

    print("Counting rows...")
    row_count = sum(1 for _ in open(INPUT_FILE, encoding='utf-8', errors='ignore')) - 1

    chunk_size = 2000
    analyzer = SentimentIntensityAnalyzer()

    print(f"Processing {row_count} rows. This will take longer with NRCLex enabled.")

    reader = pd.read_csv(INPUT_FILE, chunksize=chunk_size)
    first_chunk = True

    with tqdm(total=row_count, desc="Analyzing AO3 Data") as pbar:
        for chunk in reader:
            metrics_df = process_chunk(chunk, analyzer)
            combined = pd.concat([chunk.reset_index(drop=True), metrics_df], axis=1)

            if first_chunk:
                combined.to_csv(OUTPUT_FILE, index=False, mode='w', encoding='utf-8')
                first_chunk = False
            else:
                combined.to_csv(OUTPUT_FILE, index=False, mode='a', header=False, encoding='utf-8')

            pbar.update(len(chunk))

    print(f"\nSuccess! File created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()