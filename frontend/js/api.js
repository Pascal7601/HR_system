const API_BASE = "http://127.0.0.1:5000/api";

const api = {
  // session handling
  // Store the access token, refresh token, and user information in localStorage
  setSession(loginResponse) {
    localStorage.setItem("access_token", loginResponse.access_token);
    localStorage.setItem("refresh_token", loginResponse.refresh_token);
    localStorage.setItem("user", JSON.stringify(loginResponse.user));
  },
  // Clear the session by removing the access token, refresh token, and user information from localStorage
  clearSession() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  },
  // Retrieve the user information from localStorage and parse it as JSON
  getUser() {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  },
  // Check if the user is logged in by verifying the presence of an access token in localStorage
  isLoggedIn() {
    return !!localStorage.getItem("access_token");
  },

  // core request helper
  async request(path, options = {}) {
    const token = localStorage.getItem("access_token");
    const headers = {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    };
    // Merge the provided options with the default headers
    const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

    // Handle 401 Unauthorized responses by clearing the session and redirecting to login
    if (response.status === 401) {
      api.clearSession();
      window.location.href = "login.html";
      throw new Error("Session expired. Please log in again.");
    }

    const body = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(body.message || "Something went wrong.");
    }

    return body;
  },

  // auth
  login(email, password) {
    return api.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  // leave
  // Fetch pending leave requests for the logged-in user
  getPendingLeaveRequests() {
    return api.request("/leave/pending");
  },
  // Fetch leave requests submitted by the logged-in user
  getMyLeaveRequests() {
    return api.request("/leave/my");
  },
  // Fetch leave requests submitted by a specific employee (requires manager role)
  submitLeaveRequest(payload) {
    return api.request("/leave", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  // Review a leave request by updating its status (requires manager role)
  reviewLeaveRequest(requestId, status) {
    return api.request(`/leave/${requestId}/review`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
  },

  // payroll
  // Fetch payslips for the logged-in user
  getMyPayslips() {
    return api.request("/payroll/my");
  },
  // Fetch payslips for a specific employee (requires manager role)
  getEmployeePayslips(employeeId) {
    return api.request(`/payroll/employee/${employeeId}`);
  },
  // Generate a payslip for an employee (requires manager role)
  generatePayslip(payload) {
    return api.request("/payroll/generate", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  // Fetch approved leave requests for a specific month and year
  getApprovedLeaveForPeriod(month, year) {
    return api.request(`/leave/approved?month=${month}&year=${year}`);
  },
};
