import pandas as pd
import sqlite3


def createTransactionsTable(db:sqlite3.Cursor) -> bool:
    """create a transactions table in the database"""
    
    createTransactions = (
        'CREATE TABLE IF NOT EXISTS transactions ('
        'id INTEGER PRIMARY KEY NOT NULL,'
        'year INTEGER NOT NULL,'
        'month INTEGER NOT NULL,'
        'day INTEGER NOT NULL,'
        'value REAL NOT NULL,'
        'account TEXT,'
        'category TEXT,'
        'tag TEXT,'
        'match INTEGER UNIQUE REFERENCES transactions(id),'
        'FOREIGN KEY (account) REFERENCES accounts(name)'
        'FOREIGN KEY (category) REFERENCES categories(name)'
        ')'
    )

    db.execute(createTransactions)
    return True

def addTransaction(db:sqlite3.Cursor, year:int, month:int, day:int, value:float, account:str, category:str, tag:str) -> bool:
    """add a transaction to the transactions table"""
    sql = 'INSERT INTO transactions (year, month, day, value, account, category, tag) VALUES (?,?,?,?,?,?,?)'
    values = (year, month, day, value, account.strip(), category, tag)
    try:
        db.execute(sql, values)
    except sqlite3.IntegrityError as e:
        print(f"\nINVALID DATA: {e}\n")
        return False
    return True

def deleteTransaction(db:sqlite3.Cursor, id:int) -> bool:
    """remove a transaction from the transactions table"""
    sql = f'DELETE FROM transactions WHERE id={id}'
    db.execute(sql)
    return True

def modifyTransactionDate(db:sqlite3.Cursor, id:int, date) -> bool:
    """modify the date of a transaction"""
    sql = f'UPDATE transactions SET year=? SET month=? SET day=? WHERE id=?'
    db.execute(sql,(date[0],date[1],date[2],id))
    return True

def modifyTransactionValue(db:sqlite3.Cursor, id:int, value:float) -> bool:
    """modify the value of a transaction"""
    sql = f'UPDATE transactions SET value=? WHERE id=?'
    db.execute(sql,(value,id))
    return True

def modifyTransactionAccount(db:sqlite3.Cursor, id:int, account:str) -> bool:
    """modify the account that a transaction is associated with"""
    sql = f'UPDATE transactions SET account=? WHERE id=?'
    try:
        db.execute(sql,(account.strip(),id))
    except sqlite3.IntegrityError as e:
        print(f"\n INVALID ACCOUNT NAME, TRANSACTION NOT MODIFIED, {e}")
        return False
    return True

def modifyTransactionCategory(db:sqlite3.Cursor, id:int, category:str) -> bool:
    """modify a transaction's category"""
    sql = f'UPDATE transactions SET category=? WHERE id=?'
    try:
        db.execute(sql,(category,id))
    except sqlite3.IntegrityError as e:
        print(f"\n INVALID CATEGORY, TRANSACTION NOT MODIFIED, {e}")
        return False
    return True

def modifyTransactionTag(db:sqlite3.Cursor, id:int, tag:str) -> bool:
    """modify a transaction's tag"""
    sql = f'UPDATE transactions SET tag=? WHERE id=?'
    db.execute(sql,(tag,id))
    return True

def matchTransactions(db:sqlite3.Cursor, id1:int, id2:int) -> bool:
    '''match two transactions as a transfer'''
    sql = f'SELECT value FROM transactions WHERE id IN (?,?)'
    db.execute(sql,(id1,id2))
    if sum([value[0] for value in db.fetchall()]) == 0:
        sql = f'UPDATE transactions SET match=? WHERE id=?'
        db.executemany(sql, [(id1,id2),(id2,id1)])
        return True
    return False

def unmatchTransactions(db:sqlite3.Cursor, id1:int, id2:int) -> bool:
    '''unmatch a pair of transactions'''
    sql = f'UPDATE transactions SET match=NULL WHERE id=?'
    db.executemany(sql, [(id1,), (id2,)])
    return True

def getTransactions(db:sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM transactions ORDER BY year ASC, month ASC, day ASC", db)

def getAnnualTotals(db:sqlite3.Cursor) -> pd.DataFrame:
    """get the total value of all transactions at the end of each year"""
    sql = 'WITH YearlyTotals AS (SELECT year,SUM(value) AS total FROM transactions GROUP BY year) SELECT year,SUM(total) OVER(ORDER BY year ASC) FROM YearlyTotals'
    db.execute(sql)
    data = db.fetchall()
    years = [row[0] for row in data]
    totals = [row[1] for row in data]
    annualTotals = {'year' : years, 'total' : totals}
    return pd.DataFrame(annualTotals)

def getMonthlyTotals(db:sqlite3.Cursor) -> pd.DataFrame:
    """get the total value of all transactions at the end of each month"""
    sql = 'WITH MonthlyTotals AS (SELECT year,month,SUM(value) AS total FROM transactions GROUP BY year,month) SELECT year,month,SUM(total) OVER(ORDER BY year ASC, month ASC) FROM MonthlyTotals'
    db.execute(sql)
    data = db.fetchall()
    years = [row[0] for row in data]
    months = [row[1] for row in data]
    totals = [row[2] for row in data]
    monthlyTotals = {'year' : years, 'month' : months, 'total' : totals}
    return pd.DataFrame(monthlyTotals)

def getAccountTotals(db:sqlite3.Cursor) -> pd.DataFrame:
    """get the total value of each account for all time"""
    sql = 'SELECT account,SUM(value) FROM transactions GROUP BY account'
    db.execute(sql)
    data = db.fetchall()
    accounts = [row[0] for row in data]
    totals = [row[1] for row in data]
    accountTotals = {'account' : accounts, 'total' : totals}
    return pd.DataFrame(accountTotals)

def addTransactionsFromDf(db:sqlite3.Cursor, df):
    """add a batch of transactions from a pandas dataframe"""
    sql = 'INSERT INTO transactions (year, month, day, value, account, category, tag) VALUES (?,?,?,?,?,?,?)'
    values = zip(df['year'], df['month'], df['day'], df['value'], df['account'], df['category'], df['tag'])
    db.executemany(sql, values)
