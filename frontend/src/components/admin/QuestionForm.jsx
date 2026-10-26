// ==============================================================================
// FILE   : frontend/src/components/admin/QuestionForm.jsx
// STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
// ==============================================================================
//
// PURPOSE
//   Create/edit form for a question (admin).
//
// BEHAVIOUR
//   Fields: category, type (mcq/coding), prompt, difficulty, explanation; for mcq a dynamic list of 2..6 options with one 'correct' radio; for coding starter code + test cases (JSON textarea).
//   Client validation mirrors the server rules (exactly one correct option, required fields) and highlights errors (use case A1). Server 422 fields map to inputs.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
