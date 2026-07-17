import { useState, useCallback } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/auth-context";
import {
  MessageSquare,
  BookOpen,
  Users,
  LogOut,
  Menu,
  X,
  Waves,
} from "lucide-react";

type PageKey = "chat" | "knowledge" | "users";

export function AdminLayout() {
  const { token, user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const pageKey: PageKey =
    location.pathname === "/admin/knowledge"
      ? "knowledge"
      : location.pathname === "/admin/users"
        ? "users"
        : "chat";

  const navItems = [
    { key: "chat" as PageKey, label: "问答", longLabel: "问答工作台", icon: MessageSquare, path: "/admin" },
    { key: "knowledge" as PageKey, label: "知识库", longLabel: "知识库管理", icon: BookOpen, path: "/admin/knowledge" },
    ...(isAdmin()
      ? [{ key: "users" as PageKey, label: "用户", longLabel: "用户与权限", icon: Users, path: "/admin/users" }]
      : []),
  ];

  const handleLogout = useCallback(() => {
    logout();
    navigate("/login");
  }, [logout, navigate]);

  if (!token) {
    navigate("/login", { replace: true });
    return null;
  }

  return (
    <div className="admin-shell">
      <header className="admin-topbar">
        <div className="admin-brand">
          <button
            className="menu-btn"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <span className="brand-seal">
            <Waves size={24} />
          </span>
          <div>
            <strong>河海大学</strong>
            <span>校园知识管理中心</span>
          </div>
        </div>
        <div className="admin-user">
          <span className="system-state">
            <i />
            知识服务运行中
          </span>
          <div className="user-meta">
            <strong>{user?.username}</strong>
            <span>{isAdmin() ? "系统管理员" : "校园用户"}</span>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <LogOut size={17} />
            <span>退出</span>
          </button>
        </div>
      </header>

      <div className="admin-body">
        <nav className={`admin-sidebar ${sidebarOpen ? "open" : ""}`}>
          <div className="nav-caption">工作台</div>
          {navItems.map((item) => (
            <button
              key={item.key}
              className={`admin-nav-item ${pageKey === item.key ? "active" : ""}`}
              onClick={() => {
                navigate(item.path);
                setSidebarOpen(false);
              }}
            >
              <item.icon size={18} />
              <span>{item.longLabel}</span>
              <i />
            </button>
          ))}
          <div className="sidebar-note">
            <span>HHU · AI</span>
            <p>让校园信息更容易被找到，也更值得信赖。</p>
          </div>
        </nav>

        <main className="admin-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
