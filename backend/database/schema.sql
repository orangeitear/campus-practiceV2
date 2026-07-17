-- =============================================
-- 校园问答助手 - 数据库建表脚本
-- 表: sys_user (用户表), kb_document (文档表), qa_record (问答记录表)
-- =============================================

-- 1. 用户表
CREATE TABLE sys_user (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    role ENUM('admin', 'user') DEFAULT 'user' COMMENT '角色',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT '用户表';

-- 2. 知识库文档表
CREATE TABLE kb_document (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '文档ID',
    title VARCHAR(255) NOT NULL COMMENT '文档标题',
    file_name VARCHAR(255) NOT NULL COMMENT '文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    file_type VARCHAR(50) COMMENT '文件类型 (pdf/docx/txt/md)',
    file_size BIGINT COMMENT '文件大小 (字节)',
    chunk_count INT DEFAULT 0 COMMENT '切分块数',
    status ENUM('processing', 'completed', 'failed') DEFAULT 'processing' COMMENT '处理状态',
    uploaded_by INT COMMENT '上传者ID (关联sys_user)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (uploaded_by) REFERENCES sys_user(id) ON DELETE SET NULL
) COMMENT '知识库文档表';

-- 3. 问答记录表
CREATE TABLE qa_record (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    session_id VARCHAR(100) COMMENT '会话ID (用于分组)',
    question TEXT NOT NULL COMMENT '用户问题',
    answer TEXT NOT NULL COMMENT 'AI回答',
    sources JSON COMMENT '引用来源 (文档名/段落)',
    document_id INT COMMENT '关联文档ID (如果来自知识库)',
    user_id INT COMMENT '提问用户ID (关联sys_user)',
    ip_address VARCHAR(45) COMMENT '客户端IP',
    user_agent VARCHAR(255) COMMENT '浏览器User-Agent',
    response_time_ms INT COMMENT '响应耗时 (毫秒)',
    is_satisfied BOOLEAN DEFAULT NULL COMMENT '用户满意度 (NULL表示未评价)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (document_id) REFERENCES kb_document(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES sys_user(id) ON DELETE SET NULL
) COMMENT '问答记录表';