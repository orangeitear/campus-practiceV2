/** 统一响应格式 — 与后端 Result<T> 对应 */
export interface ApiResponse<T = unknown> {
  code: number;
  message: string;
  data: T;
  timestamp: string;
}

/** 用户对象 — 与后端 UserResponse 对应 */
export interface UserItem {
  id: number;
  username: string;
  email: string | null;
  role: "admin" | "user" | "guest";
  is_active: boolean;
  created_at: string;
}

/** 分页响应 — 与后端 /user/list 返回的 data 对应 */
export interface PaginatedUsers {
  total: number;
  page: number;
  size: number;
  list: UserItem[];
}

/** 登录请求体 */
export interface LoginRequest {
  username: string;
  password: string;
}

/** 登录响应 — 与后端 /user/login 返回的 data 对应 */
export interface LoginResponse {
  token: string;
  user: UserItem;
}

/** 注册请求体 */
export interface RegisterRequest {
  username: string;
  password: string;
  email?: string;
}

/** 更新用户状态请求体 */
export interface UpdateStatusRequest {
  is_active: boolean;
}

/** 更新用户角色请求体 */
export interface UpdateRoleRequest {
  role: string;
}

/** 新增用户请求体（管理员创建） */
export interface CreateUserRequest {
  username: string;
  password: string;
  email?: string;
}

/** 搜索/筛选参数 */
export interface UserQueryParams {
  page: number;
  size: number;
  keyword?: string;
  role?: string;
}
