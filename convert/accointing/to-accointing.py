#!/user/bin/env python3

# IMPORTANT: See TO-ACCOINTING.md
# One-off scrypt for converting some CSV formats to a CSV format based on the Accointing template.

import argparse
import json
import os.path
import sys
from collections import OrderedDict
from csv import QUOTE_NONNUMERIC, QUOTE_ALL
from enum import Enum
from pytz import timezone             # pytz: https://pythonhosted.org/pytz/#tzinfo-api
import pytz
import petl as etl                    # PETL: https://petl.readthedocs.io/en/stable/index.html


#
# -------- DEFINITIONS --------
#
# TODO: It would be preferable that the assigned values below were mostly externalized in the same way that values in
#   the `classify.json` and `pairs.json` files are externalized.


TxSource = Enum('TxSource', ['UNKNOWN', 'BINANCE_US', 'BLOCKFI', 'CELSIUS', 'TRADESTATION'])
TxType = Enum('TxType', ['COMMON', 'NONTRADE', 'TRADE'])

BINANCE_US_HEADER = ('User_Id','Time','Category','Operation','Order_Id','Transaction_Id','Primary_Asset','Realized_Amount_For_Primary_Asset','Realized_Amount_For_Primary_Asset_In_USD_Value','Base_Asset','Realized_Amount_For_Base_Asset','Realized_Amount_For_Base_Asset_In_USD_Value','Quote_Asset','Realized_Amount_For_Quote_Asset','Realized_Amount_For_Quote_Asset_In_USD_Value','Fee_Asset','Realized_Amount_For_Fee_Asset','Realized_Amount_For_Fee_Asset_In_USD_Value','Payment_Method','Withdrawal_Method','Additional_Note')
BINANCE_US_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

BLOCKFI_HEADER = ('Cryptocurrency','Amount','Transaction Type','Confirmed At')
BLOCKFI_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

CELSIUS_HEADER = ('Internal id','Date and time','Transaction type','Coin type','Coin amount','USD Value','Original Reward Coin','Reward Amount In Original Coin','Confirmed')
CELSIUS_DATETIME_FORMAT = "%B %d, %Y %I:%M %p"

TS_NONTRADE_HEADER = ('Account','Date','Time','Type','Asset','Amount','Unit','Details','TransactionID','Notes')
TS_TRADE_HEADER = ('Account','Date','Time','BoughtSold','Quantity','Symbol','ExecutionPrice','ExecutionUnit','Amount','Unit','Fee','FeeUnit','TransactionID','Notes')
TS_NONTRADE_DEFAULT_TIME_STR = "11:00:00 AM"
TS_DATETIME_FORMAT = "%m/%d/%Y %I:%M:%S %p"

IDENTIFY_MAP = {
    BINANCE_US_HEADER: (TxSource.BINANCE_US, TxType.COMMON),
    BLOCKFI_HEADER: (TxSource.BLOCKFI, TxType.COMMON),
    CELSIUS_HEADER: (TxSource.CELSIUS, TxType.COMMON),
    TS_NONTRADE_HEADER: (TxSource.TRADESTATION, TxType.NONTRADE),
    TS_TRADE_HEADER: (TxSource.TRADESTATION, TxType.TRADE)
}

TZ_DEFAULT_MAP = {
    TxSource.BLOCKFI: timezone("US/Eastern"),
    TxSource.CELSIUS: None, # `None` implies pass-through (no conversion).  Celsius CSV is already UTC.
    TxSource.TRADESTATION: timezone("US/Eastern")
}

ACCOINTING_HEADER_ROW = ['transactionType','date','inBuyAmount','inBuyAsset','outSellAmount','outSellAsset','feeAmount (optional)','feeAsset (optional)','classification (optional)','operationId (optional)','comments (optional)']
ACCOINTING_DATETIME_FORMAT = "%m/%d/%Y %H:%M:%S"

CLASSIFY_MAP = {}
PAIR_MAP = {}
INPUT_TZ = None   # `None` implies pass-through (no conversion).

UNIQUE_ORDERS = set()

#
# -------- CONFIG FUNCTIONS --------
#

def get_classify_map(regionStr):

    f = open('config/classify.json')
    jsonDict = json.load(f)
    f.close()

    if not regionStr in jsonDict:
        raise Exception("Specified region '{}' not found in classify.json".format(regionStr))

    return jsonDict[regionStr]


def get_pair_map():
    
    f = open('config/pairs.json')
    jsonDict = json.load(f)
    f.close()

    return jsonDict

