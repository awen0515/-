import pandas as pd
import datetime
from concurrent.futures import ThreadPoolExecutor

# 默认配置
config = {
    'patterns': [r'OK', r'NG']
}

def configure_cleaning(patterns=None):
    if patterns is not None:
        config['patterns'] = [rf'\b{pattern}\b' for pattern in patterns]  # 使用 \b 匹配完整单词边界

def match_pattern(df, pattern):
    return df.astype(str).apply(lambda row: row.str.contains(pattern, case=False).any(), axis=1)

def clean_data(file_path, progress_callback=None):
    try:
        if file_path.endswith('.csv'):
            df = load_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("文件格式不支持！")

        pattern_counts = {}
        matched_data = pd.DataFrame()
        total_patterns = len(config['patterns'])

        # with ThreadPoolExecutor() as executor:
        #     futures = {executor.submit(match_pattern, df, pattern): pattern for pattern in config['patterns']}
        #     for idx, future in enumerate(futures):
        #         pattern = futures[future]
        #         match = future.result()
        #         pattern_counts[pattern] = match.sum()
        #         matched_data = pd.concat([matched_data, df[match]]).drop_duplicates()
        #
        #         # 更新进度
        #         if progress_callback:
        #             progress_callback((idx + 1) / total_patterns * 100)

        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(match_pattern, df, pattern): pattern for pattern in config['patterns']}
            for future in futures:
                pattern = futures[future]
                match = future.result()
                pattern_counts[pattern] = match.sum()
                matched_data = pd.concat([matched_data, df[match]]).drop_duplicates()

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = f"cleaned_data_{timestamp}.xlsx"

        matched_data.to_excel(output_file, index=False)

        return pattern_counts, output_file

    except Exception as e:
        raise e

def load_csv(file_path):
    try:
        return pd.read_csv(file_path, encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding='gbk', low_memory=False)
