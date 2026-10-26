// ==============================================================================
// FILE   : frontend/src/pages/PracticeSessionPage.jsx
// STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
// ==============================================================================
//
// PURPOSE
//   Page at /practice/session/:sessionId (also handles /practice/session/new).
//
// BEHAVIOUR
//   When sessionId == 'new' read ?category and ?count, call startSession, then replace the URL with the real session id (keep the response in state).
//   If the server says no_questions show 'No questions found' with a link back to /practice (IT_07).
//   Shows one question at a time with progress (n of total), submits each answer immediately, shows AnswerFeedback, then Next. 'Finish' and 'Exit' both call finishSession (partial progress is kept, A2) and go to the result.
//   Refresh keeps working only for the starting call; do not re-create sessions on every render (guard against React StrictMode double effects).
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
