import tabula
import pandas as pd

pdf_path = r"F:\a\apaper\project\project\algorithm\test_media\LLM Post-Training- A Deep Dive into Reasoning Large Language Models-5.pdf"

# 指定特定页面
tables = tabula.read_pdf(pdf_path, pages='1')  # 只提取第1-3页的表格

# 指定表格区域 (top, left, bottom, right)，以页面百分比形式
tables = tabula.read_pdf(pdf_path, area=(0, 0, 100, 100), pages='1')

# 使用lattice模式（适用于有边框的表格）
# tables = tabula.read_pdf(pdf_path, pages='all', lattice=True)

# 使用stream模式（适用于没有边框的表格）
tables = tabula.read_pdf(pdf_path, pages='all', stream=True)

# 提取后，转换为DataFrame列表
for i, table in enumerate(tables):
    print(f"表格 {i+1} 的形状: {table.shape}")
    print(table.head())
