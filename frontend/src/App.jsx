// ==============================================================================
// FILE   : frontend/src/App.jsx
// STORY  : Foundation - shared scaffold (chore, no backlog issue)
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 0
// ==============================================================================
//
// PURPOSE
//   Application shell: layout, navigation and route table assembled from per-story route files.
//
// CODE TO WRITE
//   1. routeModules = import.meta.glob("./routes/*.routes.jsx", { eager: true }); routes = Object.values(routeModules).flatMap(m => m.default).
//   2. Optional pieces from story #19, resolved with import.meta.glob so a missing file does not break the build:
//        const authCtx   = import.meta.glob("./context/AuthContext.jsx",         { eager: true });  // exports AuthProvider
//        const guardMod  = import.meta.glob("./components/auth/ProtectedRoute.jsx", { eager: true }); // default export ProtectedRoute({access, children})
//      If AuthProvider exists wrap the app in it, else render children directly. If ProtectedRoute exists wrap each route element with it using route.access,
//      else render the element unguarded.
//   3. Render <NavBar /> and <Routes> with every discovered route plus "/" -> redirect to /internships and a "*" -> simple Not Found page.
//   4. Wrap content in an error boundary that shows a generic message (no stack traces in the UI, SEC-19).
//
// ROUTE OBJECT
//   { path, element, access } where access is public | authenticated | student | admin (see README contracts).
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
