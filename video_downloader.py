#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, font
import threading
import queue
import os
import re
from pathlib import Path
import yt_dlp
from urllib.parse import urlparse
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import ssl
import certifi
import sys


class VideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("智能视频下载工具 V3 ✨")
        self.root.geometry("1100x800")
        
        # 设置主题颜色
        self.colors = {
            'primary': '#FFFFFF',  # 白色
            'primary_dark': '#F0F0F0',  # 浅灰
            'success': '#FFFFFF',  # 白色
            'error': '#FFFFFF',  # 白色
            'warning': '#FFFFFF',  # 白色
            'bg': '#F5F5F5',
            'card_bg': '#FFFFFF',
            'text': '#000000',  # 纯黑色
            'text_secondary': '#000000',  # 纯黑色
            'border': '#E0E0E0',
            'progress_bg': '#E3F2FD',
            'hover': '#E8F5FF'
        }
        
        # 设置窗口背景
        self.root.configure(bg=self.colors['bg'])
        
        # 配置ttk样式
        self.setup_styles()
        
        # 设置SSL证书
        self.setup_ssl_certificates()
        
        # 设置默认值
        self.default_download_path = str(Path.home() / "Downloads")
        self.max_concurrent = 3
        self.download_queue = queue.Queue()
        self.active_downloads = {}
        self.download_executor = None
        self.stop_event = threading.Event()
        self.total_videos = 0
        self.completed_videos = 0
        self.failed_videos = 0
        self.current_speed = {}
        self.download_start_time = {}
        
        # 创建GUI
        self.setup_ui()
        
        # 启动下载线程
        self.start_download_thread()
        
    def setup_styles(self):
        """设置ttk组件样式"""
        style = ttk.Style()
        
        # 设置主题
        style.theme_use('clam')
        
        # 配置颜色
        style.configure('Title.TLabel', 
                       font=('Microsoft YaHei', 24, 'bold'),
                       foreground=self.colors['primary'])
        
        style.configure('Heading.TLabel',
                       font=('Microsoft YaHei', 11, 'bold'),
                       foreground=self.colors['text'])
        
        style.configure('Card.TFrame',
                       background=self.colors['card_bg'],
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Primary.TButton',
                       font=('Microsoft YaHei', 10),
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary_dark']),
                           ('!active', self.colors['primary'])])
        
        style.configure('Danger.TButton',
                       font=('Microsoft YaHei', 10),
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Danger.TButton',
                 background=[('active', '#D32F2F'),
                           ('!active', self.colors['error'])])
        
        # 进度条样式使用默认布局
        style.configure('TProgressbar',
                       background=self.colors['success'],
                       troughcolor=self.colors['progress_bg'],
                       borderwidth=0)
        
    def setup_ssl_certificates(self):
        """设置SSL证书以解决打包后的证书验证问题"""
        try:
            os.environ['SSL_CERT_FILE'] = certifi.where()
            os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
            ssl._create_default_https_context = ssl._create_unverified_context
        except Exception as e:
            print(f"SSL证书设置警告: {e}")
        
    def setup_ui(self):
        # 创建主容器
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 标题区域
        title_frame = tk.Frame(main_container, bg=self.colors['bg'])
        title_frame.pack(fill='x', pady=(0, 20))
        
        title = tk.Label(title_frame, 
                        text="🎥 智能视频下载工具",
                        font=('Microsoft YaHei', 28, 'bold'),
                        fg='#000000',
                        bg=self.colors['bg'])
        title.pack(side='left')
        
        # 统计信息
        stats_frame = tk.Frame(title_frame, bg=self.colors['bg'])
        stats_frame.pack(side='right', padx=20)
        
        self.stats_label = tk.Label(stats_frame,
                                   text="准备就绪",
                                   font=('Microsoft YaHei', 11),
                                   fg='#000000',
                                   bg=self.colors['bg'])
        self.stats_label.pack()
        
        # 输入区域卡片
        input_card = self.create_card(main_container, "视频链接")
        input_card.pack(fill='both', expand=True, pady=(0, 15))
        
        # URL输入提示
        hint_label = tk.Label(input_card,
                            text="💡 提示：每行输入一个视频链接，支持YouTube、Bilibili等主流平台",
                            font=('Microsoft YaHei', 10),
                            fg='#000000',
                            bg=self.colors['card_bg'])
        hint_label.pack(anchor='w', pady=(5, 5))
        
        # URL输入框
        text_frame = tk.Frame(input_card, bg=self.colors['card_bg'])
        text_frame.pack(fill='both', expand=True)
        
        self.url_text = tk.Text(text_frame, 
                               height=6,
                               font=('Consolas', 11),
                               relief='solid',
                               borderwidth=1,
                               wrap='word')
        url_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.url_text.yview)
        self.url_text.configure(yscrollcommand=url_scrollbar.set)
        
        self.url_text.pack(side='left', fill='both', expand=True)
        url_scrollbar.pack(side='right', fill='y')
        
        # 设置区域
        settings_card = self.create_card(main_container, "下载设置")
        settings_card.pack(fill='x', pady=(0, 15))
        
        settings_grid = tk.Frame(settings_card, bg=self.colors['card_bg'])
        settings_grid.pack(fill='x', pady=10)
        
        # 下载路径
        path_frame = tk.Frame(settings_grid, bg=self.colors['card_bg'])
        path_frame.pack(fill='x', pady=5)
        
        tk.Label(path_frame,
                text="📁 下载路径:",
                font=('Microsoft YaHei', 11),
                fg='#000000',
                bg=self.colors['card_bg']).pack(side='left', padx=(0, 10))
        
        self.path_var = tk.StringVar(value=self.default_download_path)
        path_entry = tk.Entry(path_frame,
                            textvariable=self.path_var,
                            font=('Microsoft YaHei', 11),
                            relief='solid',
                            borderwidth=1)
        path_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(path_frame,
                             text="浏览",
                             font=('Microsoft YaHei', 11),
                             bg='white',
                             fg='black',
                             activebackground='#F0F0F0',
                             activeforeground='black',
                             relief='solid',
                             bd=1,
                             padx=20,
                             cursor='hand2',
                             command=self.browse_folder)
        browse_btn.pack(side='right')
        
        # 并发数设置
        concurrent_frame = tk.Frame(settings_grid, bg=self.colors['card_bg'])
        concurrent_frame.pack(fill='x', pady=5)
        
        tk.Label(concurrent_frame,
                text="⚡ 并发下载数:",
                font=('Microsoft YaHei', 11),
                fg='#000000',
                bg=self.colors['card_bg']).pack(side='left', padx=(0, 10))
        
        self.concurrent_var = tk.IntVar(value=self.max_concurrent)
        concurrent_spinbox = ttk.Spinbox(concurrent_frame,
                                       from_=1, to=10,
                                       width=10,
                                       font=('Microsoft YaHei', 11),
                                       textvariable=self.concurrent_var,
                                       command=self.update_concurrent)
        concurrent_spinbox.pack(side='left')
        
        tk.Label(concurrent_frame,
                text="(建议3-5，过高可能导致限速)",
                font=('Microsoft YaHei', 10),
                fg='#000000',
                bg=self.colors['card_bg']).pack(side='left', padx=(10, 0))
        
        # 控制按钮
        button_frame = tk.Frame(main_container, bg=self.colors['bg'])
        button_frame.pack(fill='x', pady=(0, 15))
        
        self.download_btn = tk.Button(button_frame,
                                     text="▶ 开始下载",
                                     font=('Microsoft YaHei', 12, 'bold'),
                                     bg='white',
                                     fg='black',
                                     activebackground='#F0F0F0',
                                     activeforeground='black',
                                     relief='solid',
                                     bd=1,
                                     padx=35,
                                     pady=12,
                                     cursor='hand2',
                                     command=self.start_download)
        self.download_btn.pack(side='left', padx=(0, 10))
        
        self.stop_btn = tk.Button(button_frame,
                                text="⏸ 停止下载",
                                font=('Microsoft YaHei', 12, 'bold'),
                                bg='white',
                                fg='black',
                                activebackground='#F0F0F0',
                                activeforeground='black',
                                relief='solid',
                                bd=1,
                                padx=35,
                                pady=12,
                                state='disabled',
                                cursor='hand2',
                                command=self.stop_download)
        self.stop_btn.pack(side='left')
        
        # 进度显示区域
        progress_card = self.create_card(main_container, "下载进度")
        progress_card.pack(fill='both', expand=True, pady=(0, 15))
        
        # 整体进度
        overall_frame = tk.Frame(progress_card, bg=self.colors['card_bg'])
        overall_frame.pack(fill='x', pady=(10, 15))
        
        tk.Label(overall_frame,
                text="📊 整体进度:",
                font=('Microsoft YaHei', 12, 'bold'),
                fg='#000000',
                bg=self.colors['card_bg']).pack(side='left', padx=(0, 10))
        
        progress_container = tk.Frame(overall_frame, bg=self.colors['card_bg'])
        progress_container.pack(side='left', fill='x', expand=True)
        
        self.overall_progress = ttk.Progressbar(progress_container,
                                               mode='determinate')
        self.overall_progress.pack(fill='x')
        
        self.overall_label = tk.Label(overall_frame,
                                     text="0/0 (0%)",
                                     font=('Microsoft YaHei', 11, 'bold'),
                                     fg='#000000',
                                     bg=self.colors['card_bg'])
        self.overall_label.pack(side='right', padx=(10, 0))
        
        # 单个视频进度容器
        progress_container = tk.Frame(progress_card, bg=self.colors['card_bg'])
        progress_container.pack(fill='both', expand=True, pady=(0, 10))
        
        # 创建Canvas和滚动条
        canvas = tk.Canvas(progress_container,
                         bg=self.colors['card_bg'],
                         highlightthickness=0,
                         height=200)
        scrollbar = ttk.Scrollbar(progress_container, orient="vertical", command=canvas.yview)
        self.progress_inner_frame = tk.Frame(canvas, bg=self.colors['card_bg'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas_frame = canvas.create_window((0, 0), window=self.progress_inner_frame, anchor="nw")
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.progress_inner_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # 日志区域
        log_card = self.create_card(main_container, "下载日志")
        log_card.pack(fill='both', expand=True)
        
        log_frame = tk.Frame(log_card, bg=self.colors['card_bg'])
        log_frame.pack(fill='both', expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame,
                              height=8,
                              font=('Consolas', 10),
                              relief='solid',
                              borderwidth=1,
                              wrap='word',
                              bg='#FAFAFA',
                              fg='#000000')
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
        # 配置日志标签颜色（全部使用黑色，通过加粗区分）
        self.log_text.tag_config('INFO', foreground='#000000')
        self.log_text.tag_config('SUCCESS', foreground='#000000', font=('Consolas', 10, 'bold'))
        self.log_text.tag_config('ERROR', foreground='#000000', font=('Consolas', 10, 'bold'))
        self.log_text.tag_config('WARNING', foreground='#000000', font=('Consolas', 10, 'bold'))
        
        # 存储进度条组件
        self.progress_widgets = {}
        
    def create_card(self, parent, title):
        """创建卡片容器"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='solid', borderwidth=1)
        
        # 标题
        title_label = tk.Label(card,
                             text=title,
                             font=('Microsoft YaHei', 13, 'bold'),
                             fg='#000000',
                             bg=self.colors['card_bg'])
        title_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        # 分隔线
        separator = tk.Frame(card, height=1, bg=self.colors['border'])
        separator.pack(fill='x', padx=15, pady=(0, 10))
        
        return card
        
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.path_var.get())
        if folder:
            self.path_var.set(folder)
            
    def update_concurrent(self):
        self.max_concurrent = self.concurrent_var.get()
        
    def validate_url(self, url):
        """验证URL是否有效"""
        url = url.strip()
        if not url:
            return False
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    def parse_urls(self):
        """解析并验证输入的URLs"""
        text = self.url_text.get("1.0", tk.END)
        lines = text.strip().split('\n')
        
        urls = []
        invalid_lines = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            if self.validate_url(line):
                if line not in urls:
                    urls.append(line)
            else:
                invalid_lines.append(f"第{i}行: {line}")
                
        return urls, invalid_lines
        
    def log_message(self, message, level="INFO"):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        icons = {
            'INFO': 'ℹ',
            'SUCCESS': '✅',
            'ERROR': '❌',
            'WARNING': '⚠'
        }
        
        icon = icons.get(level, 'ℹ')
        log_entry = f"[{timestamp}] {icon} {message}\n"
        
        self.root.after(0, lambda: self._update_log(log_entry, level))
        
    def _update_log(self, log_entry, level):
        """在主线程中更新日志"""
        self.log_text.insert(tk.END, log_entry, level)
        self.log_text.see(tk.END)
        
    def update_stats(self):
        """更新统计信息"""
        if self.total_videos > 0:
            success_rate = ((self.completed_videos - self.failed_videos) / self.total_videos * 100)
            stats_text = f"✅ 成功: {self.completed_videos - self.failed_videos} | ❌ 失败: {self.failed_videos} | 📊 成功率: {success_rate:.1f}%"
        else:
            stats_text = "准备就绪"
        
        self.stats_label.config(text=stats_text)
        
    def start_download(self):
        """开始下载"""
        urls, invalid_lines = self.parse_urls()
        
        if invalid_lines:
            messagebox.showwarning("无效链接",
                                 "以下行包含无效链接:\n" + "\n".join(invalid_lines[:10]) +
                                 ("..." if len(invalid_lines) > 10 else ""))
            
        if not urls:
            messagebox.showerror("错误", "请输入至少一个有效的视频链接")
            return
            
        download_path = self.path_var.get()
        if not os.path.exists(download_path):
            if messagebox.askyesno("目录不存在", f"目录 {download_path} 不存在，是否创建？"):
                try:
                    os.makedirs(download_path)
                    self.log_message(f"创建目录: {download_path}")
                except Exception as e:
                    messagebox.showerror("错误", f"创建目录失败: {str(e)}")
                    return
            else:
                return
                
        # 准备下载
        self.total_videos = len(urls)
        self.completed_videos = 0
        self.failed_videos = 0
        self.stop_event.clear()
        
        # 更新UI状态
        self.download_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.url_text.config(state='disabled')
        
        # 清空进度条
        for widget in self.progress_inner_frame.winfo_children():
            widget.destroy()
        self.progress_widgets.clear()
        
        # 更新整体进度
        self.overall_progress['maximum'] = self.total_videos
        self.overall_progress['value'] = 0
        self.overall_label.config(text=f"0/{self.total_videos} (0%)")
        self.update_stats()
        
        # 添加URL到队列
        for url in urls:
            self.download_queue.put(url)
            
        self.log_message(f"开始下载 {self.total_videos} 个视频", "INFO")
        
        # 创建线程池
        self.download_executor = ThreadPoolExecutor(max_workers=self.max_concurrent)
        
        # 启动下载任务
        for _ in range(min(self.max_concurrent, self.total_videos)):
            self.download_executor.submit(self.download_worker)
            
    def stop_download(self):
        """停止下载"""
        self.stop_event.set()
        self.log_message("正在停止下载...", "WARNING")
        
        if self.download_executor:
            self.download_executor.shutdown(wait=False)
            
        while not self.download_queue.empty():
            try:
                self.download_queue.get_nowait()
            except:
                pass
                
        self.download_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.url_text.config(state='normal')
        
        self.log_message("下载已停止", "WARNING")
        
    def create_progress_widget(self, url):
        """创建单个视频的进度条"""
        # 主容器
        container = tk.Frame(self.progress_inner_frame,
                           bg='white',
                           relief='solid',
                           borderwidth=1)
        container.pack(fill='x', padx=10, pady=5)
        
        # 内部框架
        frame = tk.Frame(container, bg='white')
        frame.pack(fill='x', padx=10, pady=10)
        
        # 标题和状态行
        title_row = tk.Frame(frame, bg='white')
        title_row.pack(fill='x', pady=(0, 5))
        
        # 视频标题
        title = url.split('/')[-1][:40] + "..." if len(url) > 40 else url
        title_label = tk.Label(title_row,
                             text=f"📹 {title}",
                             font=('Microsoft YaHei', 10, 'bold'),
                             fg='#000000',
                             bg='white',
                             anchor='w')
        title_label.pack(side='left', fill='x', expand=True)
        
        # 状态标签
        status_label = tk.Label(title_row,
                              text="准备中",
                              font=('Microsoft YaHei', 10),
                              fg='#000000',
                              bg='white')
        status_label.pack(side='right')
        
        # 进度条行
        progress_row = tk.Frame(frame, bg='white')
        progress_row.pack(fill='x', pady=(0, 5))
        
        progress = ttk.Progressbar(progress_row,
                                  mode='determinate')
        progress.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        percent_label = tk.Label(progress_row,
                               text="0%",
                               font=('Microsoft YaHei', 10, 'bold'),
                               fg='#000000',
                               bg='white',
                               width=6)
        percent_label.pack(side='right')
        
        # 详细信息行
        info_row = tk.Frame(frame, bg='white')
        info_row.pack(fill='x')
        
        info_label = tk.Label(info_row,
                            text="等待开始...",
                            font=('Microsoft YaHei', 9),
                            fg='#000000',
                            bg='white',
                            anchor='w')
        info_label.pack(side='left')
        
        speed_label = tk.Label(info_row,
                             text="",
                             font=('Microsoft YaHei', 9),
                             fg='#000000',
                             bg='white')
        speed_label.pack(side='right')
        
        return {
            'container': container,
            'title': title_label,
            'progress': progress,
            'percent': percent_label,
            'status': status_label,
            'info': info_label,
            'speed': speed_label
        }
        
    def update_progress(self, url, progress_info):
        """更新进度信息"""
        if url not in self.progress_widgets:
            self.root.after(0, lambda: self._create_progress_widget_main(url))
            time.sleep(0.1)
            
        if url in self.progress_widgets:
            self.root.after(0, lambda: self._update_progress_main(url, progress_info))
            
    def _create_progress_widget_main(self, url):
        """在主线程中创建进度条"""
        self.progress_widgets[url] = self.create_progress_widget(url)
        self.download_start_time[url] = time.time()
        
    def _update_progress_main(self, url, progress_info):
        """在主线程中更新进度"""
        if url not in self.progress_widgets:
            return
            
        widgets = self.progress_widgets[url]
        
        if progress_info.get('status') == 'parsing':
            widgets['progress']['value'] = 0
            widgets['percent'].config(text="0%")
            widgets['status'].config(text="🔍 解析中", fg='#000000')
            widgets['info'].config(text="正在获取视频信息...")
            
            # 更新标题
            if progress_info.get('title'):
                title = progress_info['title'][:40] + "..." if len(progress_info['title']) > 40 else progress_info['title']
                widgets['title'].config(text=f"📹 {title}")
                
        elif progress_info.get('status') == 'preparing':
            widgets['progress']['value'] = 0
            widgets['percent'].config(text="0%")
            widgets['status'].config(text="⏳ 准备中", fg='#000000')
            widgets['info'].config(text="准备开始下载...")
            
            # 更新标题
            if progress_info.get('title'):
                title = progress_info['title'][:40] + "..." if len(progress_info['title']) > 40 else progress_info['title']
                widgets['title'].config(text=f"📹 {title}")
                
        elif progress_info.get('status') == 'processing':
            widgets['progress']['value'] = 100
            widgets['percent'].config(text="100%")
            widgets['status'].config(text="🔄 处理中", fg='#000000')
            widgets['info'].config(text="正在处理视频...")
            
        elif progress_info.get('status') == 'downloading':
            percent = progress_info.get('percent', 0)
            widgets['progress']['value'] = percent
            widgets['percent'].config(text=f"{percent:.1f}%")
            widgets['status'].config(text="⬇ 下载中", fg='#000000')
            
            # 更新标题
            if progress_info.get('title'):
                title = progress_info['title'][:40] + "..." if len(progress_info['title']) > 40 else progress_info['title']
                widgets['title'].config(text=f"📹 {title}")
            
            # 更新详细信息
            total_size = progress_info.get('total_size', '')
            downloaded = progress_info.get('downloaded_size', '')
            speed = progress_info.get('speed', '')
            eta = progress_info.get('eta', '')
            
            info_parts = []
            if downloaded and total_size:
                info_parts.append(f"{downloaded} / {total_size}")
            if eta:
                info_parts.append(f"剩余: {eta}")
                
            if info_parts:
                widgets['info'].config(text=" | ".join(info_parts))
            
            if speed:
                widgets['speed'].config(text=f"⚡ {speed}")
                
        elif progress_info.get('status') == 'completed':
            widgets['progress']['value'] = 100
            widgets['percent'].config(text="100%")
            widgets['status'].config(text="✅ 完成", fg='#000000')
            
            # 计算下载时间
            if url in self.download_start_time:
                elapsed = time.time() - self.download_start_time[url]
                widgets['info'].config(text=f"耗时: {self.format_time(elapsed)}")
                
        elif progress_info.get('status') == 'error':
            widgets['status'].config(text="❌ 失败", fg='#000000')
            error_msg = progress_info.get('error', '未知错误')
            widgets['info'].config(text=f"错误: {error_msg[:50]}")
            
    def format_time(self, seconds):
        """格式化时间"""
        if seconds < 60:
            return f"{seconds:.0f}秒"
        elif seconds < 3600:
            return f"{seconds//60:.0f}分{seconds%60:.0f}秒"
        else:
            return f"{seconds//3600:.0f}时{(seconds%3600)//60:.0f}分"
            
    def format_size(self, bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f}{unit}"
            bytes /= 1024.0
        return f"{bytes:.1f}TB"
        
    def download_worker(self):
        """下载工作线程"""
        while not self.stop_event.is_set():
            try:
                url = self.download_queue.get(timeout=1)
            except queue.Empty:
                break
                
            if self.stop_event.is_set():
                break
            
            # 立即创建进度条并显示"正在解析"状态
            self.update_progress(url, {
                'status': 'parsing',
                'title': url.split('/')[-1][:40]
            })
            
            self.download_video(url)
            
    def download_video(self, url):
        """下载单个视频"""
        download_path = self.path_var.get()
        
        def progress_hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                
                percent = (downloaded / total * 100) if total > 0 else 0
                
                progress_info = {
                    'status': 'downloading',
                    'percent': percent,
                    'title': d.get('info_dict', {}).get('title', ''),
                    'total_size': self.format_size(total) if total else '',
                    'downloaded_size': self.format_size(downloaded),
                    'speed': f"{self.format_size(speed)}/s" if speed else '',
                    'eta': self.format_time(eta) if eta else ''
                }
                self.update_progress(url, progress_info)
                
            elif d['status'] == 'finished':
                # 下载完成但可能还在后处理
                self.update_progress(url, {
                    'status': 'processing',
                    'title': d.get('info_dict', {}).get('title', '')
                })
                
        def postprocessor_hook(d):
            if d['status'] == 'processing':
                self.update_progress(url, {
                    'status': 'processing',
                    'title': d.get('info_dict', {}).get('title', '')
                })
            elif d['status'] == 'finished':
                self.update_progress(url, {'status': 'completed'})
        
        # 尝试多种格式配置
        format_configs = [
            'best[ext=mp4]/best[ext=flv]/best',  # 优先mp4，然后flv，最后任意
            'best[height<=1080]/best',  # 1080p以下
            'best[height<=720]/best',   # 720p以下
            'best[height<=480]/best',   # 480p以下
            'worst/best',               # 最差质量
        ]
        
        for i, format_string in enumerate(format_configs):
            ydl_opts = {
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'postprocessor_hooks': [postprocessor_hook],
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'nocheckcertificate': False,
                'verbose': False,
                'format': format_string,
                'merge_output_format': 'mp4',
                'no_check_formats': True,
                'ignoreerrors': False,
            }
            
            if hasattr(sys, '_MEIPASS'):
                ydl_opts['nocheckcertificate'] = True
            
            try:
                self.log_message(f"解析视频: {url}", "INFO")
                
                # 先提取视频信息
                with yt_dlp.YoutubeDL({**ydl_opts, 'skip_download': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_title = info.get('title', '未知标题')
                    
                    # 更新为"准备下载"状态，显示视频标题
                    self.update_progress(url, {
                        'status': 'preparing',
                        'title': video_title
                    })
                    
                self.log_message(f"开始下载: {video_title} (格式策略 {i+1})", "INFO")
                
                # 开始实际下载
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
                # 确保状态为完成
                self.update_progress(url, {'status': 'completed'})
                self.completed_videos += 1
                self.update_overall_progress()
                self.log_message(f"下载完成: {video_title}", "SUCCESS")
                return  # 成功下载，退出重试循环
                
            except Exception as e:
                error_msg = str(e)
                if i < len(format_configs) - 1:  # 还有其他格式可以尝试
                    self.log_message(f"格式策略 {i+1} 失败，尝试下一个策略: {error_msg[:50]}", "WARNING")
                    continue
                else:  # 所有格式都失败了
                    self.failed_videos += 1
                    self.completed_videos += 1
                    self.update_progress(url, {'status': 'error', 'error': error_msg})
                    self.log_message(f"下载失败 {url}: {error_msg}", "ERROR")
                    self.update_overall_progress()
                    return
            
    def update_overall_progress(self):
        """更新整体进度"""
        self.root.after(0, lambda: self._update_overall_progress_main())
        
    def _update_overall_progress_main(self):
        """在主线程中更新整体进度"""
        self.overall_progress['value'] = self.completed_videos
        percent = (self.completed_videos / self.total_videos * 100) if self.total_videos > 0 else 0
        self.overall_label.config(text=f"{self.completed_videos}/{self.total_videos} ({percent:.0f}%)")
        self.update_stats()
        
        if self.completed_videos >= self.total_videos:
            self.download_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.url_text.config(state='normal')
            
            if self.failed_videos == 0:
                self.log_message("🎉 所有视频下载成功！", "SUCCESS")
            else:
                self.log_message(f"下载完成：成功 {self.completed_videos - self.failed_videos} 个，失败 {self.failed_videos} 个", "WARNING")
            
    def start_download_thread(self):
        """启动后台下载线程（预留）"""
        pass


def main():
    root = tk.Tk()
    app = VideoDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()