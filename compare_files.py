import difflib
import pandas as pd
from tkinter import messagebox
import datetime

def compare_files(file_paths):
    if len(file_paths) < 2:
        messagebox.showwarning("警告", "请至少选择两个文件进行对比！")
        return

    try:
        data_frames = []
        for file_path in file_paths:
            if file_path.endswith('.csv'):
                try:
                    df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, encoding='gbk', low_memory=False)
            elif file_path.endswith(('.xlsx', '.xls')):
                try:
                    df = pd.read_excel(file_path)
                except ImportError as e:
                    messagebox.showerror("错误", f"需要安装xlrd库来读取xls文件：{e}")
                    return
            else:
                raise ValueError("文件格式不支持！")
            data_frames.append(df)

        if any(df.empty for df in data_frames):
            messagebox.showwarning("警告", "其中一个或多个文件是空的，请选择有效的文件。")
            return

        base = data_frames[0].iloc[:, 3].astype(str).tolist()
        diff_results = []

        for i, df in enumerate(data_frames[1:], start=2):
            comparison = df.iloc[:, 3].astype(str).tolist()
            d = difflib.Differ()
            diff = list(d.compare(base, comparison))
            diff_results.append((i, diff))

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = f"comparison_result_{timestamp}.xlsx"

        with pd.ExcelWriter(output_file) as writer:
            data_frames[0].to_excel(writer, sheet_name='Base File', index=False)
            for i, df in enumerate(data_frames[1:], start=2):
                df.to_excel(writer, sheet_name=f'File {i}', index=False)

            for i, diff in diff_results:
                diff_data = {"Base File 行": [], f"File {i} 行": [], "差异": []}
                line_num_base, line_num_compare = 1, 1

                for line in diff:
                    if line.startswith('+'):
                        diff_data[f"File {i} 行"].append(line_num_compare)
                        diff_data["Base File 行"].append("")
                        diff_data["差异"].append(line[2:].strip())
                        line_num_compare += 1
                    elif line.startswith('-'):
                        diff_data["Base File 行"].append(line_num_base)
                        diff_data[f"File {i} 行"].append("")
                        diff_data["差异"].append(line[2:].strip())
                        line_num_base += 1
                    elif line.startswith(' '):
                        line_num_base += 1
                        line_num_compare += 1

                if diff_data["Base File 行"] or diff_data[f"File {i} 行"]:
                    diff_df = pd.DataFrame(diff_data)
                    diff_df.to_excel(writer, sheet_name=f'Differences with File {i}', index=False)

        messagebox.showinfo("成功", f"文件对比完成！\n差异数据已保存到: {output_file}")

    except Exception as e:
        messagebox.showerror("错误", f"文件对比出错：{e}")
