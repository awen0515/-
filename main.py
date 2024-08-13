import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import data_cleaner
import compare_files

class DataCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("数据清洗与对比工具")

        self.file_path = tk.StringVar()
        self.compare_file_paths = [tk.StringVar(), tk.StringVar(), tk.StringVar()]
        self.patterns = ['OK', 'NG', '测试字段可修改']

        self.create_widgets()

    def create_widgets(self):
        # 文件选择框
        tk.Label(self.root, text="选择文件:").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.file_path, width=50).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="浏览", command=self.browse_file).grid(row=0, column=2, padx=10, pady=10)

        # 数据清洗按钮
        self.clean_button = tk.Button(self.root, text="数据清洗", command=self.start_clean_data)
        self.clean_button.grid(row=1, column=0, columnspan=3, pady=10)

        # 动态添加查找模式
        self.pattern_frame = tk.Frame(self.root)
        self.pattern_frame.grid(row=2, column=0, columnspan=3, pady=10)
        tk.Label(self.pattern_frame, text="查找字段:").grid(row=0, column=0, padx=10, pady=5)
        self.pattern_entry = tk.Entry(self.pattern_frame)
        self.pattern_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self.pattern_frame, text="添加关键字", command=self.add_pattern).grid(row=0, column=2, padx=10, pady=5)
        self.pattern_listbox = tk.Listbox(self.pattern_frame, selectmode=tk.SINGLE)
        self.pattern_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=5)
        tk.Button(self.pattern_frame, text="删除", command=self.remove_pattern).grid(row=2, column=0, columnspan=3, pady=5)

        for pattern in self.patterns:
            self.pattern_listbox.insert(tk.END, pattern)

        # 文件对比选择框
        self.compare_frame = tk.Frame(self.root)
        self.compare_frame.grid(row=3, column=0, columnspan=3, pady=10)
        for i in range(3):
            tk.Label(self.compare_frame, text=f"选择对比文件 {i+1}:").grid(row=i, column=0, padx=10, pady=5)
            tk.Entry(self.compare_frame, textvariable=self.compare_file_paths[i], width=50).grid(row=i, column=1, padx=10, pady=5)
            tk.Button(self.compare_frame, text="浏览", command=lambda i=i: self.browse_compare_file(i)).grid(row=i, column=2, padx=10, pady=5)

        # 文件对比按钮
        self.compare_button = tk.Button(self.root, text="文件对比", command=self.start_compare_files)
        self.compare_button.grid(row=4, column=0, columnspan=3, pady=10)

        # # 进度条
        # self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        # self.progress.grid(row=5, column=0, columnspan=3, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx;*.xls")])
        self.file_path.set(file_path)

    def browse_compare_file(self, index):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx;*.xls")])
        self.compare_file_paths[index].set(file_path)

    def start_clean_data(self):
        if not hasattr(self, 'clean_data_thread') or not self.clean_data_thread.is_alive():
            self.clean_data_thread = threading.Thread(target=self.clean_data)
            self.clean_data_thread.start()

    def clean_data(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showwarning("警告", "请选择一个文件！")
            return

        if not self.patterns:
            messagebox.showwarning("警告", "请添加至少一个查找模式！")
            return

        try:
            data_cleaner.configure_cleaning(self.patterns)
            pattern_counts, output_file = data_cleaner.clean_data(file_path)
        # try:
        #     def progress_callback(progress):
        #         self.progress['value'] = progress
        #         self.root.update_idletasks()
        #
        #     data_cleaner.configure_cleaning(self.patterns)
        #     pattern_counts, output_file = data_cleaner.clean_data(file_path, progress_callback)

            result_message = "数据清洗完成！\n"
            for pattern, count in pattern_counts.items():
                result_message += f"{pattern} 数量: {count}\n"
            result_message += f"保存到: {output_file}"

            messagebox.showinfo("成功", result_message)

        except Exception as e:
            messagebox.showerror("错误", f"数据处理出错：{e}")

    def add_pattern(self):
        pattern = self.pattern_entry.get()
        if pattern:
            self.patterns.append(pattern)
            self.pattern_listbox.insert(tk.END, pattern)
            self.pattern_entry.delete(0, tk.END)

    def remove_pattern(self):
        selected_indices = self.pattern_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            self.patterns.pop(index)
            self.pattern_listbox.delete(index)

    def start_compare_files(self):
        if not hasattr(self, 'compare_files_thread') or not self.compare_files_thread.is_alive():
            self.compare_files_thread = threading.Thread(target=self.compare_files)
            self.compare_files_thread.start()

    def compare_files(self):
        file_paths = [path.get() for path in self.compare_file_paths if path.get()]
        compare_files.compare_files(file_paths)

if __name__ == "__main__":
    root = tk.Tk()
    app = DataCleanerApp(root)
    root.mainloop()
