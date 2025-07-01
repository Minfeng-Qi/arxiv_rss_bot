# Cache Directory

This directory stores cache files used by the application to improve performance:

1. `author_cache.json`: Caches author information to reduce API calls to scholarly services.
2. `scholar_cache.sqlite`: SQLite database used for caching scholarly article information.

These files are automatically generated and managed by the application. They should not be committed to version control.

The cache helps reduce the number of external API calls and speeds up repeated queries for the same information. 