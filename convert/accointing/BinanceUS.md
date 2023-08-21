# Binance.US #

**NOTE:** The Accointing interface allows you to delete wallets and exchanges.  This means that you can do your own
comparison between connecting to Binance.US via the API and exporting a CSV from Binance.US and importing the converted
CSV output by the `to-accointing.py` script and use whichever best suits your needs.  (See "My Comparison" section
below.)

**NOTE:** My dataset for Binance.US was of moderate size, however, I did not necessarily use all of the features of
Binance.US.  As a result, you may have transactions that the `to-accointing.py` script does not handle. As always, I
strongly recommend thoroughly checking any conversion result.

## My Comparison ##

Since Accointing natively supports the Binance.US API, this is a comparison between connecting to Binance.US with via
the API versus exporting a CSV of transactions from Binance.US, converting the exported CSV with the `to-accointing.py`
script, and then importing the converted CSV to Accointing.

For the time period in question, there was a total of 273 unique transactions, some of which were spot trades that had
multiple fills (see note below).  As a result, the total number of items (excluding the header line) in the exported CSV
was 372.


| Accointing import result   | Binance.US via API | Binance.US via converted CSV |
| -------------------------- | ------------------ | ---------------------------- |
| Imported transactions      |         215        |              372             |
| Transactions with warnings |          52        |                8             |
| Total warnings             |          59        |                8             |


* **Note:** There is some trickiness with regard to transaction counts.  If a Binance.US user executes spot trades, some
spot trades will have multiple sub-trades, more commonly known as "fills".  Multiple fills happen when the exchange
needs to match multiple opposite orders to fill an order.  A CSV exported from Binance.US will represent each fill on a
line, so a single order may be represented over multiple lines, but each line have the same order ID.


### Connect via API Result ###

I accomplished the API connection from Accointing to my Binance.US account by first creating a read-only API key via the
Binance.US web interface.  Then, back in the Accointing web interface, I selected Wallets from the left-side menu,
clicked the (+ Add New) button to the right of the Exchanges section heading, and choosing Binance.US from the list.  I
then chose the option for Automatic (API key).  I then filled the Wallet name, API key, and Secret key information and
clicked the (Connect wallet) button to begin the import.

Binance.US token balances somehow appeared correct after adding Binance.US via an API connection, but only 215
transactions appeared in the Accointing interface. (Enabling showing of ignored transactions did not show any additional
transactions.)  There should be 273 transactions assuming Accointing is representing spot trades that have multiple
fills as a single transaction, meaning that - at the very least - 58 transactions were missing.  The Accointing
documentation mentions a limitation in their support of the Binance.US API where transactions that are "Conversions" or
that are "Commissions from referral program" must be manually added.  However, only one of my transactions met this
criteria.  I noticed immediately that at least one regular "Buy" transaction was missing (and clearly so were 57 other
transactions).

In terms of errors, 51 transactions had "No purchase history" errors, which is likely a side-effect of the missing
transactions.  8 transactions were unclassified which were due to transfers to wallets not yet added into Accounting.
Total transactions with issues: 52.


### Converted CSV Import Result ###

I accomplished the import of the CSV file output from `to-accointing.py` by selecting Wallets from the left-side menu,
clicking the (+ Add New) button to the right of the Exchanges section heading, typing "custom" into the search box, and
choosing the Custom Wallet (only choice) below the search area.  I then chose the "File import" option and dropped the
CSV file output from `to-accointing.py` into the drop zone. I left the "Start import from a certain date (optional)" on
the default value of "Import full history", and lastly clicked the "Save" button to begin the import.

The import recognized 372 transactions (same count upon enabling showing of ignored transactions), so apparently when
importing this way, orders with multiple fills are not consolidated.

After matching up the internal transfers, there remained 8 "Unclassified" transactions due to another wallet not yet
added to Accointing.  Another 8 transactions had the error of "No purchase history...".  Since the final token balances
appear to be correct, this may simply be due to the fact that Binance.US makes ACH deposited funds available
immediately, but the actual deposit may take more time.  Transactions that use funds immediately after the ACH deposit,
such as crypto buys, may get a timestamp prior to that of the ACH deposit.

The resulting token balances were correct.


[Back](TO-ACCOINTING.md)
