# Trecco What's On

A phone-friendly GitHub Pages app for Trecco Bay Showdome/Showbar and Pavilion.

## Publishing

1. Upload all files and folders in this package to a public GitHub repository.
2. Open the repository's **Actions** tab.
3. Open **Update Trecco listings** and choose **Run workflow**.
4. Open **Settings → Pages**.
5. Under **Build and deployment**, choose **Deploy from a branch**.
6. Select branch **main** and folder **/(root)**, then save.

The GitHub Action refreshes both Parkdean feeds every hour and stores the JSON inside the repository. The webpage reads those same-origin files, avoiding Safari CORS restrictions.

Live feed IDs:
- Showdome / Showbar: 11
- Pavilion: 111
