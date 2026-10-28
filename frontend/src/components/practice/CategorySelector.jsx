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
