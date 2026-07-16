import { Routes, Route, Navigate } from "react-router-dom";
import { AdminLayout } from "./layouts/AdminLayout";
import { AuthGuard, GuestGuard, AdminGuard } from "./components/AuthGuard";
import { PublicHome } from "./components/PublicHome";
import { ChatPage } from "./pages/ChatPage";
import { KnowledgePage } from "./pages/KnowledgePage";
import { UsersPage } from "./pages/UsersPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";

export default function App() {
  return (
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
      <Route
        path="/admin"
        element={
          <AuthGuard>
            <AdminLayout />
          </AuthGuard>
        }
      >
        <Route index element={<ChatPage />} />
        <Route path="chat" element={<Navigate to="/admin" replace />} />
        <Route path="knowledge" element={<KnowledgePage />} />
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
  );
}
