import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth } from "../context/auth-context";
import { api, type DocumentRecord } from "../api";
import {
  Modal,
  message,
  Tag,
  Button,
  Input,
  Upload,
  Steps,
  Progress,
  Checkbox,
} from "antd";
import type { UploadFile, RcFile } from "antd/es/upload/interface";
import {
  FileText,
  Trash2,
  RefreshCw,
  Loader,
  Database,
  Layers3,
  CircleCheck,
  Search,
  AlertTriangle,
  Upload as UploadIcon,
  Eye,
  Download,
  File as FileIcon,
  Inbox,
} from "lucide-react";

const { Dragger } = Upload;

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const ALLOWED_TYPES = [".pdf", ".doc", ".docx", ".txt"];
const ALLOWED_MIME = [
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text/plain",
];
const ALLOWED_LABEL = "PDF / Word / TXT";

/** 处理状态 */
const STATUS_MAP: Record<string, { label: string; color: string }> = {
  PENDING: { label: "待处理", color: "gold" },
  PROCESSING: { label: "处理中", color: "blue" },
  READY: { label: "已完成", color: "green" },
  FAILED: { label: "处理失败", color: "red" },
};
const PROCESSING_STATUSES = ["PENDING", "PROCESSING"];
const POLL_INTERVAL = 3000;

/** 处理流程步骤 */
const PROCESS_STEPS = [
  { key: "upload", title: "上传" },
  { key: "extract", title: "文本提取" },
  { key: "chunk", title: "切分" },
  { key: "vector", title: "向量化" },
  { key: "done", title: "完成" },
];

/** 根据文件扩展名返回图标 */
function fileIcon(filename: string) {
  const ext = filename.split(".").pop()?.toLowerCase();
  if (ext === "pdf") return <FileText size={18} color="#d93025" />;
  if (ext === "doc" || ext === "docx") return <FileText size={18} color="#005bac" />;
  return <FileIcon size={18} color="#555" />;
}

function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

