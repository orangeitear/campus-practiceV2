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
 * 游客守卫 — 已登录用户重定向到工作台
 */
export function GuestGuard({ children }: { children: ReactNode }) {
  const { token } = useAuth();

  if (token) {
    return <Navigate to="/admin" replace />;
  }

  return <>{children}</>;
}

/**
 * 管理员守卫 — 仅 admin 角色可访问
 * - 无 token → /login
 * - 非 admin → /admin（工作台）并提示无权限
 */
export function AdminGuard({ children }: { children: ReactNode }) {
  const { token, isAdmin } = useAuth();
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!isAdmin()) {
    message.warning("您没有访问该模块的权限");
    return <Navigate to="/admin" replace />;
  }

  return <>{children}</>;
}
