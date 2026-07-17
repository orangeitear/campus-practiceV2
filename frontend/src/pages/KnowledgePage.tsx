import { useState, useEffect, useCallback, useRef, type FormEvent } from "react";
import { useAuth } from "../context/auth-context";
import { api, type DocumentRecord } from "../api";
import { Modal, message, Tag, Button, Input } from "antd";
import {
  Upload,
  FileText,
  Trash2,
  RefreshCw,
  Loader,
  Database,
  Layers3,
  CircleCheck,
  Search,
  AlertTriangle,
} from "lucide-react";

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const ALLOWED_TYPES = [".pdf", ".doc", ".docx", ".txt"];
const ALLOWED_LABEL = "PDF / Word / TXT";

/** 处理状态映射 */
const STATUS_MAP: Record<string, { label: string; color: string }> = {
  PENDING: { label: "待处理", color: "gold" },
  PROCESSING: { label: "处理中", color: "blue" },
  READY: { label: "已完成", color: "green" },
  FAILED: { label: "处理失败", color: "red" },
};

const PROCESSING_STATUSES = ["PENDING", "PROCESSING"];
const POLL_INTERVAL = 3000; // 3s 轮询

export function KnowledgePage() {
  const { token, isAdmin } = useAuth();
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [query, setQuery] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<DocumentRecord | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ========== 数据加载 ==========
  const loadDocuments = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await api.documents.list(token);
      setDocuments(data);
    } catch {
      message.error("加载文档列表失败");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  // ========== 处理状态轮询 (3s) ==========
  useEffect(() => {
    const hasProcessing = documents.some((d) =>
      PROCESSING_STATUSES.includes(d.status),
    );

    if (hasProcessing && !pollTimerRef.current) {
      pollTimerRef.current = setInterval(() => {
        loadDocuments();
      }, POLL_INTERVAL);
    } else if (!hasProcessing && pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }

    return () => {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
      }
    };
  }, [documents, loadDocuments]);

  // ========== 文件上传 ==========
  const handleUpload = async (e: FormEvent) => {
    e.preventDefault();
    if (!file || !title.trim() || !token) return;

    // 客户端文件大小验证
    if (file.size > MAX_FILE_SIZE) {
      message.error(`文件不能超过 50MB，当前文件大小 ${formatSize(file.size)}`);
      return;
    }

    // 客户端文件类型验证
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!ALLOWED_TYPES.includes(ext)) {
      message.error(`仅支持 ${ALLOWED_LABEL} 格式`);
      return;
    }

    setUploading(true);
    try {
      await api.documents.upload(token, title.trim(), file);
      message.success("文档上传成功，正在处理中...");
      setTitle("");
      setFile(null);
      await loadDocuments();
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "上传失败");
    } finally {
      setUploading(false);
    }
  };

  // ========== 删除文档 ==========
  const handleDelete = async () => {
    if (!token || !deleteTarget) return;
    setDeleteLoading(true);
    try {
      await api.documents.delete(token, deleteTarget.id);
      message.success(`已删除「${deleteTarget.title}」`);
      await loadDocuments();
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "删除失败");
    } finally {
      setDeleteLoading(false);
      setDeleteTarget(null);
    }
  };

  // ========== 重新处理 ==========
  const handleReprocess = async (id: number) => {
    if (!token) return;
    try {
      await api.documents.reprocess(token, id);
      message.success("已触发重新处理");
      await loadDocuments();
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "重新处理失败");
    }
  };

  // ========== 工具函数 ==========
  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const visibleDocuments = documents.filter((doc) =>
    `${doc.title} ${doc.filename}`.toLowerCase().includes(query.toLowerCase()),
  );
  const readyCount = documents.filter((d) => d.status === "READY").length;
  const processingCount = documents.filter((d) =>
    PROCESSING_STATUSES.includes(d.status),
  ).length;
  const chunkCount = documents.reduce((sum, doc) => sum + doc.chunk_count, 0);

  // ========== 非管理员提示 ==========
  if (!isAdmin()) {
    return (
      <div className="admin-page">
        <header className="page-heading">
          <div>
            <span className="eyebrow">KNOWLEDGE ARCHIVE</span>
            <h1>知识库管理</h1>
          </div>
        </header>
        <div style={{ textAlign: "center", padding: "80px 0", color: "#999" }}>
          <Database size={48} style={{ marginBottom: 16, opacity: 0.3 }} />
          <p style={{ fontSize: 16 }}>只有管理员可以管理知识库文档</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-page">
      {/* 页面标题 */}
      <header className="page-heading">
        <div>
          <span className="eyebrow">KNOWLEDGE ARCHIVE</span>
          <h1>知识库管理</h1>
          <p>维护校园知识来源，追踪文档处理与索引状态。</p>
        </div>
        <span className="page-index">02</span>
      </header>

      {/* 统计指标 */}
      <section className="metric-strip">
        <div>
          <Database size={20} />
          <span>
            <b>{documents.length}</b>资料总数
          </span>
        </div>
        <div>
          <CircleCheck size={20} />
          <span>
            <b>{readyCount}</b>可检索
          </span>
        </div>
        <div>
          <Layers3 size={20} />
          <span>
            <b>{chunkCount.toLocaleString()}</b>知识片段
          </span>
        </div>
      </section>

      {/* 上传表单 */}
      <form className="upload-form" onSubmit={handleUpload}>
        <div className="section-title">
          <div>
            <span>资料入库</span>
            <h2>添加新的知识来源</h2>
          </div>
          <p>
            支持 {ALLOWED_LABEL} 格式，单文件不超过 50MB
            {processingCount > 0 && (
              <span style={{ color: "var(--river)", marginLeft: 8 }}>
                · {processingCount} 个文件处理中...
              </span>
            )}
          </p>
        </div>
        <div className="upload-row">
          <input
            type="text"
            placeholder="输入资料标题，例如：本科生奖学金管理办法"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <label className="file-picker">
            <FileText size={18} />
            <span>{file ? file.name : "选择资料文件"}</span>
            <input
              type="file"
              accept={ALLOWED_TYPES.join(",")}
              onChange={(e) => {
                const f = e.target.files?.[0] || null;
                if (f && f.size > MAX_FILE_SIZE) {
                  message.error(`文件过大（${formatSize(f.size)}），上限 50MB`);
                  return;
                }
                setFile(f);
              }}
              required
            />
          </label>
          <button type="submit" disabled={uploading}>
            <Upload size={16} />
            {uploading ? "上传中..." : "上传"}
          </button>
        </div>
      </form>

      {/* 搜索工具栏 */}
      <div className="list-toolbar">
        <div>
          <h2>资料目录</h2>
          <span>共 {documents.length} 条记录</span>
        </div>
        <Input
          prefix={<Search size={16} />}
          placeholder="搜索标题或文件名"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ width: 240 }}
          allowClear
        />
      </div>

      {/* 加载状态 */}
      {loading && documents.length === 0 ? (
        <div className="loading">
          <Loader size={24} className="spin" /> 加载中...
        </div>
      ) : (
        <div className="document-list">
          {/* 空状态 */}
          {visibleDocuments.length === 0 && (
            <div className="empty" style={{ textAlign: "center", padding: "60px 0" }}>
              <FileText size={48} style={{ color: "#ccc", marginBottom: 12 }} />
              <p style={{ color: "#999", fontSize: 15 }}>
                {query ? "没有找到匹配的资料" : "还没有上传任何知识资料"}
              </p>
              {!query && (
                <p style={{ color: "#bbb", fontSize: 13, marginTop: 4 }}>
                  上传 PDF、Word 或 TXT 文档来构建校园知识库
                </p>
              )}
            </div>
          )}

          {/* 文档列表 */}
          {visibleDocuments.map((doc) => {
            const statusInfo = STATUS_MAP[doc.status] || {
              label: doc.status,
              color: "default",
            };
            return (
              <div key={doc.id} className="document-card">
                <div className="doc-info">
                  <span className="doc-icon">
                    <FileText size={19} />
                  </span>
                  <div className="doc-meta">
                    <span className="doc-title">{doc.title}</span>
                    <span className="doc-detail">
                      {doc.filename} · {formatSize(doc.size)} ·{" "}
                      {doc.chunk_count} 片段
                    </span>
                  </div>
                  <Tag color={statusInfo.color}>
                    {doc.status === "PROCESSING" && (
                      <Loader size={12} className="spin" style={{ marginRight: 4 }} />
                    )}
                    {statusInfo.label}
                  </Tag>
                </div>
                <div className="doc-actions">
                  <button
                    onClick={() => handleReprocess(doc.id)}
                    title="重新处理"
                    disabled={doc.status === "PROCESSING"}
                  >
                    <RefreshCw
                      size={14}
                      className={doc.status === "PROCESSING" ? "spin" : ""}
                    />
                  </button>
                  <button
                    onClick={() => setDeleteTarget(doc)}
                    title="删除"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
                {doc.error && (
                  <div className="doc-error">
                    <AlertTriangle size={12} style={{ marginRight: 4 }} />
                    {doc.error}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* 删除确认弹窗 */}
      <Modal
        title={
          <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <AlertTriangle size={18} color="#d93025" />
            确认删除文档
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
          即将<strong style={{ color: "#d93025" }}>永久删除</strong>文档
          <strong>「{deleteTarget?.title}」</strong>
          （{deleteTarget?.filename}）
        </p>
        <p style={{ color: "#999", fontSize: 13 }}>
          此操作将同时删除文档记录、向量数据和存储文件，不可撤销。
        </p>
      </Modal>
    </div>
  );
}
