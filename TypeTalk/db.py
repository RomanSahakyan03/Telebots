# import sqlite3

# class BotDB:

#     def __init__(self, db_file):
#         self.conn = sqlite3.connect(
#             db_file, detect_types=sqlite3.PARSE_COLNAMES, check_same_thread=False)
#         self.cursor = self.conn.cursor()

#     def create_table(self, table,columns):
#         columns_str = ", ".join(columns)
#         create_table_query = f"CREATE TABLE IF NOT EXISTS {table} ( {columns_str} );"
#         self.cursor.execute(create_table_query)
#         self.conn.commit()

#     def select_parameter(self, columns="*", condition=None):
#         select_query = f"SELECT {columns} FROM users WHERE {condition}" if condition else f"SELECT {columns} FROM users"
#         self.cursor.execute(select_query)
#         result = self.cursor.fetchone()
#         if result:
#             user_params = dict(zip([column[0] for column in self.cursor.description], result))
#             return user_params
#         else:
#             return None

#     # def check_exist(self, chat_id):
#     #     user_params = self.select_parameter(columns="*", condition="chat_id = ?", params=(chat_id,))
#     #     num_filled_cols = len([v for v in user_params[0] if v is not None])
#     #     return bool(user_params) and num_filled_cols == len(self.cursor.description) - 1

#     def check_all_except_some_columns_filled(self, chat_id):
#         cursor = self.cursor

#         # Columns to exclude from the check
#         columns_to_exclude = ['region_lat', 'region_lon']

#         # Execute the SELECT query with the condition
#         query = f"SELECT * FROM users WHERE chat_id = {chat_id}"
#         cursor.execute(query)

#         # Fetch the first row matching the condition
#         row = cursor.fetchone()

#         # Check if the row exists and all non-excluded columns are filled
#         return bool(row) and all(value is not None for idx, value in enumerate(row) if idx not in columns_to_exclude)

#     def is_chat_id_exists(self, chat_id):
#         select_query = "SELECT 1 FROM users WHERE chat_id = ?"
#         self.cursor.execute(select_query, (chat_id,))
#         row = self.cursor.fetchone()
#         return row is not None

#     def insert_user(self, chat_id):
#         select_query = "SELECT chat_id FROM users WHERE chat_id = ?"
#         self.cursor.execute(select_query, (chat_id,))
#         if self.cursor.fetchone() is None:
#             insert_query = "INSERT INTO users (chat_id) VALUES (?)"
#             self.cursor.execute(insert_query, (chat_id,))
#             self.conn.commit()

#     def upsert_user_data(self, data_dict, condition):
#         columns = ", ".join(data_dict.keys())
#         values = ", ".join(["?" for i in range(len(data_dict))])
#         select_query = f"SELECT COUNT(*) FROM users WHERE {condition}"
#         self.cursor.execute(select_query)
#         row_count = self.cursor.fetchone()[0]
#         if row_count == 0:
#             # Insert new row if it does not exist
#             insert_query = f"INSERT INTO users ({columns}) VALUES ({values})"
#             self.cursor.execute(insert_query, tuple(data_dict.values()))
#         else:
#             # Update existing row if it exists
#             set_clause = ", ".join([f"{key} = ?" for key in data_dict])
#             update_query = f"UPDATE users SET {set_clause} WHERE {condition}"
#             self.cursor.execute(update_query, tuple(data_dict.values()))
#         self.conn.commit()

#     def delete_user(self, chat_id):
#         delete_query = f"DELETE FROM users WHERE chat_id = {chat_id}"
#         self.cursor.execute(delete_query)
#         self.conn.commit()

#     def close(self):
#         self.cursor.close()
#         self.conn.close()


import aiosqlite

class BotDB:

    def __init__(self, db_file):
        self.db_file = db_file

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_file)
        self.cursor = await self.conn.cursor()

    async def create_table(self, table, columns):
        columns_str = ", ".join(columns)
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table} ( {columns_str} );"
        await self.cursor.execute(create_table_query)
        await self.conn.commit()

    async def select_parameter(self, columns="*", condition=None):
        select_query = f"SELECT {columns} FROM users WHERE {condition}" if condition else f"SELECT {columns} FROM users"
        await self.cursor.execute(select_query)
        result = await self.cursor.fetchone()
        if result:
            user_params = dict(zip([column[0] for column in self.cursor.description], result))
            return user_params
        else:
            return None

    async def check_all_except_some_columns_filled(self, chat_id):
        cursor = self.cursor

        # Columns to exclude from the check
        columns_to_exclude = ['region_lat', 'region_lon']

        # Execute the SELECT query with the condition
        query = f"SELECT * FROM users WHERE chat_id = {chat_id}"
        await cursor.execute(query)

        # Fetch the first row matching the condition
        row = await cursor.fetchone()

        # Check if the row exists and all non-excluded columns are filled
        return bool(row) and all(value is not None for idx, value in enumerate(row) if idx not in columns_to_exclude)

    async def is_chat_id_exists(self, chat_id):
        select_query = "SELECT 1 FROM users WHERE chat_id = ?"
        await self.cursor.execute(select_query, (chat_id,))
        row = await self.cursor.fetchone()
        return row is not None

    async def insert_user(self, chat_id):
        select_query = "SELECT chat_id FROM users WHERE chat_id = ?"
        await self.cursor.execute(select_query, (chat_id,))
        if await self.cursor.fetchone() is None:
            insert_query = "INSERT INTO users (chat_id) VALUES (?)"
            await self.cursor.execute(insert_query, (chat_id,))
            await self.conn.commit()

    async def upsert_user_data(self, data_dict, condition):
        columns = ", ".join(data_dict.keys())
        values = ", ".join(["?" for i in range(len(data_dict))])
        select_query = f"SELECT COUNT(*) FROM users WHERE {condition}"
        await self.cursor.execute(select_query)
        row_count = (await self.cursor.fetchone())[0]
        if row_count == 0:
            # Insert new row if it does not exist
            insert_query = f"INSERT INTO users ({columns}) VALUES ({values})"
            await self.cursor.execute(insert_query, tuple(data_dict.values()))
        else:
            # Update existing row if it exists
            set_clause = ", ".join([f"{key} = ?" for key in data_dict])
            update_query = f"UPDATE users SET {set_clause} WHERE {condition}"
            await self.cursor.execute(update_query, tuple(data_dict.values()))
        await self.conn.commit()

    async def delete_user(self, chat_id):
        delete_query = f"DELETE FROM users WHERE chat_id = {chat_id}"
        await self.cursor.execute(delete_query)
        await self.conn.commit()

    async def close(self):
        await self.cursor.close()
        await self.conn.close()
