// ==============================================================================
// FILE   : frontend/src/pages/PracticeHomePage.jsx
// STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
// ==============================================================================
//
// PURPOSE
//   Page at /practice: choose a category and start practising.
//
// BEHAVIOUR
//   Loads listCategories, renders CategorySelector, optional difficulty and question-count controls, and a 'Start practice' button.
//   Start button navigates to `/practice/session/new?category=<id>&count=<n>` (a URL, NOT an import): story #22's PracticeSessionPage creates the session.
//   Selecting a different category before starting simply changes the target (ST_06). Also link to /practice/history.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
