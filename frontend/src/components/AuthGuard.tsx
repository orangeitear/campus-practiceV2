import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/auth-context";
import type { ReactNode } from "react";

export function AuthGuard({ children }: { children: ReactNode }) {
  const { token } = useAuth();
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}

export function GuestGuard({ children }: { children: ReactNode }) {
  const { token } = useAuth();

  if (token) {
    return <Navigate to="/admin" replace />;
  }

  return <>{children}</>;
}

export function AdminGuard({ children }: { children: ReactNode }) {
  const { token, isAdmin } = useAuth();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (!isAdmin()) {
    return <Navigate to="/admin" replace />;
  }

  return <>{children}</>;
}
