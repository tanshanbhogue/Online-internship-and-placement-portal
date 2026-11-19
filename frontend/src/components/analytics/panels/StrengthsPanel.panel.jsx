import { useEffect, useState } from "react";

import { getStrengthsWeaknesses } from "../../../api/insightsApi.js";
import StatusMessage from "../../common/StatusMessage.jsx";
import FocusAreas from "../FocusAreas.jsx";
import StrengthsWeaknesses from "../StrengthsWeaknesses.jsx";

function StrengthsPanel({ filters, refreshKey }) {
  const [state, setState] = useState({ loading: true, error: "", data: null });

  useEffect(() => {
    let cancelled = false;
    getStrengthsWeaknesses(filters)
      .then((data) => !cancelled && setState({ loading: false, error: "", data }))
      .catch((err) => !cancelled && setState({ loading: false, error: err.message || "Something went wrong", data: null }));
    return () => {
      cancelled = true;
    };
  }, [filters, refreshKey]);

  const { loading, error, data } = state;
  return (
    <section aria-labelledby="strengths-heading">
      <h2 id="strengths-heading">Strengths and weaknesses</h2>
      {loading && !data && <StatusMessage kind="loading" message="Loading..." />}
      {error && <StatusMessage kind="error" message={error} />}
      {data && data.has_data && (
        <>
          <StrengthsWeaknesses data={data} />
          <h3>Recommended focus areas</h3>
          <FocusAreas areas={data.focus_areas} />
        </>
      )}
    </section>
  );
}

export default { id: "strengths", order: 20, title: "Strengths and weaknesses", Component: StrengthsPanel };
