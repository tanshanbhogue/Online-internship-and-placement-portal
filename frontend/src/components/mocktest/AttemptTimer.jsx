// Story #24 Automatic Test Submission - owner: Eshwar (ESHWAR1024)
// File: frontend/src/components/mocktest/AttemptTimer.jsx
//
// Contract
//   <AttemptTimer secondsLeft={number} />   visible mm:ss countdown (UT_12). Screen readers hear it only at
//   5 min, 1 min and 10 s, not every second. Under 1 minute it also shows the words "Time is running out".
import "../../styles/mock-timer.css";

function format(total) {
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function announcement(secondsLeft) {
  if (secondsLeft === 300) return "5 minutes remaining";
  if (secondsLeft === 60) return "1 minute remaining";
  if (secondsLeft === 10) return "10 seconds remaining";
  if (secondsLeft === 0) return "Time is up";
  return null;
}

export default function AttemptTimer({ secondsLeft }) {
  const level = secondsLeft <= 10 ? "critical" : secondsLeft <= 60 ? "low" : "ok";
  const spoken = announcement(secondsLeft);
  return (
    <div className={`attempt-timer attempt-timer-${level}`} data-testid="attempt-timer">
      <span className="attempt-timer-label">Time left</span>
      <span className="attempt-timer-value" role="timer" aria-label="Time left">{format(secondsLeft)}</span>
      {level !== "ok" && <span className="attempt-timer-warning">Time is running out</span>}
      <span className="sr-only" aria-live="polite">{spoken}</span>
    </div>
  );
}
