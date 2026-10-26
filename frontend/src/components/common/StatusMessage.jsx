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
