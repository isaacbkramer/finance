import sys
import sqlite3
import accounts
import categories
import register
import investments
import csvreader
import database
import paychecks
from pathlib import Path

def startup() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    """initialize database and return a cursor to it"""
    db = database.create('database.db')
    cur = database.cursor(db)
    accounts.createAccountsTable(cur)
    categories.createCategoriesTable(cur)
    register.createTransactionsTable(cur)
    investments.createInvestmentsTable(cur)
    paychecks.createPaychecksTable(cur)
    print('\n########## WELCOME TO FINANCE-CLI ##########\n')
    print('Follow the prompts or type "exit" at any time to terminate the program.\n')
    return db, cur

def shutdown(db) -> None:
    """call database shutdown and exit"""
    database.shutdown(db)
    print('goodbye')
    sys.exit(0)

def readDate() -> tuple[int,int,int]:
    """read a date tuple from a string and return it"""
    while True:
        dateStr = input("Date YYYYMMDD: ")
        if len(dateStr) != 8:
            print("incorrect date format")
            continue
        try:
            year = int(dateStr[0:4])
        except ValueError:
            print(f"unexpected value for year {year}")
            continue
        try:
            month = int(dateStr[4:6])
        except ValueError:
            print(f"unexpected value for month {month}")
            continue    
        if month < 1 or month > 12:
            print(f"unexpected value for month {month}")
            continue
        try:
            day = int(dateStr[6:])
        except ValueError:
            print(f"unexpected value for day {day}")
            continue
        if day < 1 or day > 31:
            print(f"unexpected value for day {day}")
            continue
        return (year,month,day)

if __name__ == "__main__":
    db, cur = startup()
    while True:
        command = input("transactions investments accounts totals paychecks exit: ").lower()
        if command == 'transactions':
            while True:
                command = input("add delete modify match unmatch view exit: ").lower()
                if command =='add':
                    command = input("manual csv: ").lower()
                    if command == 'manual':
                        date = readDate()
                        value = float(input("Value: "))
                        account = str(input("Account Name: "))
                        print(categories.getCategories(db))
                        category = str(input("Category (from above options): "))
                        tag = str(input("Tag: "))
                        register.addTransaction(cur, date[0],date[1],date[2],value,account,category,tag)
                    elif command == 'csv': 
                        type = input("default quicken: ").lower()
                        account = input("account name: ")
                        file = input("filename: ")
                        file = Path(file)
                        if file.is_file():
                            if type == 'default':
                                df = csvreader.readDefaultCsv(file)
                                register.addTransactionsFromDf(cur, df)
                            elif type == 'quicken':
                                df = csvreader.readQuickenCsv(file, account)
                                register.addTransactionsFromDf(cur, df)
                            else:
                                continue
                        else:
                            print(f'file {file} does not exist')
                    else: 
                        continue
                elif command == 'delete':
                    id = int(input("id: "))
                    register.deleteTransaction(cur, id)
                elif command == 'modify':
                    id = int(input("id: "))
                    command = input("date value account category tag exit: ").lower()
                    if command == 'date':
                        register.modifyTransactionDate(cur, id, readDate())
                    elif command == 'value':
                        value = float(input("Value: "))
                        register.modifyTransactionValue(cur, id, value)
                    elif command == 'account':
                        account = str(input("Account Name: "))
                        register.modifyTransactionAccount(cur, id, account)
                    elif command == 'category':
                        print(categories.getCategories(db))
                        category = str(input("Category (from above options): "))
                        register.modifyTransactionCategory(cur, id, category)
                    elif command == 'tag':
                        tag = str(input("Tag: "))
                        register.modifyTransactionTag(cur, id, tag)
                    elif command == 'exit':
                        break
                    else:
                        print("invalid input")
                        continue
                elif command == 'match':
                    id1 = int(input("first transaction id: "))
                    id2 = int(input("second transaction id: "))
                    register.matchTransactions(cur, id1, id2)
                elif command == 'unmatch':
                    id1 = int(input("first transaction id: "))
                    id2 = int(input("second transaction id: "))
                    register.unmatchTransactions(cur, id1, id2)
                elif command == 'view':
                    print(register.getTransactions(db).to_markdown(index=False))
                elif command == 'exit':
                    break
                else:
                    print('invalid input')
                    continue
        elif command == 'investments':
            while True:
                command = input("add delete view exit: ").lower()
                if command == 'add':
                    date = readDate()
                    ticker = input("Ticker: ").upper()
                    cost = float(input("Cost: "))
                    shares = float(input("Shares: "))
                    account = input("Account name: ")
                    investments.addInvestment(cur,date[0],date[1],date[2],ticker,cost,shares,account)
                elif command == 'delete':
                    id = int(input("id: "))
                    investments.deleteInvestment(cur, id)
                elif command == 'view':
                    command = input("security lots exit: ").lower()
                    if command == 'security':
                        df = investments.getInvestments(cur)
                        if df is not None: print(df.to_markdown(index=False))
                    elif command == 'lots':
                        df = investments.getLots(cur)
                        if df is not None: print(df.to_markdown(index=False))
                    elif command == 'exit':
                        break
                    else:
                        print('invalid input')
                        continue
                elif command == 'exit':
                    break
                else:
                    print('invalid input')
                    continue
        elif command == 'accounts':
            while True:
                command = input("add view exit: ").lower()
                if command == 'add':
                    accountName = input("account name: ")
                    accounts.addAccount(cur, accountName)
                elif command == 'view':
                    print(accounts.getAccounts(db).to_markdown(index=False))
                elif command == 'exit':
                    break
                else:
                    print('invalid input')
                    continue
        elif command == 'totals':
            command = input("year month account: ").lower()
            if command == 'year':
                print(register.getAnnualTotals(cur).to_markdown(index=False))
            elif command == 'month':
                print(register.getMonthlyTotals(cur).to_markdown(index=False))
            elif command == 'account':
                print(register.getAccountTotals(cur))
        elif command == 'paychecks':
            while True:
                command = input("add delete view exit: ").lower()
                if command =='add':
                    date = readDate()
                    gross = float(input("Gross Pay: "))
                    federal = float(input("Federal Tax: "))
                    state = float(input("State Tax: "))
                    local = float(input("Local Tax: "))
                    medicare = float(input("Medicare Tax: "))
                    socialsecurity = float(input("Social Security Tax: "))
                    health = float(input("Health Insurance: "))
                    dental = float(input("Dental Insurance: "))
                    vision = float(input("Vision Insurance: "))
                    hsa = float(input("HSA Contribution: "))
                    k = float(input("401k Contribution: "))
                    rothk = float(input("Roth 401k Contribution: "))
                    paychecks.addPaycheck(cur, date[0],date[1],date[2],gross,federal,state,local,medicare,socialsecurity,health,dental,vision,hsa,k,rothk)
                elif command == 'delete':
                    id = int(input("id: "))
                    paychecks.deletePaycheck(cur, id)
                elif command == 'view':
                    print(paychecks.getPaychecks(db).to_markdown(index=False))
                elif command == 'exit':
                    break
                else:
                    print('invalid input')
                    continue
        elif command == 'exit':
            shutdown(db)
        else: 
            continue
        