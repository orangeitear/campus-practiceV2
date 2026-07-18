import { Suspense, lazy } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { GuestGuard, AdminGuard } from "./components/AuthGuard";

// ── 立即加载（首屏必需）──
import { PublicHome } from "./components/PublicHome";
import { AdminLayout } from "./layouts/AdminLayout";

// ── 按需加载（代码分割）──
const LoginPage = lazy(() =>
  import("./pages/LoginPage").then((m) => ({ default: m.LoginPage }))
);
const RegisterPage = lazy(() =>
  import("./pages/RegisterPage").then((m) => ({ default: m.RegisterPage }))
);
const ChatPage = lazy(() =>
  import("./pages/ChatPage").then((m) => ({ default: m.ChatPage }))
);
const KnowledgePage = lazy(() =>
  import("./pages/KnowledgePage").then((m) => ({ default: m.KnowledgePage }))
);
const UsersPage = lazy(() =>
  import("./pages/UsersPage").then((m) => ({ default: m.UsersPage }))
);

/** 统一的加载占位 */
function PageLoader() {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "300px",
        gap: "16px",
        color: "var(--c-text-3)",
        animation: "fade-in .3s ease",
      }}
    >
      <div
        style={{
          width: "32px",
          height: "32px",
          border: "3px solid var(--c-border)",
          borderTopColor: "var(--c-accent)",
          borderRadius: "50%",
          animation: "spin .7s linear infinite",
        }}
      />
      <span style={{ fontSize: "13px" }}>加载中...</span>
    </div>
  );
}

export default function App() {
  return (
    <Suspense fallback={<PageLoader />}>
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
        {/* 工作台 — 任何人可访问（问答），管理子路由需权限 */}
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<ChatPage />} />
          <Route path="chat" element={<Navigate to="/admin" replace />} />
          <Route
            path="knowledge"
            element={
              <AdminGuard>
                <KnowledgePage />
              </AdminGuard>
            }
          />
          <Route
            path="users"
            element={
              <AdminGuard>
                <UsersPage />
              </AdminGuard>
            }
          />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}