#
# -------- UTILITY FUNCTIONS --------
#

def separate_pair(tradingPairStr):

    return PAIR_MAP.get(tradingPairStr, ("???", "???"))



#
# -------- CONVERSION FUNCTIONS --------
#

def classify_tx(txSource, txField, tx):

    fieldMap = CLASSIFY_MAP.get(str(txSource), None)
    if (not fieldMap):
        raise Exception("Source '{}' not found in CLASSIFY_MAP.".format(str(txSource)))
    
    valueMap = fieldMap.get(txField, None)
    if (not valueMap):
        raise Exception("Field '{}' not found in field map for source '{}'.".format(txField, str(txSource)))
    
    return valueMap.get(tx[txField], None)


# ---- Binance.us ----

binance_us_dt_parser = etl.util.parsers.datetimeparser(BINANCE_US_DATETIME_FORMAT)

def binance_us_dt_xform(dateTimeStr) -> str:

    if (INPUT_TZ == None):
        return binance_us_dt_parser(dateTimeStr).strftime(ACCOINTING_DATETIME_FORMAT) 

    loc_dt = binance_us_dt_parser(dateTimeStr)
    INPUT_TZ.localize(loc_dt, is_dst=True)
    utc_dt = loc_dt.astimezone(pytz.utc)
    return utc_dt.strftime(ACCOINTING_DATETIME_FORMAT)


def binance_us_row_mapper(tx):

    typeMap = {
        'Deposit':"deposit",
        'Distribution':"deposit",
        'Withdrawal':"withdraw",
        'Buy':"order", 
        'Convert':"order", 
        'Sell':"order", 
        'Spot Trading':"order"
    }

    txIsDeposit =  typeMap[tx['Category']] == "deposit"
    txIsWithdrawal = typeMap[tx['Category']] == "withdraw"
    txIsOrder = typeMap[tx['Category']] == "order"

    transactionType = typeMap.get(tx['Category'], "???")
    txDate = binance_us_dt_xform(tx['Time'])

    if txIsDeposit:
        inBuyAmount = tx['Realized_Amount_For_Primary_Asset']
        inBuyAsset = tx['Primary_Asset']
        outSellAmount = None
        outSellAsset = None

    if txIsWithdrawal:
        inBuyAmount = None
        inBuyAsset = None
        outSellAmount = tx['Realized_Amount_For_Primary_Asset']
        outSellAsset = tx['Primary_Asset']

    if txIsOrder:

        if (tx['Category'] == 'Buy' and tx['Operation'] == 'Buy'):   # Double-checked
            inBuyAmount = tx['Realized_Amount_For_Quote_Asset']
            inBuyAsset = tx['Quote_Asset']
            outSellAmount = tx['Realized_Amount_For_Base_Asset']
            outSellAsset = tx['Base_Asset']

        if (tx['Category'] == 'Sell' and tx['Operation'] == 'Sell'):  # Double-checked
            inBuyAmount = tx['Realized_Amount_For_Quote_Asset']
            inBuyAsset = tx['Quote_Asset']
            outSellAmount = tx['Realized_Amount_For_Base_Asset']
            outSellAsset = tx['Base_Asset']

        if (tx['Category'] == 'Spot Trading' and tx['Operation'] == 'Buy'):  # Double-checked
            inBuyAmount = tx['Realized_Amount_For_Base_Asset']
            inBuyAsset = tx['Base_Asset']
            outSellAmount = tx['Realized_Amount_For_Quote_Asset']
            outSellAsset = tx['Quote_Asset']
        
        if (tx['Category'] == 'Spot Trading' and tx['Operation'] == 'Sell'):  # Double-checked
            inBuyAmount = tx['Realized_Amount_For_Quote_Asset']
            inBuyAsset = tx['Quote_Asset']
            outSellAmount = tx['Realized_Amount_For_Base_Asset']
            outSellAsset = tx['Base_Asset']

        if (tx['Category'] == 'Convert' and tx['Operation'] == 'Convert'):  #
            inBuyAmount = tx['Realized_Amount_For_Quote_Asset']
            inBuyAsset = tx['Quote_Asset']
            outSellAmount = tx['Realized_Amount_For_Base_Asset']
            outSellAsset = tx['Base_Asset']

    feeAmount = tx['Realized_Amount_For_Fee_Asset']
    feeAsset = tx['Fee_Asset']
    classification = classify_tx(TxSource.BINANCE_US, 'Operation', tx)
    operationId = tx['Order_Id']
    if (tx['Additional_Note']):
        comments = "Transaction_Id: {}; {}".format(tx['Transaction_Id'], tx['Additional_Note'])
    else:
        comments = "Transaction_Id: {}".format(tx['Transaction_Id'])

    # Since The Binance.US CSV stores multiple fills for a single order, a set will be used to determine the
    # number of unique orders.
    global UNIQUE_ORDERS
    UNIQUE_ORDERS.add(tx['Order_Id'])

    return [transactionType, txDate, inBuyAmount, inBuyAsset, outSellAmount, outSellAsset, feeAmount, feeAsset, classification, operationId, comments]


