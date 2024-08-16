import pandas as pd

def save_file(uploadFile):
    base_dir = 'uploaded_files'
    local_path = f'{base_dir}/{uploadFile.file_id}-{uploadFile.name}'
    table_description = ''
    if uploadFile.name.endswith('.csv'):
        # read csv and save to local file
        df = pd.read_csv(uploadFile, encoding="latin-1")
        df.to_csv(local_path, index=False)
        query_tabular = uploadFile.getvalue().decode("utf-8")

    elif uploadFile.name.endswith(('.xlsx', 'xls')):
        # read xlsx and save to local file
        df = pd.ExcelFile(uploadFile).parse()
        if uploadFile.name.endswith('.xlsx'):
            local_path = local_path.replace(".xlsx", ".csv")
            df.to_csv(local_path, index=False)
        else:
            local_path = local_path.replace(".xls", ".csv")
            df.to_csv(local_path, index=False)
        with open(local_path, 'r') as fp:
            query_tabular = fp.read()

    elif uploadFile.name.endswith('.docx'):
        # read docx and save to local file
        with open(local_path, "wb") as fpdf:
            fpdf.write(uploadFile.read())
        tabular_rows = docx2tabular(local_path)
        df = pd.DataFrame(tabular_rows[1:], columns=tabular_rows[0])
        query_tabular = '\n'.join(','.join(row) for row in tabular_rows)

    file_detail = {
        'name': uploadFile.name,
        'local_path': local_path,
        'description': table_description
    }

    return df, query_tabular, file_detail
