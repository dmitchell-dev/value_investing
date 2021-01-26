
for current_company_filename in file_list:
    file_num = file_num + 1
    s = f"file {file_num} of {num_files}, {current_company_filename}"
    print(s)

    # Get current report type
    filename_first = current_company_filename.split("_")[2]
    filename_second = current_company_filename.replace(".csv", "").split("_")[3]
    current_report_type = f"{filename_first} {filename_second}"

    # Get company tidm for associated id
    current_company_tidm = current_company_filename.split("_")[1]

    # Get last param name in section
    report_section_last_df = self.df_params[
        self.df_params.report_name == current_report_type.title()
    ]
    report_section_last_df = report_section_last_df[
        "report_section_last"
    ].unique()
    report_section_last_list = report_section_last_df.tolist()

    # Get company report data
    df_data = pd.read_csv(
        f"data/company_reports/{current_company_filename}",
        index_col="Period Ending",
        skiprows=1,
    )
    df_data = df_data.where((pd.notnull(df_data)), None)
    df_data = df_data.drop("Result Type", axis=0)
    if " " in df_data.index:
        df_data = df_data.drop(" ")

    # Generate parameter_id and replace index
    i_section = 0
    i_param = 0
    param_id_list = []

    param_list = df_data.index

    for section in report_section_last_list:

        param_section_filter_list_df = self.df_params[
            self.df_params.report_section_last == section
        ]

        while True:

            param_id = param_section_filter_list_df[
                (param_section_filter_list_df.param_name == param_list[i_param])
            ]
            param_id = param_id.iloc[0]["id"]
            param_id_list.append(param_id)

            if param_list[i_param] == section:
                i_section = i_section + 1
                i_param = i_param + 1
                break

            i_param = i_param + 1

    df_data.index = param_id_list

    # company id
    company_id = self.df_companies[
        self.df_companies["tidm"] == current_company_tidm
    ].id.values[0]

    # Create list of columns
    df_items = df_data.items()
    output_list = []
    for label, content in df_items:
        output_list.append([content])

    # Build SQL statement
    sql = self._sql_builder()

    # Get data from all columns and populate database
    num_col = df_data.shape[1]

    # Date formats
    date_fmts = ("%d/%m/%Y %H:%M:%S", "%d/%m/%y %H:%M:%S")

    # Iterate over date columns
    for i in range(0, num_col):

        current_col = output_list[i]
        data = current_col[0]

        # Get data for insert
        # Date of current report
        current_date = f"{data.name} 00:00:00"

        # Iterate over data to insert into database
        i = 0
        for index, value in data.items():
            i = i + 1

            # Check value format
            if value == "Infinity" or value == "-Infinity":
                value = None

            # Check datetime format
            for fmt in date_fmts:
                try:
                    current_date_time = datetime.strptime(current_date, fmt)
                    break
                except ValueError as err:
                    pass

            row = [
                str(company_id),
                index,
                current_date_time,
                value,
            ]

            self.cursor.execute(sql, row)
            self.db.commit()