# ---- BlockFi ----

blockfi_dt_parser = etl.util.parsers.datetimeparser(BLOCKFI_DATETIME_FORMAT)

def blockfi_dt_xform(dateTimeStr) -> str:

    if (INPUT_TZ == None):
        return blockfi_dt_parser(dateTimeStr).strftime(ACCOINTING_DATETIME_FORMAT)

    loc_dt = blockfi_dt_parser(dateTimeStr)
    INPUT_TZ.localize(loc_dt, is_dst=True)
    utc_dt = loc_dt.astimezone(pytz.utc)
    return utc_dt.strftime(ACCOINTING_DATETIME_FORMAT)


def blockfi_row_mapper(tx):

    blockFiDepositTypes = {'BIA Deposit', 'Crypto Transfer', 'Interest Payment', 'Referral Bonus'}
    blockFiWithdrawalTypes = {'BIA Withdraw', 'Withdrawal'}

    txIsDeposit =  tx['Transaction Type'] in blockFiDepositTypes
    txIsWithdrawal = tx['Transaction Type'] in blockFiWithdrawalTypes

    transactionType = "deposit" if txIsDeposit else ( "withdraw" if txIsWithdrawal else "???" )
    txDate = blockfi_dt_xform(tx['Confirmed At'])
    inBuyAmount = tx['Amount'] if txIsDeposit else None
    inBuyAsset = tx['Cryptocurrency'] if txIsDeposit else None
    outSellAmount = tx['Amount'].lstrip('-') if txIsWithdrawal else None
    outSellAsset = tx['Cryptocurrency'] if txIsWithdrawal else None
    feeAmount = None
    feeAsset = None
    classification = classify_tx(TxSource.BLOCKFI, 'Transaction Type', tx)
    operationId = None
    comments = tx['Transaction Type']

    return [transactionType, txDate, inBuyAmount, inBuyAsset, outSellAmount, outSellAsset, feeAmount, feeAsset, classification, operationId, comments]


# ---- Celsius ----

celsius_dt_parser = etl.util.parsers.datetimeparser(CELSIUS_DATETIME_FORMAT)

def celsius_dt_xform(dateTimeStr) -> str:
    
    if (INPUT_TZ == None):
        return celsius_dt_parser(dateTimeStr).strftime(ACCOINTING_DATETIME_FORMAT)

    loc_dt = celsius_dt_parser(dateTimeStr)
    INPUT_TZ.localize(loc_dt, is_dst=True)
    utc_dt = loc_dt.astimezone(pytz.utc)
    return utc_dt.strftime(ACCOINTING_DATETIME_FORMAT)


def celsius_row_mapper(tx):

    celsiusDepositTypes = {'Referred Award', 'Reward', 'Transfer'}
    celsiusWithdrawalTypes = {'Withdrawal'}

    txIsDeposit = ( tx['Transaction type'] in celsiusDepositTypes ) or ( tx['Transaction type'] == "" and float(tx['Coin amount']) >= 0 )
    txIsWithdrawal = ( tx['Transaction type'] in celsiusWithdrawalTypes ) or ( tx['Transaction type'] == "" and float(tx['Coin amount']) < 0 )

    transactionType = "deposit" if txIsDeposit else ( "withdraw" if txIsWithdrawal else "???" )
    txDate = celsius_dt_xform(tx['Date and time'])
    inBuyAmount = tx['Coin amount'] if txIsDeposit else None
    inBuyAsset = tx['Coin type'] if txIsDeposit else None
    outSellAmount = tx['Coin amount'].lstrip('-') if txIsWithdrawal else None
    outSellAsset = tx['Coin type'] if txIsWithdrawal else None
    feeAmount = None
    feeAsset = None
    classification = classify_tx(TxSource.CELSIUS, 'Transaction type', tx)
    operationId = tx['Internal id']
    comments = None

    return [transactionType, txDate, inBuyAmount, inBuyAsset, outSellAmount, outSellAsset, feeAmount, feeAsset, classification, operationId, comments]


