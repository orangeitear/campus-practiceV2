const getApiBase = () =>
  (typeof window !== "undefined" && window.__HHU_CHAT_API_BASE__) || "";

export interface ApiUser {
  id: number;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}
export interface AuthResponse {
  token: string;
  user: ApiUser;
}
export interface ConversationRecord {
  id: number;
  title: string;
  updated_at: string;
  message_count: number;
}
export interface SourceRecord {
  index: number;
  title: string;
  content: string;
  score: number;
  source_url?: string;
  category?: string;
}
export interface MessageRecord {
  id: number;
  role: "USER" | "ASSISTANT";
  content: string;
  sources?: SourceRecord[];
}
export interface ConversationDetail extends ConversationRecord {
  messages: MessageRecord[];
}
export interface DocumentRecord {
  id: number;
  title: string;
  filename: string;
  status: string;
  chunk_count: number;
  size: number;
  created_at: string;
  error: string | null;
}

async function fetchApi<T>(
  path: string,
  options?: RequestInit & { token?: string },
): Promise<T> {
  const base = getApiBase().replace(/\/$/, "");
   // 👇 添加这三行调试
  console.log('=== fetchApi 调试 ===');
  console.log('1. base =', base);
  console.log('2. path =', path);
  
  const url = `${base}${path}`;
  console.log('3. final url =', url);
  console.log('==================');
  // const url = `${base}${path}`;
  const isFormData = options?.body instanceof FormData;
  const headers: Record<string, string> = {
    ...(!isFormData ? { "Content-Type": "application/json" } : {}),
    ...((options?.headers as Record<string, string>) || {}),
  };
  if (options?.token) {
    headers["Authorization"] = `Bearer ${options.token}`;
  }

  const res = await fetch(url, {
    ...options,
    headers,
  });

  // Handle 401 Unauthorized - redirect to login
  if (res.status === 401) {
    localStorage.removeItem("campus-qa-auth");
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "/login";
    throw new Error("未登录或登录已过期，请重新登录");
  }

  if (!res.ok) {
    const data = await res.json().catch(() => ({ detail: "请求失败" }));
    throw new Error(data.detail || `HTTP ${res.status}`);
  }

  if (res.status === 204) {
    return null as T;
  }

  // Parse unified response format Result<T> { code, message, data }
  const json = await res.json();
  if (json && typeof json.code === "number") {
    if (json.code !== 200) {
      throw new Error(json.message || `请求失败 (code: ${json.code})`);
    }
    return json.data as T;
  }

  // Fallback for non-standard responses
  return json as T;
}

export const api = {
  health: () => fetchApi("/health"),

  login: (username: string, password: string) =>
    fetchApi<AuthResponse>("/user/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),

  guestLogin: () =>
    fetchApi<AuthResponse>("/user/guest", {
      method: "POST",
      body: JSON.stringify({}),
    }),

  register: (username: string, email: string, password: string) =>
    fetchApi<AuthResponse>("/user/register", {
      method: "POST",
      body: JSON.stringify({ username, email, password }),
    }),

  me: (token: string) => fetchApi<ApiUser>("/user/me", { token }),

  stats: (token: string) =>
    fetchApi<{ documents: number; chunks: number; conversations: number }>(
      "/stats",
      { token },
    ),

  documents: {
    list: (token: string) =>
      fetchApi<DocumentRecord[]>("/documents", { token }),
    upload: (token: string, title: string, file: File) => {
      const form = new FormData();
      form.append("title", title);
      form.append("file", file);
      return fetchApi<DocumentRecord>("/documents", {
        method: "POST",
        token,
        body: form,
      });
    },
    delete: (token: string, id: number) =>
      fetchApi<null>(`/documents/${id}`, { method: "DELETE", token }),
    reprocess: (token: string, id: number) =>
      fetchApi<DocumentRecord>(`/documents/${id}/reprocess`, {
        method: "POST",
        token,
      }),
  },

  chat: {
    stream: async (
      token: string,
      question: string,
      conversationId?: number,
    ) => {
      const url = `${getApiBase()}/chat/stream`;
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          question,
          conversation_id: conversationId,
        }),
      });
      if (!response.ok) {
        const data = await response
          .json()
          .catch(() => ({ detail: "问答请求失败" }));
        throw new Error(data.detail || `HTTP ${response.status}`);
      }
      return response;
    },
  },

  conversations: {
    list: (token: string) =>
      fetchApi<ConversationRecord[]>("/conversations", { token }),
    get: (token: string, id: number) =>
      fetchApi<ConversationDetail>(`/conversations/${id}`, { token }),
    delete: (token: string, id: number) =>
      fetchApi<null>(`/conversations/${id}`, { method: "DELETE", token }),
  },

  users: {
  // 获取所有用户列表 - 根据API文档: GET /api/user/users
  getAll: (token: string) => fetchApi<ApiUser[]>("/api/user/users", { token }),
  
  // 创建用户 - 根据API文档: POST /api/user/register
  create: (token: string, data: { username: string; email: string; password: string }) =>
    fetchApi<ApiUser>("/api/user/register", {
      method: "POST",
      token,
      body: JSON.stringify(data),
    }),
  
  // 更新用户状态 - 根据API文档: PUT /api/user/{user_id}/status
  update: (token: string, id: number, data: { is_active?: boolean; role?: string }) =>
    fetchApi<ApiUser>(`/api/user/${id}/status`, {
      method: "PUT",  // 注意是 PUT 不是 PATCH
      token,
      body: JSON.stringify({ is_active: data.is_active }),
    }),
  delete: (token: string, id: number) =>
    fetchApi<null>(`/api/user/${id}`, {
      method: "DELETE",
      token,
    }),
  
  // 更新角色 - 根据API文档: PATCH /api/user/{user_id}/role
  updateRole: (token: string, id: number, role: string) =>
    fetchApi<ApiUser>(`/api/user/${id}/role`, {
      method: "PATCH",
      token,
      body: JSON.stringify({ role }),
    }),
},
};