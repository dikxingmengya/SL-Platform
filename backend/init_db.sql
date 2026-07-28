-- ============================================================
-- SL-Platform 家教课时管理系统 - 数据库初始化脚本
-- 使用方法: mysql -u root -p < init_db.sql
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS sl_platform
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE sl_platform;

-- ============================================================
-- 1. user 表 - 用户基础表（管理员/教师/家长）
-- ============================================================
DROP TABLE IF EXISTS notification;
DROP TABLE IF EXISTS lesson_record;
DROP TABLE IF EXISTS package;
DROP TABLE IF EXISTS teacher_student;
DROP TABLE IF EXISTS teacher;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS course_type;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT 'bcrypt 密码哈希',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    role ENUM('admin','teacher','parent') NOT NULL COMMENT '角色：管理员/教师/家长',
    is_super_admin TINYINT(1) DEFAULT 0 COMMENT '是否超级管理员',
    phone VARCHAR(20) DEFAULT '' COMMENT '手机号',
    email VARCHAR(100) DEFAULT '' COMMENT '邮箱',
    is_active TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_role (role),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================================
-- 2. teacher 表 - 教师扩展信息表
-- ============================================================
CREATE TABLE teacher (
    user_id INT PRIMARY KEY COMMENT '关联 user.id',
    subject VARCHAR(100) DEFAULT '' COMMENT '擅长科目',
    bio TEXT COMMENT '个人简介',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教师扩展信息表';

-- ============================================================
-- 3. student 表 - 学生档案表（归属于家长）
-- ============================================================
CREATE TABLE student (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '学生姓名',
    parent_user_id INT NOT NULL COMMENT '所属家长用户ID（必填）',
    grade VARCHAR(20) DEFAULT '' COMMENT '年级',
    school VARCHAR(100) DEFAULT '' COMMENT '学校',
    notes TEXT COMMENT '备注',
    is_active TINYINT(1) DEFAULT 1 COMMENT '是否在读',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_user_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_parent (parent_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生档案表';

-- ============================================================
-- 4. teacher_student 表 - 师生多对多关联表
-- ============================================================
CREATE TABLE teacher_student (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL COMMENT '教师用户ID',
    student_id INT NOT NULL COMMENT '学生ID',
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '分配时间',
    UNIQUE KEY uk_teacher_student (teacher_id, student_id),
    FOREIGN KEY (teacher_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    INDEX idx_teacher (teacher_id),
    INDEX idx_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='师生分配关联表';

-- ============================================================
-- 5. course_type 表 - 课程类型表
-- ============================================================
CREATE TABLE course_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '课程名称（如：语文、数学、英语）',
    description VARCHAR(200) DEFAULT '' COMMENT '课程描述',
    default_hourly_rate DECIMAL(10,2) DEFAULT 0.00 COMMENT '默认课时费（元/小时）',
    is_active TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程类型表';

-- ============================================================
-- 6. package 表 - 课时包表（归属于具体学生）
-- ============================================================
CREATE TABLE package (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_user_id INT NOT NULL COMMENT '归属家长用户ID',
    course_type_id INT NULL COMMENT '课程类型ID，NULL=通用课时',
    total_hours DECIMAL(8,2) NOT NULL COMMENT '总课时数',
    used_hours DECIMAL(8,2) DEFAULT 0.00 COMMENT '已消耗课时数',
    price DECIMAL(10,2) DEFAULT 0.00 COMMENT '购买金额',
    expire_date DATE COMMENT '有效期截止日期',
    status ENUM('active','expired','depleted') DEFAULT 'active' COMMENT '状态：有效/过期/耗尽',
    notes VARCHAR(500) DEFAULT '' COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (course_type_id) REFERENCES course_type(id),
    INDEX idx_parent (parent_user_id),
    INDEX idx_course_type (course_type_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课时包表';

-- ============================================================
-- 7. lesson_record 表 - 上课记录表
-- ============================================================
CREATE TABLE lesson_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL COMMENT '上课学生ID',
    teacher_id INT NOT NULL COMMENT '授课教师ID',
    course_type_id INT NOT NULL COMMENT '课程类型ID',
    hours DECIMAL(5,2) NOT NULL COMMENT '上课时长（小时）',
    content TEXT COMMENT '上课内容/备注',
    date DATETIME NOT NULL COMMENT '上课时间',
    status ENUM('draft','pending','approved','rejected') DEFAULT 'pending' COMMENT '审核状态',
    reviewer_id INT COMMENT '审核人ID',
    review_comment VARCHAR(500) DEFAULT '' COMMENT '审核意见',
    reviewed_at DATETIME COMMENT '审核时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(id),
    FOREIGN KEY (teacher_id) REFERENCES user(id),
    FOREIGN KEY (course_type_id) REFERENCES course_type(id),
    FOREIGN KEY (reviewer_id) REFERENCES user(id),
    INDEX idx_student (student_id),
    INDEX idx_teacher (teacher_id),
    INDEX idx_status (status),
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='上课记录表';

-- ============================================================
-- 8. notification 表 - 站内通知表
-- ============================================================
CREATE TABLE notification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '接收通知的用户ID',
    title VARCHAR(200) NOT NULL COMMENT '通知标题',
    content TEXT COMMENT '通知内容',
    is_read TINYINT(1) DEFAULT 0 COMMENT '是否已读',
    related_type VARCHAR(50) DEFAULT '' COMMENT '关联业务类型（record/package）',
    related_id INT DEFAULT NULL COMMENT '关联业务ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_read (is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='站内通知表';

-- ============================================================
-- 初始种子数据
-- ============================================================

-- 超级管理员账号：root / root123（仅可通过服务器/数据库直接修改）
INSERT INTO user (username, password_hash, real_name, role, is_super_admin, phone, email) VALUES
('root', '$2b$12$acWMpGcHUiLVc.ranQ/b0.dLsGe8WQI2ygcge0aCwLsmfxVpdnAIi', '超级管理员', 'admin', 1, '', '');