# ---- TradeStation ----

ts_dt_parser = etl.util.parsers.datetimeparser(TS_DATETIME_FORMAT)

def ts_dt_xform(dateStr, timeStr) -> str:

    dateTimeStr = "{} {}".format(dateStr, (timeStr if timeStr else TS_NONTRADE_DEFAULT_TIME_STR) )

    if (INPUT_TZ == None):
        return ts_dt_parser(dateTimeStr).strftime(ACCOINTING_DATETIME_FORMAT)

    loc_dt = ts_dt_parser(dateTimeStr)
    INPUT_TZ.localize(loc_dt, is_dst=True)
    utc_dt = loc_dt.astimezone(pytz.utc)
    return utc_dt.strftime(ACCOINTING_DATETIME_FORMAT)


def ts_nontrade_rowmapper(tx):

    tsDepositTypes = {'Deposit', 'Interest'}
    tsWithdrawalTypes = {'Withdrawal'}

    txIsDeposit = ( tx['Type'] in tsDepositTypes )
    txIsWithdrawal = ( tx['Type'] in tsWithdrawalTypes )

    transactionType = "deposit" if txIsDeposit else ( "withdraw" if txIsWithdrawal else "???" )
    txDate = ts_dt_xform(tx['Date'], tx['Time'])
    inBuyAmount = tx['Amount'] if (tx['Type'] == "Deposit" or tx['Type'] == "Interest") else None
    inBuyAsset = tx['Unit'] if (tx['Type'] == "Deposit" or tx['Type'] == "Interest") else None
    outSellAmount = tx['Amount'] if (tx['Type'] == "Withdrawal") else None
    outSellAsset = tx['Unit'] if (tx['Type'] == "Withdrawal") else None
    feeAmount = None
    feeAsset = None
    classification = classify_tx(TxSource.TRADESTATION, 'Type', tx)
    operationId = tx['TransactionID']
    comments = "{}; {}".format(tx['Details'], tx['Notes']) if (tx['Notes']) else tx['Details']

    return [transactionType, txDate, inBuyAmount, inBuyAsset, outSellAmount, outSellAsset, feeAmount, feeAsset, classification, operationId, comments]


def ts_trade_rowmapper(tx):

    if not (tx['BoughtSold'] == "BOUGHT" or tx['BoughtSold'] == "SOLD"):
        raise Exception("Invalid value '{}' in 'BoughtSold' field.".format(tx['BoughtSold']))

    transactionType = 'order'
    txDate = ts_dt_xform(tx['Date'], tx['Time'])

    if (tx['BoughtSold'] == "BOUGHT"):
        inBuyAmount = tx['Quantity']
        inBuyAsset = separate_pair(tx['Symbol'])[0]
        outSellAmount = tx["Amount"]
        outSellAsset = separate_pair(tx['Symbol'])[1]

    if (tx['BoughtSold'] == "SOLD"):
        inBuyAmount = tx["Amount"]
        inBuyAsset = separate_pair(tx['Symbol'])[1]
        outSellAmount = tx['Quantity']
        outSellAsset = separate_pair(tx['Symbol'])[0]

    feeAmount = tx['Fee']
    feeAsset = tx['FeeUnit']
    classification = None
    operationId = tx['TransactionID']
    comments = tx['Notes']

    return [transactionType, txDate, inBuyAmount, inBuyAsset, outSellAmount, outSellAsset, feeAmount, feeAsset, classification, operationId, comments]


# ---- Rowmapper Map ----

ROWMAPPER_MAP = {
    (TxSource.BINANCE_US, TxType.COMMON): binance_us_row_mapper,
    (TxSource.BLOCKFI, TxType.COMMON): blockfi_row_mapper,
    (TxSource.CELSIUS, TxType.COMMON): celsius_row_mapper,
    (TxSource.TRADESTATION, TxType.NONTRADE): ts_nontrade_rowmapper,
    (TxSource.TRADESTATION, TxType.TRADE): ts_trade_rowmapper
}

