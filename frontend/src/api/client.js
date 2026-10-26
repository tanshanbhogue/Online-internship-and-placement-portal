import axios from "axios";

export class ApiError extends Error {
  constructor({ status = 0, code = "error", message = "Something went wrong", fields = {} } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.fields = fields || {};
  }
}

// The one axios instance. No tokens are stored anywhere: the HttpOnly cookie is the credential.
const client = axios.create({
  baseURL: "/api",
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const response = error.response;
    if (!response) {
      return Promise.reject(new ApiError({ status: 0, code: "network_error", message: "Something went wrong" }));
    }
    const body = response.data && typeof response.data === "object" ? response.data : {};
    const apiError = new ApiError({
      status: response.status,
      code: body.code || "error",
      message: typeof body.detail === "string" ? body.detail : "Something went wrong",
      fields: body.fields || {},
    });

    // An expired/invalid session mid-use sends the user to /login. The login call itself and the
    // session probe (/auth/me, used on page load) are expected to 401 and are not "expiry".
    const url = error.config?.url || "";
    const isSessionProbe = url.includes("/auth/login") || url.includes("/auth/me");
    if (response.status === 401 && apiError.code === "not_authenticated" && !isSessionProbe) {
      window.dispatchEvent(new Event("auth:expired"));
    }
    return Promise.reject(apiError);
  }
);

export default client;
