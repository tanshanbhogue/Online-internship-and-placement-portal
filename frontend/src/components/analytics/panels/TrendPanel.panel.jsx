import { useEffect, useState } from "react";

import { getTrends } from "../../../api/insightsApi.js";
import StatusMessage from "../../common/StatusMessage.jsx";
import TrendChart from "../TrendChart.jsx";

const DIRECTION = {
  improving: "Improving: your recent scores are higher than before.",
  declining: "Declining: your recent scores are lower than before.",
  steady: "Steady: your scores are holding at about the same level.",
  not_enough_data: "Complete at least 3 attempts to see the direction of your trend.",
};

function TrendPanel({ filters, refreshKey }) {
  const [state, setState] = useState({ loading: true, error: "", data: null });

  useEffect(() => {
    let cancelled = false;
    getTrends(filters)
      .then((data) => !cancelled && setState({ loading: false, error: "", data }))
      .catch((err) => !cancelled && setState({ loading: false, error: err.message || "Something went wrong", data: null }));
    return () => {
      cancelled = true;
    };
  }, [filters, refreshKey]);

  const { loading, error, data } = state;
  return (
    <section aria-labelledby="trend-heading">
      <h2 id="trend-heading">Performance trend</h2>
      {loading && !data && <StatusMessage kind="loading" message="Loading trend..." />}
      {error && <StatusMessage kind="error" message={error} />}
      {data && !data.has_data && <StatusMessage kind="empty" message="No attempts in this period" />}
      {data && data.has_data && (
        <div className="card">
          <p data-testid="trend-direction" data-direction={data.direction}><strong>{DIRECTION[data.direction]}</strong></p>
          <TrendChart points={data.points} />
        </div>
      )}
    </section>
  );
}

export default { id: "trend", order: 10, title: "Performance trend", Component: TrendPanel };
