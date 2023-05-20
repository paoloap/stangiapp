import axiosInstance from "./api";
import TokenService from "./token.service";
import { refreshToken } from "../actions/auth";
const setup = (store) => {
  axiosInstance.interceptors.request.use(
    (config) => {
      const token = TokenService.getLocalAccessToken();
      if (token && config.url !== '/refresh_token' && config.url !== '/login') {
        config.headers["Authorization"] = 'Token ' + token;  // for Spring Boot back-end
        if (config.method === "put" || (config.method === "post" && config.url !== "/login" )) {
          config.headers['X-CSRFToken'] = TokenService.getLocalCsrfToken();
        }
        // config.headers["x-access-token"] = token; // for Node.js Express back-end
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );
  const { dispatch } = store;
  axiosInstance.interceptors.response.use(
    (res) => {
      return res;
    },
    async (err) => {
      const originalConfig = err.config;
      if (originalConfig.url !== "/login" && err.response) {
        // Access Token was expired
        if (
          err.response.status === 403 && (
            err.response.data.detail ==="Non sono state immesse le credenziali di autenticazione." ||
            err.response.data.detail === "access_token expired"
          ) && !originalConfig._retry
        ) {
          try {
            const rs = await axiosInstance.post("/refresh_token", {
              headers: {
                'X-CSRFToken': TokenService.getLocalCsrfToken(),
                //"Referer": "https://stangiapp.porcedda.com"
              },
              refreshtoken: TokenService.getLocalRefreshToken(),
            });
            const { access_token } = rs.data;
            dispatch(refreshToken(access_token));
            TokenService.updateLocalAccessToken(access_token);
            return axiosInstance(originalConfig);
          } catch (_error) {
            return Promise.reject(_error);
          }
        }
      }
      return Promise.reject(err);
    }
  );
};
export default setup;
