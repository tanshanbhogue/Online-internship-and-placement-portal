const truncate = (text, max = 80) => (text.length > max ? `${text.slice(0, max).trimEnd()}…` : text);

// Prompts are plain text (React escapes them).
export default function QuestionTable({ questions, onEdit, onDelete }) {
  return (
    <table className="table card">
      <thead>
        <tr><th>Prompt</th><th>Type</th><th>Difficulty</th><th>Active</th><th>Actions</th></tr>
      </thead>
      <tbody>
        {questions.map((q) => (
          <tr key={q.id}>
            <td data-label="Prompt">{truncate(q.prompt)}</td>
            <td data-label="Type">{q.type}</td>
            <td data-label="Difficulty">{q.difficulty}</td>
            <td data-label="Active">{q.is_active ? "Yes" : "No"}</td>
            <td data-label="Actions">
              <div className="row">
                <button type="button" className="btn btn-secondary btn-small" onClick={() => onEdit(q)}>Edit</button>
                {q.is_active && (
                  <button
                    type="button"
                    className="btn btn-danger btn-small"
                    onClick={() => { if (window.confirm("Delete this question? Students will no longer see it.")) onDelete(q); }}
                  >
                    Delete
                  </button>
                )}
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
