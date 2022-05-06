#local
import sql.sql_settings as sql_sets
#python
import pymysql as sql
import pymysql.cursors as cursors



def log(message):
    print(f"\033[36;1m======> {message}\033[0m")

class SQL(sql.connect):
    def __init__(self):
        super().__init__(
            user        = sql_sets.USER,
            password    = sql_sets.PASSWORD,
            host        = sql_sets.HOST,
            port        = sql_sets.PORT,
            db          = sql_sets.DATABASE,
            cursorclass = cursors.DictCursor
        )
        self.cr = self.cursor()

    def __values_constructor(dict, sep=",", comp="=", binary=False):
        return sep.join([f"{'BINARY ' if binary else ''}{key} {comp} '{value}'" for key, value in dict.items()])
    
    def add(self, model):
        table = model.table

        columns = str(model.columns).replace("'", "`")
        values = model.values

        query = f"INSERT INTO {table} {columns} VALUES {values}"
        log(query)

        self.cr.execute(query)
        self.commit()
    
    def update(self, model, where="id", **values):
        table = model.table
        
        where_args = f"{where} = '{model.__dict__[where]}'"
        values = SQL.__values_constructor(values)

        query = f"UPDATE {table} SET {values} WHERE ({where_args})"
        log(query)

        self.cr.execute(query)
        self.commit()
    
    def select(self, model, cols="*", sep=" AND ", comp="=", order_by=None, desc=False, **values):
        table = model().table

        values = SQL.__values_constructor(values, sep=sep, comp=comp)

        query = f"SELECT {', '.join(cols)} FROM {table} WHERE ({values}){f' ORDER BY {order_by}' if order_by else ''}{' DESC' if desc else ''}"
        log(query)

        self.cr.execute(query)
        return self.cr.fetchall()
    
    def select_one(self, model, cols="*", **values):
        table = model().table

        args = SQL.__values_constructor(values, sep=" AND ", binary=True)

        query = f"SELECT {', '.join(cols)} FROM {table} WHERE ({args})"
        log(query)

        self.cr.execute(query)
        res = self.cr.fetchone()
        if res:
            return model(**res)
        return None
    
    def delete(self, model, **values):
        table = model().table

        args = SQL.__values_constructor(values, sep=" AND ", binary=True)

        query = f"DELETE FROM {table} WHERE ({args})"
        log(query)

        self.cr.execute(query)
        self.commit()
    
    def model_by_query(self, model, query):
        self.cr.execute(query)

        result = self.cr.fetchone()
        return model(**result)
    
    def exe(self, query):
        self.cr.execute(query)
        return self.cr.fetchall()
