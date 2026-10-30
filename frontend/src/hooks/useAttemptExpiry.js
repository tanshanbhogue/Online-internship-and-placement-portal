// Story #24 Automatic Test Submission - owner: Eshwar (ESHWAR1024)
// File: frontend/src/hooks/useAttemptExpiry.js
//
// A countdown that is anchored to the SERVER's "remaining_seconds" and advanced with performance.now()
// (monotonic), so changing the computer clock or refreshing the page can neither extend nor reset it (SEC-13).
// At zero it asks the server to auto-submit; the server decides (it answers 409 "not_expired" if the browser ran fast).
//
// Contract
//   useAttemptExpiry({ attemptId, remainingSeconds, syncKey, enabled, onAutoSubmitted, onResync })
//     remainingSeconds  seconds left according to the server at the moment of the last fetch
//     syncKey           anything that changes on every fetch (e.g. the attempt's server_time) so equal values re-anchor
//     enabled           false once the attempt is closed
//     onAutoSubmitted   (response) => void   called once when the server has closed the attempt
//     onResync          () => Promise<void>  re-fetch the attempt; called every 30 s, when the tab becomes visible
//                                            again, and after a "not_expired" answer
//   returns { secondsLeft, phase: "running" | "finalizing" | "done" | "error", error, retry }
import { useCallback, useEffect, useRef, useState } from "react";

import { requestAutoSubmit } from "../api/autoSubmitApi.js";

const TICK_MS = 250;
const RESYNC_MS = 30000;
const MAX_NOT_EXPIRED_RETRIES = 5;

export default function useAttemptExpiry({ attemptId, remainingSeconds, syncKey, enabled = true, onAutoSubmitted, onResync }) {
  const [secondsLeft, setSecondsLeft] = useState(remainingSeconds ?? 0);
  const [phase, setPhase] = useState("running");
  const [error, setError] = useState("");

  const anchor = useRef({ at: performance.now(), remaining: remainingSeconds ?? 0 });
  const fired = useRef(false);
  const retries = useRef(0);
  const latest = useRef({});
  latest.current = { attemptId, enabled, onAutoSubmitted, onResync };

  // Re-anchor every time the server tells us the remaining time again.
  useEffect(() => {
    anchor.current = { at: performance.now(), remaining: remainingSeconds ?? 0 };
    fired.current = false;
    setSecondsLeft(remainingSeconds ?? 0);
    setPhase("running");
    setError("");
  }, [remainingSeconds, syncKey, attemptId]);

  const fire = useCallback(async () => {
    fired.current = true;
    setPhase("finalizing");
    try {
      const response = await requestAutoSubmit(latest.current.attemptId);
      setPhase("done");
      latest.current.onAutoSubmitted?.(response);
    } catch (err) {
      if (err.code === "not_expired" && retries.current < MAX_NOT_EXPIRED_RETRIES) {
        retries.current += 1;
        if (latest.current.onResync) {
          await latest.current.onResync(); // new remainingSeconds re-anchors the clock (effect above)
        } else {
          anchor.current = { at: performance.now(), remaining: 1 };
        }
        fired.current = false;
        setPhase("running");
        return;
      }
      setError(err.message || "Something went wrong");
      setPhase("error");
    }
  }, []);

  // Tick.
  useEffect(() => {
    if (!enabled) return undefined;
    const id = setInterval(() => {
      const elapsed = (performance.now() - anchor.current.at) / 1000;
      const left = Math.max(0, Math.ceil(anchor.current.remaining - elapsed));
      setSecondsLeft(left);
      if (left === 0 && !fired.current) fire();
    }, TICK_MS);
    return () => clearInterval(id);
  }, [enabled, fire]);

  // Keep the anchor honest: periodically, and whenever a hidden/sleeping tab comes back.
  useEffect(() => {
    if (!enabled) return undefined;
    const resync = () => latest.current.onResync?.();
    const id = setInterval(resync, RESYNC_MS);
    const onVisible = () => document.visibilityState === "visible" && resync();
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      clearInterval(id);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [enabled]);

  const retry = useCallback(() => {
    retries.current = 0;
    fired.current = false;
    setError("");
    setPhase("running");
  }, []);

  return { secondsLeft, phase, error, retry };
}
