GitHub Pages deployment:
1. Upload the contents of this folder to the root of a GitHub repository.
2. Open repository Settings > Pages.
3. Choose Deploy from a branch, branch main, folder /(root), then Save.
4. Wait for GitHub Pages to publish.

Important: GitHub Pages only hosts static HTML/CSS/JavaScript. It cannot run Flask or SQLite.
This index.html is a standalone sample FAQ demo. For live shared college data, deploy the Flask backend separately and set API_BASE in index.html to its HTTPS URL. Never put a private API key in browser JavaScript or GitHub.
