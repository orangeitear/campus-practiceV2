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
  Pagination,
} from "antd";
import { useAuth } from "../context/auth-context";
import request from "../services/request";  // 只保留 request
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
} from "lucide-react";

// 删除 import { api, ApiUser } from '../api';

interface UserItem {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

const PAGE_SIZE = 10;

export function UsersPage() {
  const { token } = useAuth();
  const [users, setUsers] = useState<UserItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const [editModal, setEditModal] = useState(false);
  const [editUser, setEditUser] = useState<UserItem | null>(null);
  const [addModal, setAddModal] = useState(false);
  const [deleteModal, setDeleteModal] = useState(false);
  const [deleteUser, setDeleteUser] = useState<UserItem | null>(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [editForm] = Form.useForm();
  const [addForm] = Form.useForm();

  // ✅ 统一使用 request，路径不加 /api（request 会自动加）
  const loadUsers = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await request.get("/user/users") as UserItem[];
      setUsers(data);
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "加载用户失败");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const filteredUsers = users.filter((user) =>
    `${user.username} ${user.email} ${user.role}`.toLowerCase().includes(query.toLowerCase()),
  );

  const totalPages = Math.max(1, Math.ceil(filteredUsers.length / PAGE_SIZE));
  const paginatedUsers = filteredUsers.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE,
  );

  const adminCount = users.filter((user) => user.role === "ADMIN").length;
  const activeCount = users.filter((user) => user.is_active).length;

