# A-Level German Current Affairs Hub

This is a static HTML tool for GitHub Pages.

It is designed to:
- pull recent German-language articles from RSS feeds
- classify them into AQA A-level German themes and sub-topics
- publish the site automatically every day through GitHub Actions
- be embedded into Google Sites

## File structure

- `index.html` → main page
- `styles.css` → styling
- `app.js` → front-end logic
- `data/topics.json` → AQA themes, sub-topics, keyword map
- `data/articles.json` → generated article data
- `scripts/update_articles.py` → daily updater
- `.github/workflows/update-and-deploy.yml` → scheduled workflow and Pages deployment
- `.nojekyll` → prevents Jekyll processing on GitHub Pages

## Quick setup

1. Create a new GitHub repository.
2. Upload every file in this folder, keeping the folder structure exactly the same.
3. In GitHub, go to **Settings → Pages**.
4. Under **Build and deployment**, choose **GitHub Actions**.
5. Go to **Actions** and run **Update and deploy A-Level German hub** once manually.
6. Wait for the workflow to finish.
7. Go back to **Settings → Pages** and open the site URL.
8. In Google Sites, use **Insert → Embed** and paste the GitHub Pages URL.

## Important note

The workflow updates and deploys the site each day. The published site updates from the workflow artifact, not from a manual Git commit.

## Changing the update time

Open `.github/workflows/update-and-deploy.yml` and change:

```yml
schedule:
  - cron: '10 6 * * *'
    timezone: 'Europe/London'
```

That currently means **06:10 London time every day**.

## If the site looks empty

Run the workflow manually from **Actions** first. Some feeds may occasionally return no matching articles for the specification keyword map.
