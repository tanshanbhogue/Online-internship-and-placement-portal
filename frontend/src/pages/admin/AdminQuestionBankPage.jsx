// ==============================================================================
// FILE   : frontend/src/pages/admin/AdminQuestionBankPage.jsx
// STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
// ==============================================================================
//
// PURPOSE
//   Page at /admin/question-bank (admin only).
//
// BEHAVIOUR
//   Category tabs/select with counts, QuestionTable, 'Add question' opening QuestionForm, edit and delete flows, add-category input. Uses the adminApi functions; shows success/error via StatusMessage.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { useCallback, useEffect, useState } from "react";

import {
  adminCreateCategory, adminCreateQuestion, adminDeleteQuestion, adminGetQuestion,
  adminListCategories, adminListQuestions, adminUpdateQuestion,
} from "../../api/questionBankApi.js";
import QuestionForm from "../../components/admin/QuestionForm.jsx";
import QuestionTable from "../../components/admin/QuestionTable.jsx";
import StatusMessage from "../../components/common/StatusMessage.jsx";

const PAGE_SIZE = 20;

export default function AdminQuestionBankPage() {
  const [categories, setCategories] = useState([]);
  const [categoryId, setCategoryId] = useState(null);
  const [questions, setQuestions] = useState({ items: [], total: 0 });
  const [page, setPage] = useState(1);
  const [editing, setEditing] = useState(null); // null = closed, {} = new, question = edit
  const [newCategory, setNewCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ kind: "", text: "" });

  const fail = (err) => setMessage({ kind: "error", text: err.message || "Something went wrong" });

  const loadCategories = useCallback(async () => {
    const cats = await adminListCategories();
    setCategories(cats);
    setCategoryId((current) => current ?? cats[0]?.id ?? null);
  }, []);

  const loadQuestions = useCallback(async () => {
    if (categoryId === null) { setQuestions({ items: [], total: 0 }); return; }
    setQuestions(await adminListQuestions({ category_id: categoryId, page, page_size: PAGE_SIZE }));
  }, [categoryId, page]);

  useEffect(() => {
    loadCategories().catch(fail).finally(() => setLoading(false));
  }, [loadCategories]);

  useEffect(() => {
    loadQuestions().catch(fail);
  }, [loadQuestions]);

  async function addCategory(event) {
    event.preventDefault();
    if (!newCategory.trim()) { setMessage({ kind: "error", text: "Enter a category name" }); return; }
    try {
      const created = await adminCreateCategory(newCategory.trim());
      setNewCategory("");
      setCategoryId(created.id);
      setPage(1);
      await loadCategories();
      setMessage({ kind: "success", text: `Category "${created.name}" added` });
    } catch (err) { fail(err); }
  }

  async function openEdit(question) {
    try { setEditing(await adminGetQuestion(question.id)); } catch (err) { fail(err); }
  }

  // Throws on failure so QuestionForm can map the server's field errors onto its inputs.
  async function saveQuestion(payload) {
    if (editing && editing.id) await adminUpdateQuestion(editing.id, payload);
    else await adminCreateQuestion(payload);
    setEditing(null);
    setMessage({ kind: "success", text: "Question saved" });
    await Promise.all([loadQuestions(), loadCategories()]);
  }

  async function removeQuestion(question) {
    try {
      await adminDeleteQuestion(question.id);
      setMessage({ kind: "success", text: "Question deleted" });
      await Promise.all([loadQuestions(), loadCategories()]);
    } catch (err) { fail(err); }
  }

  const totalPages = Math.max(1, Math.ceil(questions.total / PAGE_SIZE));
  return (
    <div>
      <h1>Question Bank</h1>
      {message.text && <StatusMessage kind={message.kind} message={message.text} />}
      {loading && <StatusMessage kind="loading" message="Loading..." />}

      <form className="row" onSubmit={addCategory} style={{ marginBottom: "1rem" }}>
        <label htmlFor="new-category" className="sr-only">New category name</label>
        <input id="new-category" type="text" placeholder="New category name" maxLength={60} value={newCategory}
          onChange={(e) => setNewCategory(e.target.value)} style={{ maxWidth: "18rem" }} />
        <button className="btn btn-secondary" type="submit">Add category</button>
      </form>

      <div className="tabs" role="group" aria-label="Categories">
        {categories.map((c) => (
          <button key={c.id} type="button" className="tab" aria-pressed={c.id === categoryId}
            onClick={() => { setCategoryId(c.id); setPage(1); setEditing(null); }}>
            {c.name} ({c.question_count})
          </button>
        ))}
      </div>

      {categoryId !== null && !editing && (
        <p><button type="button" className="btn" onClick={() => setEditing({})}>Add question</button></p>
      )}

      {editing && (
        <QuestionForm
          key={editing.id || "new"}
          categories={categories}
          initial={editing.id ? editing : null}
          defaultCategoryId={categoryId}
          onSubmit={saveQuestion}
          onCancel={() => setEditing(null)}
        />
      )}

      {!loading && categoryId !== null && questions.items.length === 0 && (
        <StatusMessage kind="empty" message="No questions in this category yet." />
      )}
      {questions.items.length > 0 && (
        <>
          <QuestionTable questions={questions.items} onEdit={openEdit} onDelete={removeQuestion} />
          {totalPages > 1 && (
            <nav className="row spread" style={{ marginTop: "1rem" }} aria-label="Pagination">
              <button type="button" className="btn btn-secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>
              <span>Page {page} of {totalPages}</span>
              <button type="button" className="btn btn-secondary" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next</button>
            </nav>
          )}
        </>
      )}
    </div>
  );
}
