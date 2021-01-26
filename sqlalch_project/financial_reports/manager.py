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