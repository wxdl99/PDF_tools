from __future__ import annotations


DEFAULT_LANGUAGE = "zh"


LANGUAGES = {
    "zh": "中文",
    "en": "English",
}


TEXT = {
    "zh": {
        "app_title": "PDF 合并工具",
        "initial_status": "请选择需要合并的 PDF 文件。",
        "available_operations": "当前接口：{operations}",
        "file_list_title": "待合并 PDF（按列表顺序合并）",
        "add_pdf": "添加 PDF",
        "remove_selected": "移除选中",
        "move_up": "上移",
        "move_down": "下移",
        "clear_list": "清空列表",
        "keep_metadata": "保留首个 PDF 元数据",
        "language": "语言",
        "output_settings": "输出设置",
        "save_to": "保存到",
        "choose_location": "选择位置",
        "merge": "开始合并",
        "choose_pdf_title": "选择 PDF 文件",
        "pdf_files": "PDF 文件",
        "all_files": "所有文件",
        "selected_count": "已选择 {count} 个 PDF。",
        "list_cleared": "列表已清空。",
        "save_merged_title": "保存合并后的 PDF",
        "default_output_name": "合并结果.pdf",
        "choose_output_error": "请选择输出文件位置。",
        "merging": "正在合并，请稍候...",
        "merge_done_status": "合并完成：{path}",
        "merge_done_message": "PDF 合并完成！\n\n{path}",
        "merge_failed_status": "合并失败，请检查文件后重试。",
        "error_min_files": "请至少选择 2 个 PDF 文件。",
        "error_missing_file": "文件不存在：{path}",
        "error_encrypted_pdf": "暂不支持加密 PDF：{name}",
    },
    "en": {
        "app_title": "PDF Merger",
        "initial_status": "Choose the PDF files you want to merge.",
        "available_operations": "Available API: {operations}",
        "file_list_title": "PDFs to merge (merged in list order)",
        "add_pdf": "Add PDFs",
        "remove_selected": "Remove Selected",
        "move_up": "Move Up",
        "move_down": "Move Down",
        "clear_list": "Clear List",
        "keep_metadata": "Keep first PDF metadata",
        "language": "Language",
        "output_settings": "Output Settings",
        "save_to": "Save to",
        "choose_location": "Choose Location",
        "merge": "Merge PDFs",
        "choose_pdf_title": "Choose PDF Files",
        "pdf_files": "PDF files",
        "all_files": "All files",
        "selected_count": "{count} PDF(s) selected.",
        "list_cleared": "The list is now empty.",
        "save_merged_title": "Save Merged PDF",
        "default_output_name": "merged.pdf",
        "choose_output_error": "Choose an output file location.",
        "merging": "Merging, please wait...",
        "merge_done_status": "Merged successfully: {path}",
        "merge_done_message": "PDF merge complete!\n\n{path}",
        "merge_failed_status": "Merge failed. Check the files and try again.",
        "error_min_files": "Choose at least 2 PDF files.",
        "error_missing_file": "File does not exist: {path}",
        "error_encrypted_pdf": "Encrypted PDFs are not supported yet: {name}",
    },
}


def t(language: str, key: str, **kwargs: object) -> str:
    messages = TEXT.get(language, TEXT[DEFAULT_LANGUAGE])
    template = messages.get(key, TEXT[DEFAULT_LANGUAGE][key])
    return template.format(**kwargs)
