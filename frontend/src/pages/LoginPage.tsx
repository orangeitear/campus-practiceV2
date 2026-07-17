import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Form, Input, Button, Checkbox, message } from "antd";
import { useAuth } from "../context/auth-context";
import request from "../services/request";
import {
  BookOpen,
  LogIn,
  UserPlus,
  Waves,
  ShieldCheck,
  Library,
  Quote,
  User,      // 添加 User
  Lock,       // 保留 Lock
} from "lucide-react";

const loginSchema = z.object({
  username: z.string().min(1, "用户名不能为空"),
  password: z.string().min(1, "密码不能为空"),
  remember: z.boolean().optional(),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      remember: false,
    },
  });

  const remember = watch("remember");

  const onSubmit = async (data: LoginFormData) => {
    setLoading(true);
    try {
      const res = await request.post("/user/login", {
        username: data.username,  // email → username
        password: data.password,
      }) as { token: string; user: any };
      login(res.token, res.user);
      message.success("登录成功");
      // 记住用户名
      if (data.remember) {
        localStorage.setItem("campus-qa-remember-username", data.username);
      } else {
        localStorage.removeItem("campus-qa-remember-username");
      }
      // 延迟跳转，确保 React Context 状态已更新
      setTimeout(() => {
        const target = res.user.role === "admin" ? "/admin" : "/";
        navigate(target, { replace: true });
      }, 100);
    } catch (err: unknown) {
      message.error(err instanceof Error ? err.message : "登录失败");
    } finally {
      setLoading(false);
    }
  };

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
            把散落的信息，
            <br />
            汇成可信的答案。
          </h1>
          <p>面向河海师生的校园知识管理与智能问答平台。</p>
        </div>
        <div className="auth-principles">
          <div>
            <Library size={20} />
            <span>
              <b>校本知识</b>源自学校公开资料
            </span>
          </div>
          <div>
            <ShieldCheck size={20} />
            <span>
              <b>来源可循</b>每条回答附参考依据
            </span>
          </div>
        </div>
        <Quote className="auth-quote" size={72} />
      </section>
      <section className="auth-panel">
        <div className="auth-card">
          <div className="auth-heading">
            <span>
              <BookOpen size={18} />
            </span>
            <div>
              <small>ADMINISTRATION</small>
              <h2>登录管理后台</h2>
              <p>使用管理员账号进入知识工作台</p>
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
              label="密码"
              validateStatus={errors.password ? "error" : ""}
              help={errors.password?.message}
            >
              <Input.Password
                prefix={<Lock size={16} />}
                placeholder="请输入密码"
                {...register("password")}
                onChange={(e) => setValue("password", e.target.value, { shouldValidate: true })}
              />
            </Form.Item>
            <Form.Item>
              <Checkbox
                checked={remember}
                onChange={(e) => setValue("remember", e.target.checked)}
              >
                记住我
              </Checkbox>
            </Form.Item>
            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                block
                loading={loading}
                icon={<LogIn size={18} />}
                size="large"
              >
                登录
              </Button>
            </Form.Item>
          </Form>
          <div className="auth-footer">
            <Link to="/register" className="btn-link">
              <UserPlus size={16} />
              还没有账号？去注册
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
