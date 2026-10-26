FRONTEND DEPENDENCIES (package.json cannot hold comments, so the list lives here)
  Create the Vite app with:  npm create vite@latest frontend -- --template react
  dependencies   : react, react-dom, react-router-dom (v6), axios
  devDependencies: vite, @vitejs/plugin-react, eslint (optional)
  scripts        : dev -> vite ; build -> vite build ; preview -> vite preview
  Dev server     : port 5173, proxy /api to http://localhost:8000 (see vite.config.js) so cookies are same-origin.
  Owner: Foundation (Sinchana). Add a dependency only through a PR that edits package.json and this note together.
