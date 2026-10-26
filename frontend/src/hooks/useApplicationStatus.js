// ==============================================================================
// FILE   : frontend/src/hooks/useApplicationStatus.js
// STORY  : #18 Prevent Duplicate Internship Applications  [FR-002; SEC-15]
// OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 5
// ==============================================================================
//
// PURPOSE
//   React hook telling a page whether the current student already applied to a listing.
//
// EXPOSES
//   useApplicationStatus(internshipId) -> { loading, applied, status, appliedAt, error, refresh() }
//   Uses checkApplication; refresh() is called by the apply flow after a successful submit. Pure UX aid: the server still rejects duplicates (SEC-15).
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { useCallback, useEffect, useState } from "react";

import { checkApplication } from "../api/applicationCheckApi.js";

/**
 * Tells a page whether the current student already applied to a listing.
 * A UX aid only: the server still rejects duplicates (SEC-15).
 */
export function useApplicationStatus(internshipId) {
  const [state, setState] = useState({ loading: true, applied: false, status: null, appliedAt: null, error: "" });

  const load = useCallback(async () => {
    if (!internshipId) return;
    try {
      const data = await checkApplication(internshipId);
      setState({ loading: false, applied: data.applied, status: data.status, appliedAt: data.applied_at, error: "" });
    } catch (err) {
      setState({ loading: false, applied: false, status: null, appliedAt: null, error: err.message || "Something went wrong" });
    }
  }, [internshipId]);

  useEffect(() => {
    setState((s) => ({ ...s, loading: true }));
    load();
  }, [load]);

  return { ...state, refresh: load };
}

export default useApplicationStatus;
