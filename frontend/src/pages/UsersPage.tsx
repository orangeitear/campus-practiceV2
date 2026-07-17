import { useState, useEffect, useCallback } from "react";
import {
  Table,
  Input,
  Tag,
  Button,
  Modal,
  Form,
  Select,
  message,
} from "antd";
import { useAuth } from "../context/auth-context";
import request from "../services/request";
import type { UserItem, PaginatedUsers } from "../types/api";
import {
  Users,
  Shield,
  UserCheck,
  UserX,
  Search,
  UserRoundCheck,
  ShieldCheck,
  Pencil,
  Plus,
  Trash2,
  AlertTriangle,
  Filter,
} from "lucide-react";

const PAGE_SIZE = 10;

/** 角色选项映射 */
const ROLE_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "全部角色" },
  { value: "admin", label: "管理员" },
  { value: "user", label: "普通用户" },
  { value: "guest", label: "游客" },
];

const ROLE_LABELS: Record<string, string> = {
  admin: "管理员",
  user: "普通用户",
  guest: "游客",
};

export function UsersPage() {
  const { token } = useAuth();

  // ========== 列表状态 ==========
  const [users, setUsers] = useState<UserItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [keyword, setKeyword] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [total, setTotal] = useState(0);

  // 统计信息（从后端全量获取）
  const [stats, setStats] = useState({ total: 0, active: 0, admin: 0 });

  // ========== 弹窗状态 ==========
  const [editModal, setEditModal] = useState(false);
  const [editUser, setEditUser] = useState<UserItem | null>(null);
  const [addModal, setAddModal] = useState(false);
  const [deleteModal, setDeleteModal] = useState(false);
  const [deleteUser, setDeleteUser] = useState<UserItem | null>(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [editForm] = Form.useForm();
  const [addForm] = Form.useForm();

  // ========== 后端分页加载 ==========
  const loadUsers = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await request.get("/user/list", {
        params: {
          page: currentPage,
          size: PAGE_SIZE,
          keyword: keyword || undefined,
        },
      }) as PaginatedUsers;

      setUsers(data.list ?? []);
      setTotal(data.total ?? 0);
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "加载用户失败");
      setUsers([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [token, currentPage, keyword]);

  // 获取统计信息（全量列表，仅统计用）
  const loadStats = useCallback(async () => {
    if (!token) return;
    try {
      const allUsers = await request.get("/user/users") as UserItem[];
      setStats({
        total: allUsers.length,
        active: allUsers.filter((u) => u.is_active).length,
        admin: allUsers.filter((u) => u.role === "admin").length,
      });
    } catch {
      // 统计加载失败不弹错误提示
    }
  }, [token]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  // ========== 搜索与筛选 ==========
  const handleSearch = (value: string) => {
    setKeyword(value);
    setCurrentPage(1); // 搜索时重置页码
  };

  const handleRoleFilter = (value: string) => {
    setRoleFilter(value);
    // 角色筛选暂用前端过滤（后端 list 接口暂不支持 role 参数）
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  // 前端角色筛选（临时方案，可后续升级为后端 role 参数）
  const filteredUsers = roleFilter
    ? users.filter((u) => u.role === roleFilter)
    : users;

  // ========== 操作函数 ==========
  const refreshAfterAction = () => {
    loadUsers();
    loadStats();
  };

  const toggleRole = async (user: UserItem) => {
    if (!token) return;
    const newRole = user.role === "admin" ? "user" : "admin";
    try {
      await request.patch(`/user/${user.id}/role`, { role: newRole });
      message.success(`已将 ${user.username} 设为${ROLE_LABELS[newRole]}`);
      refreshAfterAction();
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "角色更新失败");
    }
  };

  const toggleActive = async (user: UserItem) => {
    if (!token) return;
    try {
      await request.put(`/user/${user.id}/status`, { is_active: !user.is_active });
      message.success(user.is_active ? `已停用 ${user.username}` : `已启用 ${user.username}`);
      refreshAfterAction();
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "状态更新失败");
    }
  };

  const handleDelete = async () => {
    if (!token || !deleteUser) return;
    setModalLoading(true);
    try {
      await request.delete(`/user/${deleteUser.id}`);
      message.success(`已删除用户 ${deleteUser.username}`);
      refreshAfterAction();
      setDeleteModal(false);
      setDeleteUser(null);
      // 如果删完当前页为空，回到上一页
      if (filteredUsers.length <= 1 && currentPage > 1) {
        setCurrentPage((prev) => prev - 1);
      }
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "删除失败");
    } finally {
      setModalLoading(false);
    }
  };

  const handleEdit = async (values: { role: string }) => {
    if (!token || !editUser) return;
    setModalLoading(true);
    try {
      // 仅通过角色接口更新角色；邮箱目前后端无单独更新接口
      if (values.role !== editUser.role) {
        await request.patch(`/user/${editUser.id}/role`, { role: values.role });
      }
      message.success(`用户 ${editUser.username} 已更新`);
      refreshAfterAction();
      setEditModal(false);
      setEditUser(null);
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "更新失败");
    } finally {
      setModalLoading(false);
    }
  };

  const handleAdd = async (values: {
    username: string;
    email: string;
    password: string;
  }) => {
    if (!token) return;
    setModalLoading(true);
    try {
      await request.post("/user/register", values);
      message.success("用户已创建");
      refreshAfterAction();
      setAddModal(false);
      addForm.resetFields();
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "创建失败");
    } finally {
      setModalLoading(false);
    }
  };

  // ========== 表格列配置 ==========
  const columns = [
    {
      title: "ID",
      dataIndex: "id",
      width: 60,
    },
    {
      title: "用户名",
      dataIndex: "username",
    },
    {
      title: "邮箱",
      dataIndex: "email",
      render: (email: string | null) => email || <span style={{ color: "#bbb" }}>未填写</span>,
    },
    {
      title: "角色",
      dataIndex: "role",
      render: (role: string) => {
        const label = ROLE_LABELS[role] || role;
        if (role === "admin") {
          return (
            <Tag color="blue">
              <Shield size={12} style={{ marginRight: 4 }} />
              {label}
            </Tag>
          );
        }
        if (role === "guest") {
          return (
            <Tag color="default">
              <Users size={12} style={{ marginRight: 4 }} />
              {label}
            </Tag>
          );
        }
        return (
          <Tag>
            <Users size={12} style={{ marginRight: 4 }} />
            {label}
          </Tag>
        );
      },
    },
    {
      title: "状态",
      dataIndex: "is_active",
      render: (is_active: boolean) =>
        is_active ? (
          <Tag color="green">
            <UserCheck size={12} style={{ marginRight: 4 }} />
            启用
          </Tag>
        ) : (
          <Tag color="red">
            <UserX size={12} style={{ marginRight: 4 }} />
            停用
          </Tag>
        ),
    },
    {
      title: "注册时间",
      dataIndex: "created_at",
      render: (created_at: string) =>
        created_at ? new Date(created_at).toLocaleString("zh-CN") : "-",
    },
    {
      title: "操作",
      key: "actions",
      width: 340,
      render: (_: unknown, record: UserItem) => (
        <div className="actions" style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
          <Button
            size="small"
            icon={<Pencil size={12} />}
            onClick={() => {
              setEditUser(record);
              editForm.setFieldsValue({ role: record.role });
              setEditModal(true);
            }}
          >
            编辑
          </Button>
          <Button
            size="small"
            onClick={() => toggleRole(record)}
          >
            {record.role === "admin" ? "设为普通用户" : "设为管理员"}
          </Button>
          <Button
            size="small"
            onClick={() => toggleActive(record)}
          >
            {record.is_active ? "停用" : "启用"}
          </Button>
          <Button
            size="small"
            danger
            icon={<Trash2 size={12} />}
            onClick={() => {
              setDeleteUser(record);
              setDeleteModal(true);
            }}
          >
            删除
          </Button>
        </div>
      ),
    },
  ];

  // ========== 渲染 ==========
  return (
    <div className="admin-page">
      {/* 页面标题 */}
      <header className="page-heading">
        <div>
          <span className="eyebrow">IDENTITY & ACCESS</span>
          <h1>用户与权限</h1>
          <p>查看校园用户，维护账号状态与管理权限。</p>
        </div>
        <span className="page-index">03</span>
      </header>

      {/* 统计指标 */}
      <section className="metric-strip">
        <div>
          <Users size={20} />
          <span>
            <b>{stats.total}</b>用户总数
          </span>
        </div>
        <div>
          <UserRoundCheck size={20} />
          <span>
            <b>{stats.active}</b>正常账号
          </span>
        </div>
        <div>
          <ShieldCheck size={20} />
          <span>
            <b>{stats.admin}</b>管理员
          </span>
        </div>
      </section>

      {/* 搜索与工具栏 */}
      <div className="list-toolbar">
        <div>
          <h2>用户目录</h2>
          <span>角色与账号状态实时生效</span>
        </div>
        <div className="toolbar-actions" style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <Select
            value={roleFilter}
            onChange={handleRoleFilter}
            style={{ width: 130 }}
            options={ROLE_OPTIONS}
            suffixIcon={<Filter size={14} />}
          />
          <Input.Search
            placeholder="搜索用户名或邮箱"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onSearch={handleSearch}
            style={{ width: 240 }}
            prefix={<Search size={16} />}
            allowClear
          />
          <Button
            icon={<Plus size={16} />}
            onClick={() => setAddModal(true)}
            style={{
              background: "white",
              color: "var(--river)",
              border: "1px solid var(--river)",
              fontWeight: 600,
            }}
          >
            新增用户
          </Button>
        </div>
      </div>

      {/* 用户表格 */}
      <Table
        rowKey="id"
        columns={columns}
        dataSource={filteredUsers}
        loading={loading}
        pagination={{
          current: currentPage,
          pageSize: PAGE_SIZE,
          total: roleFilter ? filteredUsers.length : total,
          onChange: handlePageChange,
          showSizeChanger: false,
          showTotal: (t) => `共 ${t} 条记录`,
          style: { marginTop: 16, justifyContent: "flex-end" },
        }}
        locale={{
          emptyText: (
            <div style={{ padding: 40 }}>
              <Users size={48} style={{ color: "#ccc", marginBottom: 8 }} />
              <p style={{ color: "#999" }}>暂无用户数据</p>
            </div>
          ),
        }}
      />

      {/* ========== 编辑弹窗 ========== */}
      <Modal
        title={
          <span>
            <Pencil size={16} style={{ marginRight: 8 }} />
            编辑用户
          </span>
        }
        open={editModal}
        onCancel={() => {
          setEditModal(false);
          setEditUser(null);
        }}
        footer={null}
        destroyOnHidden
        forceRender
      >
        <Form form={editForm} layout="vertical" onFinish={handleEdit}>
          <Form.Item label="用户名">
            <Input value={editUser?.username} disabled />
          </Form.Item>
          <Form.Item label="邮箱">
            <Input value={editUser?.email ?? "未填写"} disabled />
          </Form.Item>
          <Form.Item
            name="role"
            label="角色"
            rules={[{ required: true, message: "请选择角色" }]}
          >
            <Select>
              <Select.Option value="admin">管理员</Select.Option>
              <Select.Option value="user">普通用户</Select.Option>
              <Select.Option value="guest">游客</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item style={{ marginBottom: 0, textAlign: "right" }}>
            <Button
              onClick={() => {
                setEditModal(false);
                setEditUser(null);
              }}
              style={{ marginRight: 8 }}
            >
              取消
            </Button>
            <Button type="primary" htmlType="submit" loading={modalLoading}>
              保存
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* ========== 新增弹窗 ========== */}
      <Modal
        title={
          <span>
            <Plus size={16} style={{ marginRight: 8 }} />
            新增用户
          </span>
        }
        open={addModal}
        onCancel={() => {
          setAddModal(false);
          addForm.resetFields();
        }}
        footer={null}
        destroyOnHidden
        forceRender
      >
        <Form form={addForm} layout="vertical" onFinish={handleAdd}>
          <Form.Item
            name="username"
            label="用户名"
            rules={[
              { required: true, message: "请输入用户名" },
              { min: 3, message: "至少3个字符" },
              { max: 50, message: "最多50个字符" },
            ]}
          >
            <Input placeholder="请输入用户名" />
          </Form.Item>
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { type: "email", message: "邮箱格式不正确" },
            ]}
          >
            <Input placeholder="请输入邮箱（可选）" />
          </Form.Item>
          <Form.Item
            name="password"
            label="密码"
            rules={[
              { required: true, message: "请输入密码" },
              { min: 6, message: "密码至少6位" },
            ]}
          >
            <Input.Password placeholder="至少6位字符" />
          </Form.Item>
          <Form.Item style={{ marginBottom: 0, textAlign: "right" }}>
            <Button
              onClick={() => {
                setAddModal(false);
                addForm.resetFields();
              }}
              style={{ marginRight: 8 }}
            >
              取消
            </Button>
            <Button type="primary" htmlType="submit" loading={modalLoading}>
              创建
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* ========== 删除确认弹窗 ========== */}
      <Modal
        title={
          <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <AlertTriangle size={18} color="#d93025" />
            确认删除用户
          </span>
        }
        open={deleteModal}
        onCancel={() => {
          setDeleteModal(false);
          setDeleteUser(null);
        }}
        footer={[
          <Button
            key="cancel"
            onClick={() => {
              setDeleteModal(false);
              setDeleteUser(null);
            }}
          >
            取消
          </Button>,
          <Button
            key="delete"
            danger
            loading={modalLoading}
            onClick={handleDelete}
            icon={<Trash2 size={14} />}
          >
            确认删除
          </Button>,
        ]}
      >
        <p>
          即将<strong style={{ color: "#d93025" }}>永久删除</strong>用户
          <strong> {deleteUser?.username}</strong>
          {deleteUser?.email && <>（{deleteUser.email}）</>}
        </p>
        <p style={{ color: "#999", fontSize: 13 }}>
          此操作不可撤销，该用户的所有数据将被清除。
        </p>
      </Modal>
    </div>
  );
}
