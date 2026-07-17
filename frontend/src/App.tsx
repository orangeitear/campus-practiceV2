import { lazy, Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { AdminLayout } from "./layouts/AdminLayout";
import { GuestGuard, AdminGuard } from "./components/AuthGuard";
import { PublicHome } from "./components/PublicHome";
import { Loader } from "lucide-react";

// 懒加载管理后台页面 — 按需加载减少初始包体积
const ChatPage = lazy(() => import("./pages/ChatPage"));
const KnowledgePage = lazy(() => import("./pages/KnowledgePage"));
const UsersPage = lazy(() => import("./pages/UsersPage"));
const LoginPage = lazy(() => import("./pages/LoginPage"));
const RegisterPage = lazy(() => import("./pages/RegisterPage"));

/** 页面加载时的 fallback */
const PageFallback = () => (
  <div style={{
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    height: "60vh",
    color: "#999",
    gap: 10,
  }}>
    <Loader size={20} className="spin" />
    加载中...
  </div>
);

export default function App() {
  return (
    <Suspense fallback={<PageFallback />}>
      <Routes>
        <Route path="/" element={<PublicHome />} />
        <Route
          path="/login"
          element={
            <GuestGuard>
              <LoginPage />
            </GuestGuard>
          }
        />
        <Route
          path="/register"
          element={
            <GuestGuard>
              <RegisterPage />
            </GuestGuard>
          }
        />
        {/* 管理后台 — 仅 admin 角色可访问 */}
        <Route
          path="/admin"
          element={
            <AdminGuard>
              <AdminLayout />
            </AdminGuard>
          }
        >
          <Route index element={<ChatPage />} />
          <Route path="chat" element={<Navigate to="/admin" replace />} />
          <Route path="knowledge" element={<KnowledgePage />} />
          <Route path="users" element={<UsersPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}
