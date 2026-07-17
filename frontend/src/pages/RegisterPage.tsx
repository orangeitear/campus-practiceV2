import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Form, Input, Button, message } from "antd";
import { useAuth } from "../context/auth-context";
import request from "../services/request";
import {
  UserPlus,
  Waves,
  Quote,
  User,
  AtSign,
  Lock,
  LogIn,
} from "lucide-react";

const registerSchema = z
  .object({
    username: z.string().min(2, "姓名至少2个字符").max(40, "姓名最多40个字符"),
    email: z.string().min(1, "邮箱不能为空").email("请输入有效的邮箱地址"),
    password: z.string().min(6, "密码至少6位").max(72, "密码最多72位"),
    confirmPassword: z.string().min(1, "请确认密码"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "两次输入的密码不一致",
    path: ["confirmPassword"],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const password = watch("password");

  const onSubmit = async (data: RegisterFormData) => {
  setLoading(true);
  try {
    // 直接调用，不需要 res.data
    await request.post("/user/register", {
      username: data.username,
      email: data.email,
      password: data.password,
    });
    
    // 注册成功
    message.success("注册成功，请登录");
    navigate("/login");
    
  } catch (err: unknown) {
    // 注册失败（如用户名已存在）
    const error = err as Error;
    message.error(error.message || "注册失败");
    console.error("注册失败:", error);
  } finally {
    setLoading(false);
  }
};

  // Password strength indicator
  const getStrength = (pwd: string) => {
    let score = 0;
    if (pwd.length >= 6) score++;
    if (pwd.length >= 10) score++;
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score++;
    if (/\d/.test(pwd)) score++;
    if (/[^a-zA-Z0-9]/.test(pwd)) score++;
    return score;
  };

  const strength = getStrength(password || "");
  const strengthLabels = ["太短", "弱", "一般", "良好", "强", "很强"];
  const strengthColors = ["#d93025", "#d93025", "#f9ab00", "#4a9b9b", "#1e8e3e", "#1e8e3e"];

  return (
    <div className="auth-shell">
      <section className="auth-story">
        <div className="auth-mark">
          <Waves size={28} />
          <span>
            河海大学
            <br />
            <small>HOHAI UNIVERSITY</small>
          </span>
        </div>
        <div className="auth-copy">
          <span>校园知识 · 汇流成河</span>
          <h1>
            从一次提问，
            <br />
            走近一所大学。
          </h1>
          <p>创建账号，保留你的校园问答历史与学习线索。</p>
        </div>
        <Quote className="auth-quote" size={72} />
      </section>
      <section className="auth-panel">
        <div className="auth-card">
          <div className="auth-heading">
            <span>
              <UserPlus size={18} />
            </span>
            <div>
              <small>CREATE ACCOUNT</small>
              <h2>注册校园账号</h2>
              <p>填写基本信息，开启知识服务</p>
            </div>
          </div>
          <Form onFinish={handleSubmit(onSubmit)} layout="vertical" style={{ marginTop: 24 }}>
            <Form.Item
              label="用户名"
              validateStatus={errors.username ? "error" : ""}
              help={errors.username?.message}
            >
              <Input
                prefix={<User size={16} />}
                placeholder="请输入用户名"
                {...register("username")}
                onChange={(e) => setValue("username", e.target.value, { shouldValidate: true })}
              />
            </Form.Item>
            <Form.Item
              label="邮箱"
              validateStatus={errors.email ? "error" : ""}
              help={errors.email?.message}
            >
              <Input
                prefix={<AtSign size={16} />}
                placeholder="请输入邮箱"
                {...register("email")}
                onChange={(e) => setValue("email", e.target.value, { shouldValidate: true })}
              />
            </Form.Item>
            <Form.Item
              label="密码"
              validateStatus={errors.password ? "error" : ""}
              help={errors.password?.message}
            >
              <Input.Password
                prefix={<Lock size={16} />}
                placeholder="至少6位字符"
                {...register("password")}
                onChange={(e) => setValue("password", e.target.value, { shouldValidate: true })}
              />
            </Form.Item>
            {password && (
              <div style={{ marginBottom: 16 }}>
                <div style={{ display: "flex", gap: 4, marginBottom: 4 }}>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div
                      key={i}
                      style={{
                        flex: 1,
                        height: 4,
                        borderRadius: 2,
                        background: i < strength ? strengthColors[strength] : "#e0e0e0",
                        transition: "background 0.2s",
                      }}
                    />
                  ))}
                </div>
                <span style={{ color: strengthColors[strength], fontSize: 12 }}>
                  密码强度：{strengthLabels[strength]}
                </span>
              </div>
            )}
            <Form.Item
              label="确认密码"
              validateStatus={errors.confirmPassword ? "error" : ""}
              help={errors.confirmPassword?.message}
            >
              <Input.Password
                prefix={<Lock size={16} />}
                placeholder="再次输入密码"
                {...register("confirmPassword")}
                onChange={(e) =>
                  setValue("confirmPassword", e.target.value, { shouldValidate: true })
                }
              />
            </Form.Item>
            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                block
                loading={loading}
                icon={<UserPlus size={18} />}
                size="large"
              >
                注册
              </Button>
            </Form.Item>
          </Form>
          <div className="auth-footer">
            <Link to="/login" className="btn-link">
              <LogIn size={16} />
              已有账号？去登录
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}