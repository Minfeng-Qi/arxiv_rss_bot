# Output Directory

This directory stores the generated RSS feed files. The files are named with the format `YYYYMMDD_HHMMSS_CATEGORIES.xml`, where:

- `YYYYMMDD_HHMMSS`: Timestamp when the feed was generated
- `CATEGORIES`: Abbreviations of the arXiv categories included in the feed

Example: `20250101_120000_ML_AI_CV.xml` would be a feed generated on January 1, 2025 at 12:00:00 containing papers from Machine Learning, Artificial Intelligence, and Computer Vision categories.

The directory may also contain intermediate files with the prefix `arxiv_filtered_` that represent the filtered papers before the final RSS feed generation. 