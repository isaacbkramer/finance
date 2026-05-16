import pytest
import finance.database as dat
import finance.accounts as acc
import finance.categories as cat
import finance.register as reg
import finance.investments as inv

@pytest.fixture(scope="module")
def database():
    db = dat.create('test.db')
    cursor = dat.cursor(db)
    yield cursor
    db.commit()
    db.close()

def test_tables(database):
    """test functions that create database tables"""
    assert acc.createAccountsTable(database) == True
    assert reg.createTransactionsTable(database) == True
    assert inv.createInvestmentsTable(database) == True
    assert cat.createCategoriesTable(database) == True

def test_accounts(database):
    """test functions that add accounts to accounts table"""
    assert acc.addAccount(database, 'SAVINGS') == True
    assert acc.addAccount(database, 'BROKERAGE') == True

def test_valid_transaction(database):
    """test the creation of transactions"""
    assert reg.addTransaction(database, 2026, 4, 25, 100.00, 'SAVINGS', 'INCOME', 'NONE') == True
    totals = reg.getAccountTotals(database)
    series = totals.loc[totals['account'] == 'SAVINGS', 'total']
    assert len(series) == 1
    assert series.iloc[0] == 100.00
    assert reg.deleteTransaction(database, 1)

def test_invalid_transaction(database):
    """test the creation and rejection of invalid transactions"""
    assert reg.addTransaction(database, 2026, 4, 25, 100.00, 'CHECKING', 'INCOME', 'NONE') == False
    assert reg.addTransaction(database, 2026, 4, 25, 100.00, 'SAVINGS', 'TAXES', 'NONE') == False

def test_match_transactions(database):
    '''test the matching and unmatching of transaction pairs'''
    assert reg.addTransaction(database, 2026, 5, 14, 100.00, 'SAVINGS', 'INCOME', 'NONE') == True
    assert reg.addTransaction(database, 2026, 5, 15, -100.00, 'SAVINGS', 'FOOD', 'NONE') == True
    assert reg.matchTransactions(database, 1, 2) == True
    assert reg.unmatchTransactions(database, 1, 2) == True

    assert reg.addTransaction(database, 2026, 5, 15, -99.00, 'SAVINGS', 'FOOD', 'NONE') == True
    assert reg.matchTransactions(database, 1, 3) == False

def test_valid_investments(database):
    """test the creation of investments"""
    assert inv.addInvestment(database, 2026, 4, 25, 'VTSAX', 500, 1.0, 'BROKERAGE') == True
    assert inv.addInvestment(database, 2026, 4, 25, 'FXAIX', 1000, 2.0, 'BROKERAGE') == True

    totals = inv.getInvestments(database)

    series = totals.loc[totals['Ticker'] == 'VTSAX', 'Shares']
    assert len(series) == 1
    assert series.iloc[0] == 1.0

    series = totals.loc[totals['Ticker'] == 'FXAIX', 'Shares']
    assert len(series) == 1
    assert series.iloc[0] == 2.0

def test_invalid_investment(database):
    """test the creation and rejection of invalid investments"""
    assert inv.addInvestment(database, 2026, 4, 25, 'FXAIX', 1000, 2.0, 'IRA') == False

def test_get_tickers(database):
    """test getting investment tickers"""
    tickers = inv.getTickers(database)
    assert len(tickers) == 2
