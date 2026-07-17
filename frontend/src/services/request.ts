import axios from "axios";
import { message } from "antd";

const request = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

// Request interceptor: automatically attach Bearer token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor: unified unpack and error handling
request.interceptors.response.use(
  (res) => {
    const { code, message: msg, data } = res.data;
    if (code !== undefined && code !== 200) {
      return Promise.reject(new Error(msg || "请求失败"));
    }
    return data ?? res.data;
  },
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      localStorage.removeItem("campus-qa-auth");
      message.error("登录已过期，请重新登录");
      window.location.href = "/login";
    }
    const detail = err.response?.data?.detail;
    return Promise.reject(new Error(detail || err.message || "请求失败"));
  },
);

export default request;
