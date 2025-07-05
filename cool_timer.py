#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时推送程序
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import subprocess
from tkinter import PhotoImage
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class TimerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⏰ 定时推送助手")
        # 只设置一次主窗口icon，优先用ico格式，彻底覆盖tk默认图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'QQ.ico')
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass
        self.root.geometry("1200x700")
        
        # 设置黑色主题
        self.setup_dark_theme()
        
        self.running = False
        self.tasks = []
        
        self.create_interface()
        
    def setup_dark_theme(self):
        """设置黑色主题"""
        self.root.configure(bg='#1a1a1a')
        
        # 定义颜色方案
        self.colors = {
            'bg': '#1a1a1a',
            'fg': '#ffffff',
            'accent': '#00ff88',
            'secondary': '#333333',
            'warning': '#ff6b6b',
            'success': '#4ecdc4',
            'info': '#45b7d1'
        }
        
    def create_interface(self):
        """创建界面"""
        # 主容器
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 标题区域
        title_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        title_frame.pack(fill="x", pady=(0, 5))
        
        title_label = tk.Label(title_frame, 
                              text="⏰ 定时推送助手", 
                              font=("Arial", 16, "bold"),
                              bg=self.colors['bg'],
                              fg=self.colors['accent'])
        title_label.pack()
        
        # 创建三栏布局
        content_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        content_frame.pack(fill="both", expand=True)
        
        # 左侧 - 任务管理
        left_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 3))
        
        self.create_task_section(left_frame)
        
        # 中间 - 推送配置
        middle_frame = tk.Frame(content_frame, bg=self.colors['bg'], width=480)
        middle_frame.pack(side="left", fill="y", padx=3)
        middle_frame.pack_propagate(False)
        # 新建一个内容容器，所有推送设置放这里
        push_content = tk.Frame(middle_frame, bg=self.colors['bg'])
        push_content.pack(fill="both", expand=True)
        self.create_push_section(push_content)
        # --- logo+QQ群号区域放到整个中间栏最下方 ---
        self.create_logo_qq_section(middle_frame)
        
        # 右侧 - 状态和日志
        right_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        right_frame.pack(side="right", fill="both", expand=True, padx=(3, 0))
        
        self.create_status_section(right_frame)
        
    def create_task_section(self, parent):
        """创建任务管理区域"""
        # 任务管理标题
        task_title = tk.Label(parent, 
                             text="📋 任务管理", 
                             font=("Arial", 12, "bold"),
                             bg=self.colors['bg'],
                             fg=self.colors['accent'])
        task_title.pack(anchor="w", pady=(0, 5))
        
        # 任务输入区域
        input_frame = tk.Frame(parent, bg=self.colors['secondary'], relief="raised", bd=1)
        input_frame.pack(fill="x", pady=(0, 5))
        
        # 任务名称
        name_frame = tk.Frame(input_frame, bg=self.colors['secondary'])
        name_frame.pack(fill="x", padx=8, pady=3)
        
        tk.Label(name_frame, text="任务名称:", 
                font=("Arial", 9, "bold"),
                bg=self.colors['secondary'],
                fg=self.colors['fg']).pack(anchor="w")
        
        self.task_name_var = tk.StringVar()
        name_entry = tk.Entry(name_frame, 
                             textvariable=self.task_name_var,
                             font=("Arial", 9),
                             bg=self.colors['bg'],
                             fg=self.colors['fg'],
                             insertbackground=self.colors['accent'],
                             relief="flat",
                             bd=2)
        name_entry.pack(fill="x", pady=(1, 0))
        
        # 执行时间 + 重复设置并排
        time_repeat_frame = tk.Frame(input_frame, bg=self.colors['secondary'])
        time_repeat_frame.pack(fill="x", padx=8, pady=3)
        # 执行时间
        tk.Label(time_repeat_frame, text="执行时间:", font=("Arial", 9, "bold"), bg=self.colors['secondary'], fg=self.colors['fg']).pack(side="left")
        self.task_time_var = tk.StringVar(value="12:00")
        time_entry = tk.Entry(time_repeat_frame, textvariable=self.task_time_var, font=("Arial", 9), bg=self.colors['bg'], fg=self.colors['fg'], insertbackground=self.colors['accent'], relief="flat", bd=2, width=8)
        time_entry.pack(side="left", padx=(2, 8))
        tk.Label(time_repeat_frame, text="(HH:MM)", font=("Arial", 8), bg=self.colors['secondary'], fg=self.colors['fg']).pack(side="left")
        # 重复设置
        tk.Label(time_repeat_frame, text="  重复设置:", font=("Arial", 9, "bold"), bg=self.colors['secondary'], fg=self.colors['fg']).pack(side="left", padx=(8, 0))
        self.task_repeat_var = tk.StringVar(value="每天")
        repeat_combo = ttk.Combobox(time_repeat_frame, textvariable=self.task_repeat_var, values=["一次", "每天", "每周", "每月"], font=("Arial", 9), state="readonly", width=10)
        repeat_combo.pack(side="left", padx=(2, 0))
        
        # 按钮区域（优化字体+高亮）
        button_frame = tk.Frame(input_frame, bg=self.colors['secondary'])
        button_frame.pack(fill="x", padx=8, pady=5)
        btn_font = ("Arial", 11, "bold")
        btns = []
        btn_cfgs = [
            ("➕ 添加", self.add_task, self.colors['success'], '#36ffe0'),
            ("🗑️ 删除", self.delete_task, self.colors['warning'], '#ff3333', 'w'),
            ("▶️ 启动", self.start_timer, self.colors['accent'], '#00cc66'),
            ("⏹️ 停止", self.stop_timer, self.colors['info'], '#1e90ff'),
        ]
        for i, cfg in enumerate(btn_cfgs):
            if len(cfg) == 4:
                text, cmd, color, hover = cfg
                anchor = 'center'
            else:
                text, cmd, color, hover, anchor = cfg
            btn = tk.Button(button_frame, text=text, command=cmd, font=btn_font, bg=color, fg='#FFFFFF', relief="flat", bd=0, padx=12, pady=5, activebackground=hover, anchor=anchor)
            btn.pack(side="left", padx=(0, 5))
            def on_enter(e, b=btn, c=hover): b.config(bg=c)
            def on_leave(e, b=btn, c=color): b.config(bg=c)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            btns.append(btn)
        
        # 任务列表
        list_frame = tk.Frame(parent, bg=self.colors['secondary'], relief="raised", bd=1)
        list_frame.pack(fill="both", expand=True)
        
        tk.Label(list_frame, text="当前任务列表", 
                font=("Arial", 9, "bold"),
                bg=self.colors['secondary'],
                fg=self.colors['accent']).pack(pady=3)
        
        # 创建带滚动条的列表框
        list_container = tk.Frame(list_frame, bg=self.colors['secondary'])
        list_container.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        
        self.task_listbox = tk.Listbox(list_container,
                                      bg=self.colors['bg'],
                                      fg=self.colors['fg'],
                                      selectbackground=self.colors['accent'],
                                      selectforeground='#000000',
                                      font=("Arial", 9),
                                      relief="flat",
                                      bd=0,
                                      height=8)
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side="right", fill="y")
        
        self.task_listbox.pack(side="left", fill="both", expand=True)
        self.task_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.task_listbox.yview)
        
    def create_push_section(self, parent):
        """创建推送配置区域"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # 推送配置标题
        push_title = tk.Label(parent, 
                             text="📤 推送配置", 
                             font=("Arial", 12, "bold"),
                             bg=self.colors['bg'],
                             fg=self.colors['accent'])
        push_title.pack(anchor="w", pady=(0, 5))
        
        # 推送方式选择
        push_type_frame = tk.Frame(parent, bg=self.colors['secondary'], relief="raised", bd=1)
        push_type_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(push_type_frame, text="推送方式", 
                font=("Arial", 9, "bold"),
                bg=self.colors['secondary'],
                fg=self.colors['accent']).pack(pady=3)
        
        self.push_type_var = tk.StringVar(value="smtp")
        
        smtp_radio = tk.Radiobutton(push_type_frame, 
                                   text="📧 SMTP邮箱",
                                   variable=self.push_type_var,
                                   value="smtp",
                                   command=self.toggle_push_type,
                                   font=("Arial", 9, "bold"),
                                   bg=self.colors['secondary'],
                                   fg=self.colors['fg'],
                                   selectcolor=self.colors['accent'])
        smtp_radio.pack(anchor="w", padx=8, pady=1)
        
        http_radio = tk.Radiobutton(push_type_frame,
                                   text="🌐 HTTP API",
                                   variable=self.push_type_var,
                                   value="http",
                                   command=self.toggle_push_type,
                                   font=("Arial", 9, "bold"),
                                   bg=self.colors['secondary'],
                                   fg=self.colors['fg'],
                                   selectcolor=self.colors['accent'])
        http_radio.pack(anchor="w", padx=8, pady=1)
        
        # SMTP配置
        self.smtp_frame = tk.Frame(parent, bg=self.colors['secondary'], relief="raised", bd=1)
        self.smtp_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(self.smtp_frame, text="SMTP设置", 
                font=("Arial", 9, "bold"),
                bg=self.colors['secondary'],
                fg=self.colors['accent']).pack(pady=3)
        
        # SMTP配置项
        smtp_configs = [
            ("邮箱服务器:", "smtp.qq.com", "smtp_server_var"),
            ("邮箱账号:", "", "smtp_user_var"),
            ("邮箱密码:", "", "smtp_pass_var", True),
            ("收件人:", "", "to_email_var"),
            ("邮件主题:", "定时提醒", "email_subject_var")
        ]
        
        for i, (label, default, var_name, *args) in enumerate(smtp_configs):
            frame = tk.Frame(self.smtp_frame, bg=self.colors['secondary'])
            frame.pack(fill="x", padx=8, pady=1)
            
            tk.Label(frame, text=label, 
                    font=("Arial", 9),
                    bg=self.colors['secondary'],
                    fg=self.colors['fg']).pack(anchor="w")
            
            var = tk.StringVar(value=default)
            setattr(self, var_name, var)
            
            entry = tk.Entry(frame,
                           textvariable=var,
                           font=("Arial", 9),
                           bg=self.colors['bg'],
                           fg=self.colors['fg'],
                           insertbackground=self.colors['accent'],
                           relief="flat",
                           bd=1,
                           show="*" if args and args[0] else None)
            entry.pack(fill="x", pady=(1, 0))
        
        # 邮件内容
        content_frame = tk.Frame(self.smtp_frame, bg=self.colors['secondary'])
        content_frame.pack(fill="x", padx=8, pady=1)
        
        tk.Label(content_frame, text="邮件内容:", 
                font=("Arial", 9),
                bg=self.colors['secondary'],
                fg=self.colors['fg']).pack(anchor="w")
        
        self.email_content_text = tk.Text(content_frame,
                                         height=2,
                                         font=("Arial", 9),
                                         bg=self.colors['bg'],
                                         fg=self.colors['fg'],
                                         insertbackground=self.colors['accent'],
                                         relief="flat",
                                         bd=1)
        self.email_content_text.pack(fill="x", pady=(1, 0))
        self.email_content_text.insert("1.0", "这是一条定时提醒消息！")
        
        # HTTP API配置
        self.http_frame = tk.Frame(parent, bg=self.colors['secondary'], relief="raised", bd=1)
        
        tk.Label(self.http_frame, text="HTTP API设置", 
                font=("Arial", 9, "bold"),
                bg=self.colors['secondary'],
                fg=self.colors['accent']).pack(pady=3)
        
        # HTTP API配置项
        http_configs = [
            ("API地址:", "", "api_url_var"),
            ("请求方法:", "POST", "api_method_var"),
            ("请求头:", '{"Content-Type": "application/json"}', "api_headers_var")
        ]
        
        for label, default, var_name in http_configs:
            frame = tk.Frame(self.http_frame, bg=self.colors['secondary'])
            frame.pack(fill="x", padx=8, pady=1)
            
            tk.Label(frame, text=label, 
                    font=("Arial", 9),
                    bg=self.colors['secondary'],
                    fg=self.colors['fg']).pack(anchor="w")
            
            var = tk.StringVar(value=default)
            setattr(self, var_name, var)
            
            if var_name == "api_method_var":
                combo = ttk.Combobox(frame,
                                   textvariable=var,
                                   values=["GET", "POST", "PUT"],
                                   font=("Arial", 9),
                                   state="readonly")
                combo.pack(fill="x", pady=(1, 0))
            else:
                entry = tk.Entry(frame,
                               textvariable=var,
                               font=("Arial", 9),
                               bg=self.colors['bg'],
                               fg=self.colors['fg'],
                               insertbackground=self.colors['accent'],
                               relief="flat",
                               bd=1)
                entry.pack(fill="x", pady=(1, 0))
        
        # 请求体
        body_frame = tk.Frame(self.http_frame, bg=self.colors['secondary'])
        body_frame.pack(fill="x", padx=8, pady=1)
        
        tk.Label(body_frame, text="请求体:", 
                font=("Arial", 9),
                bg=self.colors['secondary'],
                fg=self.colors['fg']).pack(anchor="w")
        
        self.api_body_text = tk.Text(body_frame,
                                    height=2,
                                    font=("Arial", 9),
                                    bg=self.colors['bg'],
                                    fg=self.colors['fg'],
                                    insertbackground=self.colors['accent'],
                                    relief="flat",
                                    bd=1)
        self.api_body_text.pack(fill="x", pady=(1, 0))
        self.api_body_text.insert("1.0", '{"message": "定时提醒"}')
        
        # 测试按钮
        test_btn = tk.Button(parent, text="🧪 测试推送", command=self.test_push, font=("Arial", 10, "bold"), bg=self.colors['accent'], fg='#000000', relief="flat", bd=0, padx=18, pady=7)
        test_btn.pack(pady=5)
        
    def create_logo_qq_section(self, parent):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_qq_frame = tk.Frame(parent, bg=self.colors['bg'])
        logo_qq_frame.pack(side="bottom", fill="x", padx=8, pady=20, anchor="s")
        # LOGO
        logo_path = os.path.join(base_dir, 'bin', 'logo.png')
        print(f"尝试加载LOGO: {logo_path}")
        logo_img = None
        if os.path.exists(logo_path):
            try:
                if PIL_AVAILABLE:
                    img = Image.open(logo_path)
                    img = img.resize((193, 61), Image.LANCZOS)
                    logo_img = ImageTk.PhotoImage(img)
                else:
                    logo_img = PhotoImage(file=logo_path)
            except Exception as e:
                print(f"❌ LOGO加载失败: {e}")
                logo_img = None
        else:
            print(f"❌ LOGO文件不存在: {logo_path}")
        if logo_img:
            self.logo_img = logo_img
            logo_label = tk.Label(logo_qq_frame, image=self.logo_img, bg=self.colors['bg'], cursor="hand2")
            logo_label.pack(side="left", padx=(0, 20))
            logo_label.bind("<Button-1>", lambda e: self.open_logo_link())
        else:
            logo_label = tk.Label(logo_qq_frame, text="[LOGO加载失败]", fg="#12B7F5", bg=self.colors['bg'], cursor="hand2")
            logo_label.pack(side="left", padx=(0, 20))
            logo_label.bind("<Button-1>", lambda e: self.open_logo_link())
        # QQ图标+群号
        qq_frame = tk.Frame(logo_qq_frame, bg=self.colors['bg'])
        qq_frame.pack(side="left")
        qq_icon = None
        qq_icon_path = os.path.join(base_dir, 'bin', 'QQ.png')
        print(f"尝试加载QQ图标: {qq_icon_path}")
        if os.path.exists(qq_icon_path):
            try:
                if PIL_AVAILABLE:
                    img = Image.open(qq_icon_path)
                    img = img.resize((48, 48), Image.LANCZOS)
                    qq_icon = ImageTk.PhotoImage(img)
                else:
                    qq_icon = PhotoImage(file=qq_icon_path)
            except Exception as e:
                print(f"❌ QQ图标加载失败: {e}")
                qq_icon = None
        else:
            print(f"❌ QQ图标文件不存在: {qq_icon_path}")
        if qq_icon:
            self.qq_icon = qq_icon
            qq_img_label = tk.Label(qq_frame, image=self.qq_icon, bg=self.colors['bg'], cursor="hand2")
            qq_img_label.pack(side="left")
            qq_img_label.bind("<Button-1>", lambda e: self.open_qq_group())
        else:
            qq_img_label = tk.Label(qq_frame, text="[QQ图标加载失败]", fg="#12B7F5", bg=self.colors['bg'], cursor="hand2")
            qq_img_label.pack(side="left")
            qq_img_label.bind("<Button-1>", lambda e: self.open_qq_group())
        qq_num_label = tk.Label(qq_frame, text="群号 1055867603", font=("Arial", 18, "bold"), fg="#12B7F5", bg=self.colors['bg'], cursor="hand2")
        qq_num_label.pack(side="left", padx=(12, 0))
        qq_num_label.bind("<Button-1>", lambda e: self.open_qq_group())
        
        # 初始显示SMTP配置
        self.toggle_push_type()
        
    def create_status_section(self, parent):
        """创建状态和日志区域"""
        # 状态栏
        status_frame = tk.Frame(parent, bg=self.colors['secondary'], relief="raised", bd=1)
        status_frame.pack(fill="x", pady=(0, 5))
        
        # 状态和QQ群链接
        status_link_frame = tk.Frame(status_frame, bg=self.colors['secondary'])
        status_link_frame.pack(fill="x", padx=8, pady=3)
        
        # 状态显示
        self.status_var = tk.StringVar(value="状态: 未运行")
        status_label = tk.Label(status_link_frame,
                               textvariable=self.status_var,
                               font=("Arial", 9, "bold"),
                               bg=self.colors['secondary'],
                               fg=self.colors['accent'])
        status_label.pack(side="left")
        
        # 删除右上角QQ群按钮（不再创建qq_button）
        
        # 日志显示
        log_frame = tk.Frame(parent, bg=self.colors['secondary'], relief="raised", bd=1)
        log_frame.pack(fill="both", expand=True)
        
        tk.Label(log_frame, text="运行日志", 
                font=("Arial", 9, "bold"),
                bg=self.colors['secondary'],
                fg=self.colors['accent']).pack(pady=3)
        
        self.log_text = tk.Text(log_frame,
                               height=15,
                               font=("Consolas", 8),
                               bg=self.colors['bg'],
                               fg=self.colors['fg'],
                               insertbackground=self.colors['accent'],
                               relief="flat",
                               bd=0)
        self.log_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        # 日志组件创建好后输出QQ图标加载信息
        if hasattr(self, 'log_text'):
            try:
                self.log_message(f"尝试加载QQ图标: {os.path.abspath(os.path.join('bin', 'QQ.png'))}")
            except Exception:
                pass
        
    def toggle_push_type(self):
        """切换推送方式"""
        if self.push_type_var.get() == "smtp":
            self.smtp_frame.pack(fill="x", pady=(0, 5))
            self.http_frame.pack_forget()
        else:
            self.smtp_frame.pack_forget()
            self.http_frame.pack(fill="x", pady=(0, 5))
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f'[{timestamp}] {message}\n'
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update()
    
    def send_email(self, smtp_server, smtp_user, smtp_pass, to_email, subject, content):
        """发送邮件"""
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(smtp_server, 587)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            
            self.log_message(f'✅ 邮件发送成功: {to_email}')
            return True
        except Exception as e:
            self.log_message(f'❌ 邮件发送失败: {str(e)}')
            return False
    
    def send_http_api(self, url, method, headers, body):
        """发送HTTP API请求"""
        try:
            headers_dict = json.loads(headers) if headers else {}
            body_dict = json.loads(body) if body else {}
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers_dict, params=body_dict)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers_dict, json=body_dict)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers_dict, json=body_dict)
            
            if response.status_code in [200, 201]:
                self.log_message(f'✅ HTTP API请求成功: {url}')
                return True
            else:
                self.log_message(f'❌ HTTP API请求失败: {response.status_code}')
                return False
        except Exception as e:
            self.log_message(f'❌ HTTP API请求失败: {str(e)}')
            return False
    
    def execute_task(self, task):
        """执行任务"""
        self.log_message(f'🚀 执行任务: {task["name"]}')
        
        if self.push_type_var.get() == "smtp":
            smtp_server = self.smtp_server_var.get()
            smtp_user = self.smtp_user_var.get()
            smtp_pass = self.smtp_pass_var.get()
            to_email = self.to_email_var.get()
            subject = self.email_subject_var.get()
            content = self.email_content_text.get("1.0", tk.END).strip()
            
            self.send_email(smtp_server, smtp_user, smtp_pass, to_email, subject, content)
        else:
            url = self.api_url_var.get()
            method = self.api_method_var.get()
            headers = self.api_headers_var.get()
            body = self.api_body_text.get("1.0", tk.END).strip()
            
            self.send_http_api(url, method, headers, body)
    
    def timer_thread(self):
        """定时器线程"""
        while self.running:
            current_time = datetime.now().strftime('%H:%M')
            
            for task in self.tasks:
                if task['time'] == current_time and not task.get('executed_today', False):
                    self.execute_task(task)
                    task['executed_today'] = True
            
            if current_time == '00:00':
                for task in self.tasks:
                    task['executed_today'] = False
            
            time.sleep(30)
    
    def start_timer(self):
        """启动定时器"""
        if not self.running:
            self.running = True
            self.log_message('🟢 定时器已启动')
            self.status_var.set('状态: 运行中')
            
            timer_thread = threading.Thread(target=self.timer_thread, daemon=True)
            timer_thread.start()
    
    def stop_timer(self):
        """停止定时器"""
        self.running = False
        self.log_message('🔴 定时器已停止')
        self.status_var.set('状态: 已停止')
    
    def add_task(self):
        """添加任务"""
        task_name = self.task_name_var.get()
        task_time = self.task_time_var.get()
        task_repeat = self.task_repeat_var.get()
        
        if not task_name or not task_time:
            messagebox.showwarning("警告", "请填写任务名称和执行时间")
            return
        
        try:
            datetime.strptime(task_time, '%H:%M')
        except ValueError:
            messagebox.showerror("错误", "时间格式错误，请使用HH:MM格式")
            return
        
        task = {
            'name': task_name,
            'time': task_time,
            'repeat': task_repeat,
            'executed_today': False
        }
        
        self.tasks.append(task)
        self.log_message(f'✅ 添加任务成功: {task_name} ({task_time})')
        
        self.task_name_var.set('')
        self.task_time_var.set('12:00')
        self.update_task_list()
    
    def delete_task(self):
        """删除任务"""
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的任务")
            return
        
        for index in reversed(selection):
            if index < len(self.tasks):
                deleted_task = self.tasks.pop(index)
                self.log_message(f'🗑️ 删除任务: {deleted_task["name"]}')
        
        self.update_task_list()
    
    def update_task_list(self):
        """更新任务列表"""
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, f"{task['name']} - {task['time']} ({task['repeat']})")
    
    def open_qq_group(self):
        """打开QQ群链接"""
        try:
            # 使用系统默认浏览器打开链接
            subprocess.run(['start', 'https://qm.qq.com/q/RAqkqsrQEq'], shell=True)
            self.log_message("🔗 正在打开QQ群链接...")
        except Exception as e:
            self.log_message(f"❌ 打开QQ群链接失败: {str(e)}")
    
    def test_push(self):
        """测试推送"""
        self.log_message('🧪 开始测试推送...')
        
        if self.push_type_var.get() == "smtp":
            smtp_server = self.smtp_server_var.get()
            smtp_user = self.smtp_user_var.get()
            smtp_pass = self.smtp_pass_var.get()
            to_email = self.to_email_var.get()
            subject = self.email_subject_var.get()
            content = self.email_content_text.get("1.0", tk.END).strip()
            
            if not all([smtp_server, smtp_user, smtp_pass, to_email]):
                messagebox.showerror("错误", "请填写完整的SMTP配置")
                return
            
            self.send_email(smtp_server, smtp_user, smtp_pass, to_email, subject, content)
        else:
            url = self.api_url_var.get()
            method = self.api_method_var.get()
            headers = self.api_headers_var.get()
            body = self.api_body_text.get("1.0", tk.END).strip()
            
            if not url:
                messagebox.showerror("错误", "请填写API地址")
                return
            
            self.send_http_api(url, method, headers, body)
    
    def run(self):
        """运行程序"""
        self.root.mainloop()

    def open_logo_link(self):
        try:
            subprocess.run(['start', 'https://bbs.125.la/'], shell=True)
            self.log_message("🔗 正在打开精易论坛链接...")
        except Exception as e:
            self.log_message(f"❌ 打开精易论坛链接失败: {str(e)}")

if __name__ == '__main__':
    app = TimerApp()
    app.run() 