import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/auth-context";
import { message } from "antd";
import type { ReactNode } from "react";

/** 已登录用户可访问（不限角色） */
export function AuthGuard({ children }: { children: ReactNode }) {
  const { token } = useAuth();
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}

/**
 * 游客守卫 — 已登录用户重定向
 * - admin → /admin（管理后台）
 * - user/guest → /（公开首页）
 */
export function GuestGuard({ children }: { children: ReactNode }) {
  const { token, isAdmin } = useAuth();

  if (token) {
    const target = isAdmin() ? "/admin" : "/";
    return <Navigate to={target} replace />;
  }

  return <>{children}</>;
}

/**
 * 管理员守卫 — 仅 admin 角色可访问
 * - 无 token → /login
 * - 非 admin → /（公开首页）并提示无权限
 */
export function AdminGuard({ children }: { children: ReactNode }) {
  const { token, isAdmin } = useAuth();
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!isAdmin()) {
    // 防止在初始加载时重复弹 toast
    if (location.pathname !== "/") {
      message.warning("您没有访问管理后台的权限");
    }
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}