def get_file_context(filename):

    fileContextDict = {}
    fileContextDict['filename'] = filename

    # Does the file Exist
    if (not os.path.isfile(filename)):
        fileContextDict['success'] = False
        fileContextDict['message'] = "File does not exist."
        return fileContextDict

    # Create a table
    fileContextDict['table'] = etl.fromcsv(filename)

    # Remove leading and trailing white space from field names in the header for identification.
    stripped = [v.strip() for v in etl.header(fileContextDict['table'])]
    fileContextDict['table'] = etl.transform.headers.setheader(fileContextDict['table'], stripped)

    # Determine Source Type
    idTuple = IDENTIFY_MAP.get(etl.header(fileContextDict['table']), (TxSource.UNKNOWN, TxType.COMMON))

    fileContextDict['source'] = idTuple[0]
    fileContextDict['type'] = idTuple[1]
 
    if (fileContextDict['source'] == TxSource.UNKNOWN):
        fileContextDict['success'] = False
        fileContextDict['message'] = "Unrecognized header in file: '{}'".format(filename)
        return fileContextDict

    fileContextDict['rowmapper'] = ROWMAPPER_MAP.get(idTuple, None)

    if (not fileContextDict['rowmapper']):
        raise Exception("Missing ROWMAPPER_MAP entry for idTuple ({},{}).".format(TxSource, TxType))

    fileContextDict['success'] = True
    fileContextDict['message'] = None

    return fileContextDict


#
# -------- MAIN --------
#

def main() -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--region", help="Specify which region within 'classify.json' is used for classifications.")
    parser.add_argument("-t", "--timezone", help="Specify the timezone for times within the input files.")
    parser.add_argument("-i", "--input", help="Specify -i/--input for each input file.", action="extend", nargs="+", required=True)
    parser.add_argument("-o", "--output", help="The output filename.")

    args = parser.parse_args()

    global CLASSIFY_MAP
    if (args.region):
        CLASSIFY_MAP = get_classify_map( args.region.lower() )
    else:
        sys.stderr.write("Using default region of 'us' for transaction classifications.\n")
        CLASSIFY_MAP = get_classify_map("us")

    global PAIR_MAP
    PAIR_MAP = get_pair_map()

    # Validate that the user-supplied timezone (if present) is valid for pytz (if not "UTC").
    if (args.timezone):
        if args.timezone != "UTC":
            try:
                user_tz = timezone(args.timezone)
                sys.stderr.write("Using specified timezone for times within input files: '{}'.\n".format(user_tz))
            except pytz.exceptions.UnknownTimeZoneError:
                sys.stderr.write("Specified timezone is unknown (check spelling): '{}'.\n".format(args.timezone))
                return 1
        else:
            sys.stderr.write("Using specified timezone for times within input files: 'UTC'.\n")

    
    ctxList = []
    inputError = False
    sourceSet = set()
    for filename in args.input:
        ctx = get_file_context(filename)
        
        inputError |= not ctx["success"]
        if (not ctx["success"]):
            sys.stderr.write("ERROR: {0} -> '{1}'\n".format(ctx["message"], ctx["filename"]))
        else:
            sourceSet.add(ctx["source"])
            if (len(sourceSet) > 1):
                inputError = True
                sys.stderr.write("ERROR: File is from a different source. -> '{0}'\n".format(ctx["filename"]))
            else:
                ctxList.append(ctx)
                sys.stderr.write("Identified '{0}' as {1}\n".format(ctx['filename'], ctx['source']))

    if (inputError):
        sys.stderr.write("Conversion aborted.  See above input errors.\n")
        return 1

    # Make final determination of timezone for input files.
    global INPUT_TZ
    if (args.timezone):
        INPUT_TZ = timezone(args.timezone) if (args.timezone != "UTC") else None
    else:
        INPUT_TZ = TZ_DEFAULT_MAP.get(list(sourceSet)[0], None) if (len(sourceSet) > 0) else None

    sys.stderr.write("Input timezone: {}.\n".format(INPUT_TZ if INPUT_TZ else "None (UTC assumed)"))

    # Convert each file and stack it onto the resultTable
    resultTable = [ACCOINTING_HEADER_ROW]
    for ctx in ctxList:
        outTable = etl.rowmap(ctx['table'], ctx['rowmapper'], header=ACCOINTING_HEADER_ROW, failonerror=True)
        resultTable = etl.stack(resultTable, outTable)

    # Write the csv to the specified output, or to stdout if no output was specified.
    etl.io.csv.tocsv(resultTable, args.output if args.output else etl.io.sources.StdoutSource(), quoting=QUOTE_NONNUMERIC)

    # Special case output for Binance.US: Show the number of unique orders.
    if (list(sourceSet)[0] == TxSource.BINANCE_US):
        global UNIQUE_ORDERS
        sys.stderr.write("Unique order count: {}\n".format(len(UNIQUE_ORDERS)))

    return 0


if __name__ == '__main__':
    sys.exit(main())
