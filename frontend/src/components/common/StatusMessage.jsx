// ==============================================================================
// FILE   : frontend/src/components/common/StatusMessage.jsx
// STORY  : Foundation - shared scaffold (chore, no backlog issue)
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 0
// ==============================================================================
//
// PURPOSE
//   Small shared component for loading, error, empty and success messages.
//
// CODE TO WRITE
//   <StatusMessage kind="loading|error|empty|success" message="..." /> with role="alert" for errors and aria-live="polite" otherwise.
//   Renders message as plain text (React escapes it; never use dangerouslySetInnerHTML, SEC-10). Used by all pages for the exact messages in the use cases.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

/**
 * <StatusMessage kind="loading|error|empty|success" message="..." />
 * The message is rendered as plain text (React escapes it). Never use dangerouslySetInnerHTML here (SEC-10).
 * Optional children (e.g. a link) are shown after the message.
 */
export default function StatusMessage({ kind = "loading", message, children }) {
  const isError = kind === "error";
  return (
    <div
      className={`status status-${kind}`}
      role={isError ? "alert" : undefined}
      aria-live={isError ? undefined : "polite"}
    >
      {message}
      {children ? <> {children}</> : null}
    </div>
  );
}
