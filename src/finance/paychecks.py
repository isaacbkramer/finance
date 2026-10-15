import pandas as pd
import sqlite3


def createPaychecksTable(db:sqlite3.Cursor) -> bool:
    """create a paychecks table in the database"""
    
    createPaychecks = (
        'CREATE TABLE IF NOT EXISTS paychecks ('
        'id INTEGER PRIMARY KEY NOT NULL,'
        'year INTEGER NOT NULL,'
        'month INTEGER NOT NULL,'
        'day INTEGER NOT NULL,'
        'gross REAL NOT NULL,'
        'federal REAL NOT NULL,'
        'state REAL NOT NULL,'
        'local REAL NOT NULL,'
        'medicare REAL NOT NULL,'
        'ss REAL NOT NULL,'
        'health REAL NOT NULL,'
        'dental REAL NOT NULL,'
        'vision REAL NOT NULL,'
        'hsa REAL NOT NULL,'
        'k REAL NOT NULL,'
        'rothk REAL NOT NULL,'
        'net REAL GENERATE ALWAYS AS (gross + federal + state + local + medicare + ss + health + dental + vision + hsa + k + rothk) VIRTUAL'
        ')'
    )

    db.execute(createPaychecks)
    return True

def addPaycheck(db:sqlite3.Cursor, year:int, month:int, day:int, gross:float, federal:float, state:float, local:float, medicare:float, ss:float, health:float, dental:float, vision:float, hsa:float, k:float, rothk:float) -> bool:
    """add a paycheck to the paychecks table"""
    sql = 'INSERT INTO paychecks (year, month, day, gross, federal, state, local, medicare, ss, health, dental, vision, hsa, k, rothk) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    values = (year, month, day, gross, federal, state, local, medicare, ss, health, dental, vision, hsa, k, rothk)
    db.execute(sql, values)
    return True

def deletePaycheck(db:sqlite3.Cursor, id:int) -> bool:
    """remove a paycheck from the paychecks table"""
    sql = f'DELETE FROM paychecks WHERE id={id}'
    db.execute(sql)
    return True

def getPaychecks(db:sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM paychecks ORDER BY year ASC, month ASC, day ASC", db)