export function KnowledgePage() {
  const { token, isAdmin } = useAuth();

  // ========== 列表状态 ==========
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ========== 上传状态 ==========
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [title, setTitle] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadPercent, setUploadPercent] = useState(0);

  // ========== 弹窗状态 ==========
  const [detailDoc, setDetailDoc] = useState<DocumentRecord | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<DocumentRecord | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  // 批量删除
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [batchDeleteModal, setBatchDeleteModal] = useState(false);
  const [batchDeleteLoading, setBatchDeleteLoading] = useState(false);

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

  // ========== 处理状态轮询 ==========
  useEffect(() => {
    const hasProcessing = documents.some((d) =>
      PROCESSING_STATUSES.includes(d.status),
    );
    if (hasProcessing && !pollTimerRef.current) {
      pollTimerRef.current = setInterval(() => loadDocuments(), POLL_INTERVAL);
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

  // ========== Antd Upload 配置 ==========
  const beforeUpload = (file: RcFile) => {
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!ALLOWED_TYPES.includes(ext)) {
      message.error(`仅支持 ${ALLOWED_LABEL} 格式`);
      return Upload.LIST_IGNORE;
    }
    if (file.size > MAX_FILE_SIZE) {
      message.error(`文件不能超过 50MB，当前大小 ${formatSize(file.size)}`);
      return Upload.LIST_IGNORE;
    }
    if (!title.trim()) {
      message.warning("请先输入文档标题");
      return Upload.LIST_IGNORE;
    }
    return true;
  };

  const handleUpload = async () => {
    if (fileList.length === 0 || !title.trim() || !token) return;
    const file = fileList[0].originFileObj as File;
    if (!file) return;

    setUploading(true);
    setUploadPercent(0);

    // 模拟进度（真实场景应使用 axios onUploadProgress）
    const progressTimer = setInterval(() => {
      setUploadPercent((prev) => Math.min(prev + 15, 90));
    }, 200);

    try {
      await api.documents.upload(token, title.trim(), file);
      clearInterval(progressTimer);
      setUploadPercent(100);
      message.success("文档上传成功，正在处理中...");
      setTitle("");
      setFileList([]);
      setUploadPercent(0);
      await loadDocuments();
    } catch (err: unknown) {
      clearInterval(progressTimer);
      setUploadPercent(0);
      message.error(err instanceof Error ? err.message : "上传失败");
    } finally {
      setUploading(false);
    }
  };

  // ========== 单个删除 ==========
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

  // ========== 批量删除 ==========
  const handleBatchDelete = async () => {
    if (!token || selectedIds.size === 0) return;
    setBatchDeleteLoading(true);
    try {
      // 逐个删除（后端无批量接口）
      for (const id of selectedIds) {
        await api.documents.delete(token, id);
      }
      message.success(`已删除 ${selectedIds.size} 个文档`);
      setSelectedIds(new Set());
      await loadDocuments();
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "批量删除失败");
    } finally {
      setBatchDeleteLoading(false);
      setBatchDeleteModal(false);
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

  // ========== 数据处理 ==========
  const visibleDocuments = documents.filter((doc) =>
    `${doc.title} ${doc.filename}`.toLowerCase().includes(query.toLowerCase()),
  );
  const readyCount = documents.filter((d) => d.status === "READY").length;
  const processingCount = documents.filter((d) =>
    PROCESSING_STATUSES.includes(d.status),
  ).length;
  const chunkCount = documents.reduce((sum, doc) => sum + doc.chunk_count, 0);

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  // 当前步骤（用于详情弹窗）
  const getStepIndex = (status: string) => {
    if (status === "PENDING") return 0;
    if (status === "PROCESSING") return 2; // 假设在切分/向量化阶段
    if (status === "READY") return 4;
    if (status === "FAILED") return -1; // 错误状态
    return -1;
  };

  // ========== 非管理员 ==========
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
          <span><b>{documents.length}</b>资料总数</span>
        </div>
        <div>
          <CircleCheck size={20} />
          <span><b>{readyCount}</b>可检索</span>
        </div>
        <div>
          <Layers3 size={20} />
          <span><b>{chunkCount.toLocaleString()}</b>知识片段</span>
        </div>
      </section>

      {/* ========== Antd Dragger 拖拽上传 ========== */}
      <div className="upload-form">
        <div className="section-title">
          <div>
            <span>资料入库</span>
            <h2>添加新的知识来源</h2>
          </div>
          <p>
            支持 {ALLOWED_LABEL} 格式，单文件不超过 50MB，支持拖拽上传
            {processingCount > 0 && (
              <span style={{ color: "var(--river)", marginLeft: 8 }}>
                · {processingCount} 个文件处理中...
              </span>
            )}
          </p>
        </div>

        <div style={{ marginBottom: 12 }}>
          <Input
            placeholder="输入资料标题，例如：本科生奖学金管理办法"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={{ maxWidth: 480 }}
          />
        </div>

        <Dragger
          fileList={fileList}
          beforeUpload={beforeUpload}
          onChange={({ fileList: fl }) => setFileList(fl.slice(-1))}
          onRemove={() => setFileList([])}
          maxCount={1}
          accept={ALLOWED_TYPES.join(",")}
          disabled={uploading}
          style={{ marginBottom: 16 }}
        >
          <p className="ant-upload-drag-icon">
            <Inbox size={36} color="#005bac" />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持 {ALLOWED_LABEL} 格式，最大 50MB
          </p>
        </Dragger>

        {uploadPercent > 0 && (
          <Progress percent={uploadPercent} style={{ marginBottom: 12 }} />
        )}

        <Button
          type="primary"
          icon={<UploadIcon size={16} />}
          onClick={handleUpload}
          loading={uploading}
          disabled={fileList.length === 0 || !title.trim()}
        >
          {uploading ? "上传中..." : "上传文档"}
        </Button>
      </div>

      {/* ========== 搜索 + 批量操作 ========== */}
      <div className="list-toolbar">
        <div>
          <h2>资料目录</h2>
          <span>共 {documents.length} 条记录</span>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          {selectedIds.size > 0 && (
            <Button
              danger
              icon={<Trash2 size={14} />}
              onClick={() => setBatchDeleteModal(true)}
            >
              批量删除 ({selectedIds.size})
            </Button>
          )}
          <Input
            prefix={<Search size={16} />}
            placeholder="搜索标题或文件名"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ width: 240 }}
            allowClear
          />
        </div>
      </div>

      {/* ========== 文档列表 ========== */}
      {loading && documents.length === 0 ? (
        <div className="loading">
          <Loader size={24} className="spin" /> 加载中...
        </div>
      ) : (
        <div className="document-list">
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

          {visibleDocuments.map((doc) => {
            const statusInfo = STATUS_MAP[doc.status] || { label: doc.status, color: "default" };
            const ext = doc.filename.split(".").pop()?.toLowerCase() || "";
            return (
              <div key={doc.id} className="document-card">
                <div className="doc-info">
                  <Checkbox
                    checked={selectedIds.has(doc.id)}
                    onChange={() => toggleSelect(doc.id)}
                    style={{ marginRight: 8 }}
                  />
                  <span className="doc-icon">{fileIcon(doc.filename)}</span>
                  <div className="doc-meta">
                    <span className="doc-title">{doc.title}</span>
                    <span className="doc-detail">
                      {doc.filename} · {ext.toUpperCase()} · {formatSize(doc.size)} ·{" "}
                      {doc.chunk_count} 片段 ·{" "}
                      {doc.created_at ? new Date(doc.created_at).toLocaleDateString("zh-CN") : "-"}
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
                  <button onClick={() => setDetailDoc(doc)} title="查看详情">
                    <Eye size={14} />
                  </button>
                  <button
                    onClick={() => handleReprocess(doc.id)}
                    title="重新处理"
                    disabled={doc.status === "PROCESSING"}
                  >
                    <RefreshCw size={14} className={doc.status === "PROCESSING" ? "spin" : ""} />
                  </button>
                  <button onClick={() => setDeleteTarget(doc)} title="删除">
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

      {/* ========== 详情弹窗 ========== */}
      <Modal
        title="文档详情"
        open={!!detailDoc}
        onCancel={() => setDetailDoc(null)}
        footer={
          <Button onClick={() => setDetailDoc(null)}>关闭</Button>
        }
        width={560}
      >
        {detailDoc && (
          <div>
            <div style={{ display: "flex", gap: 12, marginBottom: 20 }}>
              {fileIcon(detailDoc.filename)}
              <div>
                <h3 style={{ margin: 0 }}>{detailDoc.title}</h3>
                <p style={{ color: "#999", margin: "4px 0 0" }}>{detailDoc.filename}</p>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px 16px", marginBottom: 20 }}>
              <span>类型：<strong>{detailDoc.filename.split(".").pop()?.toUpperCase()}</strong></span>
              <span>大小：<strong>{formatSize(detailDoc.size)}</strong></span>
              <span>片段数：<strong>{detailDoc.chunk_count}</strong></span>
              <span>上传时间：<strong>{detailDoc.created_at ? new Date(detailDoc.created_at).toLocaleString("zh-CN") : "-"}</strong></span>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Tag color={STATUS_MAP[detailDoc.status]?.color || "default"}>
                {STATUS_MAP[detailDoc.status]?.label || detailDoc.status}
              </Tag>
            </div>

            {/* 处理流程 Steps */}
            <Steps
              size="small"
              current={getStepIndex(detailDoc.status)}
              status={detailDoc.status === "FAILED" ? "error" : detailDoc.status === "PROCESSING" ? "process" : undefined}
              items={PROCESS_STEPS.map((step) => ({
                title: step.title,
              }))}
            />

            {detailDoc.error && (
              <div style={{ marginTop: 16, padding: 12, background: "#fff2f0", borderRadius: 6, color: "#d93025", fontSize: 13 }}>
                <AlertTriangle size={14} style={{ marginRight: 6, verticalAlign: -2 }} />
                {detailDoc.error}
              </div>
            )}

            {detailDoc.status === "READY" && (
              <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
                <Button
                  type="primary"
                  icon={<Download size={14} />}
                  onClick={() => {
                    // 后端需提供下载接口，这里先提示
                    message.info("下载功能需后端提供文件下载接口");
                  }}
                >
                  下载原始文件
                </Button>
                <Button
                  icon={<RefreshCw size={14} />}
                  onClick={() => {
                    setDetailDoc(null);
                    handleReprocess(detailDoc.id);
                  }}
                >
                  重新处理
                </Button>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* ========== 删除确认弹窗 ========== */}
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
          <Button key="cancel" onClick={() => setDeleteTarget(null)}>取消</Button>,
          <Button key="delete" danger loading={deleteLoading} onClick={handleDelete} icon={<Trash2 size={14} />}>
            确认删除
          </Button>,
        ]}
      >
        <p>
          即将<strong style={{ color: "#d93025" }}>永久删除</strong>文档
          <strong>「{deleteTarget?.title}」</strong>（{deleteTarget?.filename}）
        </p>
        <p style={{ color: "#999", fontSize: 13 }}>
          此操作将同时删除文档记录、向量数据和存储文件，不可撤销。
        </p>
      </Modal>

      {/* ========== 批量删除确认弹窗 ========== */}
      <Modal
        title={
          <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <AlertTriangle size={18} color="#d93025" />
            确认批量删除
          </span>
        }
        open={batchDeleteModal}
        onCancel={() => setBatchDeleteModal(false)}
        footer={[
          <Button key="cancel" onClick={() => setBatchDeleteModal(false)}>取消</Button>,
          <Button key="delete" danger loading={batchDeleteLoading} onClick={handleBatchDelete} icon={<Trash2 size={14} />}>
            删除 {selectedIds.size} 个文档
          </Button>,
        ]}
      >
        <p>
          即将<strong style={{ color: "#d93025" }}>永久删除 {selectedIds.size} 个文档</strong>
        </p>
        <p style={{ color: "#999", fontSize: 13 }}>
          此操作不可撤销，所有选中文档的数据将被清除。
        </p>
      </Modal>
    </div>
  );
}
