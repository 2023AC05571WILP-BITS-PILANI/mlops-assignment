#!/bin/bash

WATCH_FILE="data/iris.csv"
COMMAND="/Users/sanjaykumarc/anaconda/anaconda3/bin/python /Users/sanjaykumarc/mlops-assignment/mlops-assignment/main.py"

echo "👀 Monitoring $WATCH_FILE for changes..."

fswatch -o "$WATCH_FILE" | while read change; do
    echo "🔄 Change detected in $WATCH_FILE. Running pipeline..."
    $COMMAND
done
