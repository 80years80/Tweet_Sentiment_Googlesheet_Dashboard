#!/usr/bin/env python3
"""Convert TweetClaw exports into the polarity,tweet CSV used by this project."""

import argparse
import csv
import json
from pathlib import Path

TEXT_COLUMNS = ("tweet", "text", "full_text", "content", "rawContent")
SENTIMENT_COLUMNS = ("polarity", "sentiment", "sentiment_label", "label")


def normalize_name(value):
    return value.lower().replace(" ", "").replace("-", "").replace("_", "")


def pick_column(row, candidates):
    normalized = {normalize_name(column): column for column in row}
    for candidate in candidates:
        source = normalized.get(normalize_name(candidate))
        if source:
            return source
    return None


def load_rows(input_path):
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        with input_path.open(newline="", encoding="utf-8-sig") as csv_file:
            return list(csv.DictReader(csv_file))
    if suffix in {".jsonl", ".ndjson"}:
        with input_path.open(encoding="utf-8") as jsonl_file:
            return [json.loads(line) for line in jsonl_file if line.strip()]
    if suffix == ".json":
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return payload
        for key in ("tweets", "data", "items", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    raise ValueError("Input must be a TweetClaw CSV, JSON, JSONL, or NDJSON export.")


def label_to_polarity(value):
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized in {"positive", "pos", "4", "1", "1.0"}:
        return 1.0
    if normalized in {"neutral", "neu", "2", "0", "0.0"}:
        return 0.0
    if normalized in {"negative", "neg", "-1", "-1.0"}:
        return -1.0
    return None


def textblob_polarity(text):
    try:
        from textblob import TextBlob
    except ImportError as exc:
        raise ValueError(
            "No sentiment column found. Install textblob or export a sentiment column."
        ) from exc
    return TextBlob(text).sentiment.polarity


def convert_rows(rows):
    if not rows:
        raise ValueError("TweetClaw export did not contain rows.")

    text_column = pick_column(rows[0], TEXT_COLUMNS)
    if not text_column:
        raise ValueError("TweetClaw export needs a tweet text column.")

    sentiment_column = pick_column(rows[0], SENTIMENT_COLUMNS)
    converted = []
    skipped = 0
    for row in rows:
        tweet = str(row.get(text_column, "")).strip()
        if not tweet:
            skipped += 1
            continue
        polarity = label_to_polarity(row.get(sentiment_column)) if sentiment_column else None
        if polarity is None:
            polarity = textblob_polarity(tweet)
        converted.append({"polarity": polarity, "tweet": tweet})

    if not converted:
        raise ValueError("TweetClaw export did not contain usable tweet text.")
    return converted, skipped


def write_rows(output_path, rows):
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=("polarity", "tweet"))
        writer.writeheader()
        writer.writerows(rows)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert a TweetClaw export into this project's Kaggle CSV schema."
    )
    parser.add_argument("input", type=Path, help="TweetClaw CSV, JSON, JSONL, or NDJSON export")
    parser.add_argument("output", type=Path, help="Output CSV with polarity,tweet columns")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        converted, skipped = convert_rows(load_rows(args.input))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    write_rows(args.output, converted)
    print(f"Wrote {len(converted)} rows to {args.output}; skipped {skipped} blank rows.")


if __name__ == "__main__":
    main()
