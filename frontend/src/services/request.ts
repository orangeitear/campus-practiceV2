import axios, { type AxiosError } from "axios";
import { message } from "antd";

const request = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

// ============================================================
// 请求拦截器：自动携带 Bearer Token
// ============================================================
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

// ============================================================
// 响应拦截器：统一解包 Result<T> + 异常处理
//
// 后端统一响应格式: { code, message, data, timestamp }
//   code=200     → 成功，返回 data 字段
//   code=400/401 → 业务错误，reject(message)
//   HTTP 401     → 未登录，清除 token 并跳转
// ============================================================
request.interceptors.response.use(
  (res) => {
    const { code, message: msg, data } = res.data;
    // 统一响应格式：有 code 字段则按标准格式解析
    if (code !== undefined) {
      if (code !== 200) {
        return Promise.reject(new Error(msg || `请求失败 (code: ${code})`));
      }
      return data;
    }
    // 非标准响应（如 health check），直接返回
    return res.data;
  },
  (err: AxiosError<{ code?: number; message?: string; detail?: string }>) => {
    // HTTP 401 — Token 过期或未登录
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      localStorage.removeItem("campus-qa-auth");
      message.error("登录已过期，请重新登录");
      // 延迟跳转，确保用户看到错误提示
      setTimeout(() => {
        window.location.href = "/login";
      }, 800);
      return Promise.reject(new Error("登录已过期，请重新登录"));
    }

    // 403 无权限
    if (err.response?.status === 403) {
      message.error("您没有权限执行此操作");
      return Promise.reject(new Error("您没有权限执行此操作"));
    }

    // 提取错误信息：优先取后端 message，其次 detail，最后兜底
    const backendMsg =
      err.response?.data?.message ||
      err.response?.data?.detail ||
      null;

    return Promise.reject(
      new Error(backendMsg || err.message || "网络请求失败，请稍后重试"),
    );
  },
);

export default request;
