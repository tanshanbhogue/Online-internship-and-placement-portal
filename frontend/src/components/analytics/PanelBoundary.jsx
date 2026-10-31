// Contract: <PanelBoundary title>…</PanelBoundary>   if one dashboard panel crashes only that panel is replaced by a
// generic message (never a stack trace); the rest of the dashboard keeps working.
import { Component } from "react";

export default class PanelBoundary extends Component {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch() {
    // Intentionally empty: details stay out of the UI.
  }

  render() {
    if (this.state.failed) {
      return (
        <div className="status status-error" role="alert">
          {this.props.title ? `${this.props.title} could not be shown.` : "This section could not be shown."}
        </div>
      );
    }
    return this.props.children;
  }
}
