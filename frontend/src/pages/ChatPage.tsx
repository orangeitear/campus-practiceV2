import {
  useState,
  useRef,
  useEffect,
  useCallback,
  type KeyboardEvent,
} from "react";
import { useAuth } from "../context/auth-context";
import {
  api,
  type MessageRecord,
  type SourceRecord,
  type ConversationRecord,
} from "../api";
import { Modal, Button, message } from "antd";
import {
  Send,
  MessageSquare,
  Trash2,
  Loader,
  Sparkles,
  History,
  Square,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

const CONV_PAGE_SIZE = 10;

export function ChatPage() {
  const { token } = useAuth();
  const [conversations, setConversations] = useState<ConversationRecord[]>([]);
  const [convPage, setConvPage] = useState(1);
  const [convTotal, setConvTotal] = useState(0);
  const [currentId, setCurrentId] = useState<number | undefined>();
  const [messages, setMessages] = useState<MessageRecord[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<ConversationRecord | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  // ========== 会话列表（分页）==========
  const loadConversations = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.conversations.list(token);
      setConversations(data);
      setConvTotal(data.length);
    } catch {
      // ignore
    }
  }, [token]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // 前端分页显示会话列表
  const paginatedConversations = conversations.slice(
    (convPage - 1) * CONV_PAGE_SIZE,
    convPage * CONV_PAGE_SIZE,
  );
  const totalConvPages = Math.max(1, Math.ceil(convTotal / CONV_PAGE_SIZE));

  // ========== 自动滚动 ==========
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ========== 发送消息 ==========
  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || !token || loading) return;

    const question = input.trim();
    setInput("");
    setLoading(true);

    const userMsg: MessageRecord = {
      id: Date.now(),
      role: "USER",
      content: question,
    };
    setMessages((prev) => [...prev, userMsg]);

    // 创建 AbortController 用于停止生成
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await api.chat.stream(token, question, currentId);
      const reader = res.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      let buffer = "";
      let assistantContent = "";
      let sources: SourceRecord[] = [];
      const assistantId = Date.now() + 1;

      setMessages((prev) => [
        ...prev,
        { id: assistantId, role: "ASSISTANT", content: "", sources: [] },
      ]);

      while (true) {
        if (controller.signal.aborted) {
          reader.cancel();
          break;
        }

        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const block of lines) {
          const eventMatch = block.match(/^event: (\w+)/m);
          const dataMatch = block.match(/^data: (.+)$/m);
          if (!eventMatch || !dataMatch) continue;

          const event = eventMatch[1];
          const data = dataMatch[1];

          if (event === "meta") {
            try {
              const parsed = JSON.parse(data);
              sources = parsed.sources || [];
              if (parsed.conversation_id) {
                setCurrentId(parsed.conversation_id);
              }
            } catch { /* ignore */ }
          } else if (event === "token") {
            try {
              const parsed = JSON.parse(data);
              const text = parsed.text || "";
              assistantContent += text;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? { ...m, content: assistantContent, sources }
                    : m,
                ),
              );
            } catch { /* ignore */ }
          } else if (event === "done") {
            break;
          }
        }
      }

      await loadConversations();
    } catch (err: unknown) {
      if (controller.signal.aborted) return; // 用户主动停止，不显示错误
      message.error(err instanceof Error ? err.message : "请求失败");
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 2,
          role: "ASSISTANT",
          content: "抱歉，请求出错，请稍后重试。",
        },
      ]);
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  };

  // ========== 停止生成 ==========
  const stopGeneration = () => {
    abortRef.current?.abort();
    setLoading(false);
  };

  // ========== 键盘事件：Enter 发送，Shift+Enter 换行 ==========
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // ========== 会话操作 ==========
  const loadConversation = async (id: number) => {
    if (!token) return;
    setCurrentId(id);
    try {
      const data = await api.conversations.get(token, id);
      setMessages(
        data.messages.map((m) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          sources: m.sources || [],
        })),
      );
    } catch {
      message.error("加载会话失败");
      setMessages([]);
    }
  };

  const newChat = () => {
    setCurrentId(undefined);
    setMessages([]);
  };

  const handleDelete = async () => {
    if (!token || !deleteTarget) return;
    setDeleteLoading(true);
    try {
      await api.conversations.delete(token, deleteTarget.id);
      message.success("会话已删除");
      await loadConversations();
      if (currentId === deleteTarget.id) {
        newChat();
      }
    } catch {
      message.error("删除失败");
    } finally {
      setDeleteLoading(false);
      setDeleteTarget(null);
    }
  };

  return (
    <div className="admin-page chat-page">
      <header className="page-heading">
        <div>
          <span className="eyebrow">CAMPUS ANSWER DESK</span>
          <h1>问答工作台</h1>
          <p>验证知识检索效果，查看来源引用与连续对话表现。</p>
        </div>
        <span className="page-index">01</span>
      </header>

      <div className="chat-layout">
        {/* 会话侧边栏 */}
        <aside className="chat-sidebar">
          <div className="sidebar-header">
            <button className="btn-new-chat" onClick={newChat}>
              <MessageSquare size={16} />
              新对话
            </button>
            <span>
              <History size={14} /> 最近会话
            </span>
          </div>
          <div className="conversation-list">
            {conversations.length === 0 && (
              <div style={{ padding: "20px 12px", color: "#999", fontSize: 13, textAlign: "center" }}>
                暂无历史会话
              </div>
            )}
            {paginatedConversations.map((conv) => (
              <div
                key={conv.id}
                className={`conversation-item ${currentId === conv.id ? "active" : ""}`}
                onClick={() => loadConversation(conv.id)}
              >
                <MessageSquare size={14} />
                <span className="conv-title">{conv.title}</span>
                <button
                  className="btn-delete"
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeleteTarget(conv);
                  }}
                  title="删除会话"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            ))}
          </div>
          {/* 会话分页 */}
          {totalConvPages > 1 && (
            <div className="conv-pagination">
              <button
                disabled={convPage <= 1}
                onClick={() => setConvPage((p) => p - 1)}
              >
                <ChevronLeft size={14} />
              </button>
              <span>
                {convPage} / {totalConvPages}
              </span>
              <button
                disabled={convPage >= totalConvPages}
                onClick={() => setConvPage((p) => p + 1)}
              >
                <ChevronRight size={14} />
              </button>
            </div>
          )}
        </aside>

        {/* 聊天主区域 */}
        <main className="chat-main">
          <div className="messages">
            {/* 欢迎界面 */}
            {messages.length === 0 && !loading && (
              <div className="welcome">
                <span className="welcome-mark">
                  <Sparkles size={24} />
                </span>
                <small>HOHAI KNOWLEDGE ASSISTANT</small>
                <h2>今天想了解河海的什么？</h2>
                <p>试着询问招生、教学、校园服务，回答会标注资料来源。</p>
                <div className="examples">
                  <button onClick={() => setInput("图书馆开放时间？")}>
                    图书馆开放时间？
                  </button>
                  <button onClick={() => setInput("校园卡怎么补办？")}>
                    校园卡怎么补办？
                  </button>
                  <button onClick={() => setInput("奖学金申请条件？")}>
                    奖学金申请条件？
                  </button>
                </div>
              </div>
            )}

            {/* 消息列表 */}
            {messages.map((msg) => (
              <div key={msg.id} className={`message ${msg.role.toLowerCase()}`}>
                <div className="message-bubble">
                  <div className="message-content">
                    {msg.content || (
                      <span style={{ color: "#bbb", fontStyle: "italic" }}>
                        思考中...
                      </span>
                    )}
                  </div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources">
                      <div className="sources-title">参考来源：</div>
                      {msg.sources.map((s) => (
                        <div key={s.index} className="source-item">
                          <span className="source-index">[{s.index}]</span>
                          <span className="source-title">{s.title}</span>
                          <span className="source-score">
                            相关度: {(s.score * 100).toFixed(1)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* 加载指示器 */}
            {loading && (
              <div className="message assistant">
                <div className="message-bubble">
                  <Loader size={16} className="spin" />
                  <span style={{ marginLeft: 8 }}>AI 正在思考...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 */}
          <div className="chat-input-area">
            <textarea
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入问题，Enter 发送，Shift+Enter 换行"
              disabled={loading}
              rows={2}
            />
            <div className="chat-actions">
              {loading ? (
                <button
                  className="btn-stop"
                  onClick={stopGeneration}
                  title="停止生成"
                >
                  <Square size={16} />
                  停止
                </button>
              ) : (
                <button
                  className="btn-send"
                  onClick={() => handleSubmit()}
                  disabled={!input.trim()}
                  title="发送 (Enter)"
                >
                  <Send size={18} />
                </button>
              )}
            </div>
          </div>
        </main>
      </div>

      {/* 删除会话确认弹窗 */}
      <Modal
        title={
          <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <AlertTriangle size={18} color="#d93025" />
            确认删除会话
          </span>
        }
        open={!!deleteTarget}
        onCancel={() => setDeleteTarget(null)}
        footer={[
          <Button key="cancel" onClick={() => setDeleteTarget(null)}>
            取消
          </Button>,
          <Button
            key="delete"
            danger
            loading={deleteLoading}
            onClick={handleDelete}
            icon={<Trash2 size={14} />}
          >
            确认删除
          </Button>,
        ]}
      >
        <p>
          即将删除会话 <strong>「{deleteTarget?.title}」</strong>
          {deleteTarget?.message_count != null && (
            <>（包含 {deleteTarget.message_count} 条消息）</>
          )}
        </p>
        <p style={{ color: "#999", fontSize: 13 }}>
          此操作不可撤销，该会话的所有消息将被清除。
        </p>
      </Modal>
    </div>
  );
}
