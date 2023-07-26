# TradeStation #

TradeStation, as far as I have been able to determine, does not provide any way to export crypto transactions in a CSV
format (correct me, if you know of a way).  All that is available are crypto confirmation PDF files.  As a result, it's
necessary to manually transcribe the data from the PDF files into a CSV file.  (Yes, a PDF text scraper might work, but
I didn't have time for that.)

If you have a small number of transactions, it may be best to simply download the Accointing Excel Template, populate
it, and then import that back into Accointing.

However, the Accointing template is not structured the same way as the information in TradeStation's crypto confirmation
PDF files, and I prefer to have a CSV representation that matches the source data as closely as practical.  As a result,
I have created two CSV formats for TradeStation crypto transactions:  One for Trade transactions (buy or sell crypto)
and one for Non-Trade transactions (send, receive, interest).  The reason for having two different formats is due to the
fact that the crypto confirmation PDFs have a different representation for Trade versus Non-Trade transactions.  

For data entry, it may be easier to create a spreadsheet with column headers that *exactly* match the CSV headers shown
below and then export it to CSV after entering all the transactions.  Then convert that CSV with the `to-accointing.py`
script, and finally import the converted CSV into Accointing.

Since the time values in the crypto confirmation PDFs for US appear to be in the "US/Eastern" time zone, this is the
timezone that the `to-accointing.py` script will use by default.  If you choose to use a different timezone for the
time values, you can use the `-t` option to specify the correct timezone.

The `to-accointing.py` script will automatically classify *some* transactions to save the user time.  The automatic
classifications are controlled by the `classify.json` file.  Note that if you edit the `classify.json` file, be aware
that Accointing silently ignores transactions that it does not understand, so check your import carefully.

**NOTE:**  The two CSV formats below do not include fiat deposits into the trading account because those transactions
are not present in the crypto confirmation PDF files.  Accounting will probably need this information, so you may need
to add fiat deposit transactions manually using the Accointing interface, or add them manually to the Non-Trade CSV.


## TradeStation Non-Trade CSV ##

The header for the Non-Trade CSV is as follows:

    Account,Date,Time,Type,Asset,Amount,Unit,Details,TransactionID,Notes

The field names correspond to what is found in the "DIGITAL ASSET - NON TRADE TRANSACTIONS" section of the PDF.  The
field names are slightly modified in some cases to remove spaces or special characters.

**Account**: Is the account number.

**Date**: Is the date in annoying American format MM/DD/YYYY (e.g., "01/24/2022" ) to match the way dates are
represented in the PDF.

**Time**: 12-hour format with HH:MM:SS PM, e.g., "11:00:00 AM". The PDFs weirdly do not include times for non-trade
transactions, so the Time field may be left empty in the CSV. However, Accointing may require the time in order to
recognize an internal transfer.  Note that when the Time field is empty, the `to-accointing` script will assign a
default time.

**Type**: Is the transaction type: Deposit, Interest, or Withdrawal.

**Asset**: Is the crypto symbol such as BTC, ETH, USDC.

**Amount**: Amount is the amount of the transaction.

**Unit**: Is the currency of the transaction, such as BTC, ETH, USDC, and so forth (seems to always match the Asset).

**Details**: A verbal description of the transaction, sometimes containing a destination wallet address.

**TransactionID**: TradeStation's transaction ID.  TradeStation appears to have a convention of expressing non-trade
transaction IDs in all lower-case letters.

**Notes**: Any notes you want to add.  I usually include the name of the crypto confirmation PDF file that contains the
transaction for my own reference.


## TradeStation Trade CSV ##

The header for the Trade CSV is as follows:

    Account,Date,Time,BoughtSold,Quantity,Symbol,ExecutionPrice,ExecutionUnit,Amount,Unit,Fee,FeeUnit,TransactionID,Notes

The field names correspond to what is found in the "DIGITAL ASSET - TRADES" section of the PDF.  The field names are
slightly modified in some cases to remove spaces or special characters.

**Account**: Is the account number.

**Date**: Is the date in annoying American format MM/DD/YYYY (e.g., "01/24/2022" ) to match the way dates are
represented in the PDF.

**Time**: 12-hour format with HH:MM:SS PM, e.g., "11:00:00 AM".

**BoughtSold**: Must be either: BOUGHT or SOLD.

**Quantity**: The quantity of the left-side asset.

**Symbol**: A compound "trading pair" symbol, such as ETHUSD (ETH priced in USD).  **NOTE**: Each pair must exist in the
`pairs.csv` file so that the `to-accointing.py` script can unambiguously separate them into left-side and right-side.

**ExecutionPrice**: The price of the left-side asset in terms of the right-side asset.

**ExecutionUnit**: This should typically match the right-side asset's symbol.

**Amount**:  The amount of right-side asset.

**Unit**:  The right-side asset's symbol.

**Fee**:  The amount of fee paid for the transaction.

**FeeUnit**:  The symbol in which the fee was paid.

**TransactionID**: TradeStation's transaction ID.  TradeStation appears to have a convention of expressing trade
transaction IDs in all upper-case letters.

**Notes**:  Any notes you want to add.  I usually include the name of the crypto confirmation PDF file that contains the
transaction for my own reference.


[Back](TO-ACCOINTING.md)
