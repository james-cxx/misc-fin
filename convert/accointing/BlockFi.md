# BlockFi #

**NOTE:** The Accointing interface allows you to delete wallets and exchanges.  This means that you can do your own
comparison between importing the CSV exported from BlockFi and importing the converted CSV output by the
`to-accointing.py` script and use whichever best suits your needs.  (See "My Comparison" section below.)

**NOTE:** My dataset for BlockFi is very small consisting of only 32 transactions.  Furthermore, I did not make use of
the loan feature of BlockFi, so I have no idea about how loan-related transactions are expressed in a CSV downloaded
from BlockFi.  As a result, you may have transactions that the `to-accointing.py` script does not handle. As always, I
strongly recommend thoroughly checking any conversion result.

**NOTE:** IMPORTANT:  When a trade is done in BlockFi, the CSV exported from BlockFi will contain two lines for the
trade:  One line for the "In" asset (with a positive 'Amount') and another line for the "Out" asset (with a negative
'Amount').  *Both lines will have the same 'Confirmed At' time.*  The `to-accointing.py` script currently does not
consolidate these two lines into one line *as required by the Accointing template format*, so *after the conversion to
the Accounting format*, the two lines of the trade *must be manually combined into one line* before importing the
converted CSV into Accointing.

**NOTE:** A similar situation to the trade case above occurs with withdrawal fees, such that the withdrawal fee is
recorded on a separate line from the withdrawal that incurred the fee.  *Both lines will have the same 'Confirmed At'
time.* However, the consolidation of the two lines into one line is optional, since the withdrawal fee transaction will
still be recorded as a fee.  (However, it is more accurate to combine the lines into one line.)

The CSV downloaded from the BlockFi website (typically named `trade_report_all.csv`) includes transfers between the
BlockFi interest account and custody account, which are designated as "BIA Deposit" and "BIA Withdraw".  The default
behavior of the `to-accointing.py` script is to classify these internal transfers as "ignored".  However, this means
that not all transactions in the converted CSV will be imported into Accointing, since Accointing will skip the ignored
transactions.

As a result, the number of transactions shown after converting the BlockFi CSV with `to-accointing.py` and then
importing into Accointing will be the total number of transactions in the CSV less the number of "BIA Deposit" and "BIA
Withdraw" transactions.

In the CSV file that I downloaded from BlockFi, time values are specified in the "US/Eastern" time zone.  If you find
otherwise in the CSV that you download from BlockFi, the `to-accointing.py` script will not interpret the time values
within the CSV correctly.  In this case, you can use the `-t` option to specify the correct timezone for the time values
in the CSV file.

The `to-accointing.py` script will automatically classify *some* transactions to save the user time.  The automatic
classifications are controlled by the `classify.json` file.  Note that if you edit the `classify.json` file, be aware
that Accointing silently ignores transactions that it does not understand, so check your import carefully.


## My Comparison ##

The CSV file that I downloaded from BlockFi has 32 transactions.  Of these, 6 transactions were internal transfers
(indicated as "BIA Deposit" or "BIA Withdraw").

Given the BlockFi CSV as input, the CSV file output from `to-accointing.py` (referred to as the "converted CSV") also
has 32 transactions, with the 6 internal transfers being classified as "ignored".


| Accointing import result   | BlockFi CSV | Converted CSV |
| -------------------------- | ----------- | ------------- |
| Imported transactions      |      23     |        26     |
| Transactions with warnings |      23     |         6     |
| Total warnings             |      25     |         6     |


### BlockFi CSV Import Result ###

I accomplished the import of the BlockFi CSV file by selecting Wallets from the left-side menu, clicking the (+ Add New)
button to the right of the Exchanges section heading, and choosing BlockFi from the list.  I then chose the "File
import" option and dropped the BlockFi CSV into the drop zone to the right side. I left the "Start import from a certain
date (optional)" on the default value of "Import full history", and lastly clicked the "Save" button to begin the
import.

I would have expected either 32 imported transactions (all transactions retained) or 26 transactions (if the internal
transfers are ignored.).  Instead there was a bizarre 23 transfers imported.  When importing the BlockFi CSV, Accointing
appears to have ignored all six internal transfers (indicated as "BIA Deposit" or "BIA Withdraw"), which is acceptable.
Unfortunately, it also ignored all three transactions indicated as "Crypto Transfer" without any warning! "Crypto
Transfer" seems to be BlockFi's way of indicating a deposit of crypto from an outside source.  Ouch!  I can't imagine
the amount of confusion this must be causing users.

No transactions were classified, and so all imported transactions had the warning: "Unclassified: Classification is
missing, check the circumstances under which each classification should be applied here".  I don't really understand why
Accointing doesn't classify the interest payment as "Staking rewards", since this is what the Accointing documentation
recommends.

Two withdrawal transactions also had warning:  "Missing Funds:  No purchase history for #### token."  This is clearly a
side-effect of the fact that the deposits were ignored, so Accointing cannot figure out where the funds came from.

Strangely, the final token balances in the account was essentially correct (of two tokens, one was exactly correct and
the other was off by less than a penny).  This is also disturbing because, by simply browsing the transactions, it's
obvious that there are no external transfers into the account and that the withdrawals greatly exceed the sum of the
interest and reward transactions.  I can only guess that Accointing must be making an assumption that there must have
been funds matching the withdrawal amounts.  But this is potentially very misleading, because it gives the impression
that the import was correct when in fact important transactions were silently ignored.  I have no idea how tax reporting
could be correct under these circumstances.

### Converted CSV Import Result ###

I accomplished the import of the CSV file output from `to-accointing.py` by selecting Wallets from the left-side menu,
clicking the (+ Add New) button to the right of the Exchanges section heading, typing "custom" into the search box, and
choosing the Custom Wallet (only choice) below the search area.  I then chose the "File import" option and dropped the
CSV file output from `to-accointing.py` into the drop zone. I left the "Start import from a certain date (optional)" on
the default value of "Import full history", and lastly clicked the "Save" button to begin the import.

As before, I would have expected either 32 imported transactions (all transactions retained) or 26 transactions (if the
internal transfers are ignored.)  And, in fact, the result was 26 transactions with the internal transfers not being
imported.  That's acceptable, but I would really prefer that Accointing import the ignored transactions and simply show
them  as ignored in the list of transactions.

Per the defaults of the `to-accointing.py` script, all interest transactions were classified as "Staking Income" and
referral rewards as "Bounty".  The 6 transactions with Warnings were all the "Unclassified: ..." warning, which is
exactly as expected, since these transactions were deposits from external sources or withdrawals to external
destinations, and there's no way for the `to-accointing.py` script to know whether those sources/destinations are
internal or not.  Hence they are unavoidably left as unclassified, requiring the user to classify them.

The resulting token balances were also essentially correct (of two tokens, one was exactly correct and the other was off
by less than a penny).


[Back](TO-ACCOINTING.md)
