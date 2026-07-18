import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/auth-context";
import { ExternalLink, MessageCircle, Waves, LogIn } from "lucide-react";
import { message } from "antd";
import request from "../services/request";

export function PublicHome() {
  const navigate = useNavigate();
  const { token, isAdmin } = useAuth();

  const handleStartConsult = async () => {
    if (token) {
      navigate("/admin");
      return;
    }
    // 未登录：自动访客登录，然后进入工作台
    try {
      const res = await request.post("/user/guest");
      const { token: guestToken, user } = res as any;
      if (guestToken && user) {
        localStorage.setItem("token", guestToken);
        localStorage.setItem("campus-qa-auth", JSON.stringify(user));
        localStorage.setItem("role", user.role);
        window.location.href = "#/admin";
        window.location.reload();
      } else {
        throw new Error("访客登录响应格式错误");
      }
    } catch (err: any) {
      message.error(err?.message || "访客登录失败，请手动登录");
      navigate("/login");
    }
  };

  const handleAdminEntry = () => {
    if (!token) {
      // 未登录去登录页
      navigate("/login");
      return;
    }
    if (!isAdmin()) {
      message.warning("您没有管理员权限");
      return;
    }
    navigate("/admin");
  };

  return (
    <div className="public-shell">
      {/* 水波纹装饰层 — 保留"水"字设计 */}
      <div className="water-ripple" aria-hidden="true">
        <div className="ripple-1" />
        <div className="ripple-2" />
        <div className="ripple-3" />
      </div>

      {/* 顶部 spacer — 自动分配空间实现垂直居中，溢出时压缩为安全边距 */}
      <div className="public-spacer" aria-hidden="true" />

      <main className="public-hero">
        <span className="public-kicker">
          <Waves size={14} />
          HOHAI UNIVERSITY · CAMPUS KNOWLEDGE
        </span>
        <h1>
          问河海，
          <br />
          从一条可靠的答案
          <br />
          开始。
        </h1>
        <p>
          连接学校公开知识与校园服务信息，为师生提供有来源、可追溯的智能问答。
        </p>
        <div className="public-actions">
          <button onClick={handleStartConsult} className="btn-primary">
            <MessageCircle size={16} />
            开始咨询
          </button>
          <button onClick={handleAdminEntry} className="btn-secondary">
            {token && isAdmin() ? (
              <>
                管理入口 <ExternalLink size={15} />
              </>
            ) : (
              <>
                <LogIn size={15} />
                管理入口
              </>
            )}
          </button>
        </div>
      </main>

      {/* 底部 spacer — 同上 */}
      <div className="public-spacer" aria-hidden="true" />

      <footer className="public-footer">
        <span>河海大学 · 智慧校园问答系统</span>
      </footer>
    </div>
  );
}
