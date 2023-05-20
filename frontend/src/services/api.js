import axios from "axios";

const baseUrl = window.location.protocol + "//" + window.location.host + "/api";
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFToken";
const instance = axios.create({
	baseURL: baseUrl,
  // xsrfHeaderName: 'X-CSRFToken',
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});
export default instance;