  // ✅ 统一使用 request
  const toggleRole = async (user: UserItem) => {
    if (!token) return;
    const newRole = user.role === "ADMIN" ? "USER" : "ADMIN";
    try {
      await request.patch(`/user/${user.id}/role`, { role: newRole });
      message.success("角色已更新");
      await loadUsers();
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "更新失败");
    }
  };

  // ✅ 统一使用 request
  const toggleActive = async (user: UserItem) => {
    if (!token) return;
    try {
      await request.put(`/user/${user.id}/status`, { is_active: !user.is_active });
      message.success(user.is_active ? "已停用" : "已启用");
      await loadUsers();
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "更新失败");
    }
  };


  // ✅ 统一使用 request
  const handleDelete = async () => {
    if (!token || !deleteUser) return;
    setModalLoading(true);
    try {
      await request.delete(`/user/${deleteUser.id}`);
      message.success("用户已删除");
      await loadUsers();
      setDeleteModal(false);
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "删除失败");
    } finally {
      setModalLoading(false);
    }
  };

  // ✅ 统一使用 request
  const handleEdit = async (values: { role: string; email: string }) => {
    if (!token || !editUser) return;
    setModalLoading(true);
    try {
      await request.patch(`/user/${editUser.id}/role`, { role: values.role });
      message.success("更新成功");
      await loadUsers();
      setEditModal(false);
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "更新失败");
    } finally {
      setModalLoading(false);
    }
  };

  // ✅ 统一使用 request
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
      await loadUsers();
      setAddModal(false);
      addForm.resetFields();
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "创建失败");
    } finally {
      setModalLoading(false);
    }
  };

  // 表格列配置保持不变
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
    },
    {
      title: "角色",
      dataIndex: "role",
      render: (role: string) =>
        role === "ADMIN" ? (
          <Tag color="blue">
            <Shield size={12} style={{ marginRight: 4 }} />
            管理员
          </Tag>
        ) : (
          <Tag>
            <Users size={12} style={{ marginRight: 4 }} />
            普通用户
          </Tag>
        ),
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
        new Date(created_at).toLocaleString("zh-CN"),
    },
    {
      title: "操作",
      key: "actions",
      render: (_: unknown, record: UserItem) => (
        <div className="actions" style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
          <Button
            size="small"
            icon={<Pencil size={12} />}
            onClick={() => {
              setEditUser(record);
              editForm.setFieldsValue({ role: record.role, email: record.email });
              setEditModal(true);
            }}
          >
            编辑
          </Button>
          <Button size="small" onClick={() => toggleRole(record)}>
            {record.role === "ADMIN" ? "设为普通用户" : "设为管理员"}
          </Button>
          <Button size="small" onClick={() => toggleActive(record)}>
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

  return (
    <div className="admin-page">
      <header className="page-heading">
        <div>
          <span className="eyebrow">IDENTITY & ACCESS</span>
          <h1>用户与权限</h1>
          <p>查看校园用户，维护账号状态与管理权限。</p>
        </div>
        <span className="page-index">03</span>
      </header>
      <section className="metric-strip">
        <div>
          <Users size={20} />
          <span>
            <b>{users.length}</b>用户总数
          </span>
        </div>
        <div>
          <UserRoundCheck size={20} />
          <span>
            <b>{activeCount}</b>正常账号
          </span>
        </div>
        <div>
          <ShieldCheck size={20} />
          <span>
            <b>{adminCount}</b>管理员
          </span>
        </div>
      </section>
      <div className="list-toolbar">
        <div>
          <h2>用户目录</h2>
          <span>角色与账号状态实时生效</span>
        </div>
        <div className="toolbar-actions">
          <Input.Search
            placeholder="搜索姓名或邮箱"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setCurrentPage(1);
            }}
            style={{ width: 240 }}
            prefix={<Search size={16} />}
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

      <Table
        rowKey="id"
        columns={columns}
        dataSource={paginatedUsers}
        loading={loading}
        pagination={false}
      />

      {totalPages > 1 && (
        <div className="pagination" style={{ marginTop: 16, justifyContent: "flex-end" }}>
          <Pagination
            current={currentPage}
            pageSize={PAGE_SIZE}
            total={filteredUsers.length}
            onChange={(page) => setCurrentPage(page)}
            showSizeChanger={false}
          />
        </div>
      )}

      {/* Edit Modal */}
      <Modal
        title={
          <span>
            <Pencil size={16} style={{ marginRight: 8 }} />
            编辑用户
          </span>
        }
        open={editModal}
        onCancel={() => setEditModal(false)}
        footer={null}
      >
        <Form form={editForm} layout="vertical" onFinish={handleEdit}>
          <Form.Item label="用户名">
            <Input value={editUser?.username} disabled />
          </Form.Item>
          <Form.Item label="邮箱">
            <Input value={editUser?.email} disabled />
          </Form.Item>
          <Form.Item name="role" label="角色" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="ADMIN">管理员</Select.Option>
              <Select.Option value="USER">普通用户</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={modalLoading}>
              保存
            </Button>
            <Button style={{ marginLeft: 8 }} onClick={() => setEditModal(false)}>
              取消
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* Add Modal */}
      <Modal
        title={
          <span>
            <Plus size={16} style={{ marginRight: 8 }} />
            新增用户
          </span>
        }
        open={addModal}
        onCancel={() => setAddModal(false)}
        footer={null}
      >
        <Form form={addForm} layout="vertical" onFinish={handleAdd}>
          <Form.Item
            name="username"
            label="用户名"
            rules={[{ required: true, message: "请输入用户名" }, { min: 2, message: "至少2个字符" }]}
          >
            <Input placeholder="请输入用户名" />
          </Form.Item>
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: "请输入邮箱" },
              { type: "email", message: "邮箱格式不正确" },
            ]}
          >
            <Input placeholder="请输入邮箱" />
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
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={modalLoading}>
              创建
            </Button>
            <Button style={{ marginLeft: 8 }} onClick={() => setAddModal(false)}>
              取消
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* Delete Modal */}
            <Modal
        title={
          <span>
            <AlertTriangle size={16} style={{ marginRight: 8 }} />
            确认删除用户？
          </span>
        }
        open={deleteModal}
        onCancel={() => setDeleteModal(false)}
        footer={[
          <Button key="cancel" onClick={() => setDeleteModal(false)}>取消</Button>,
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
          即将<strong style={{ color: 'red' }}>永久删除</strong>用户 <strong>{deleteUser?.username}</strong>（{deleteUser?.email}）
          <br />
          此操作不可撤销，该用户的所有数据将被清除。
        </p>
      </Modal>
    </div>
  );
}
