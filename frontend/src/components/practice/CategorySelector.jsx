// ==============================================================================
// FILE   : frontend/src/components/practice/CategorySelector.jsx
// STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
// ==============================================================================
//
// PURPOSE
//   Selectable list/cards of practice categories.
//
// BEHAVIOUR
//   props { categories, selectedId, onSelect }. Shows name + question count; categories with 0 questions are still selectable but show 'No questions yet' (so IT_07 can be exercised). Keyboard accessible radio-group semantics.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

// Native radio inputs give keyboard support (arrow keys, space) and radio-group semantics for free.
export default function CategorySelector({ categories, selectedId, onSelect }) {
  return (
    <fieldset className="category-grid" style={{ border: "none", padding: 0 }}>
      <legend className="sr-only">Practice category</legend>
      {categories.map((c) => (
        <label key={c.id} className="category-option">
          <input type="radio" name="category" value={c.id} checked={selectedId === c.id} onChange={() => onSelect(c.id)} />
          <span>
            <strong>{c.name}</strong>
            <br />
            <span className="muted small">
              {c.question_count > 0 ? `${c.question_count} ${c.question_count === 1 ? "question" : "questions"}` : "No questions yet"}
            </span>
          </span>
        </label>
      ))}
    </fieldset>
  );
}
