# Celsius #

**NOTE:** The Accointing interface allows you to delete wallets and exchanges.  This means that you can do your own
comparison between importing the CSV exported from Celsius and importing the converted CSV output by the
`to-accointing.py` script and use whichever best suits your needs.  (See "My Comparison" section below.)

**NOTE:**  I did not make use of the loan feature of Celsius Network, so I have no idea about how loan-related
transactions are expressed in a CSV downloaded from Celsius.  As a result, you may have transactions that the
`to-accointing.py` script does not handle. As always, I strongly recommend thoroughly checking any conversion result.


In the CSV file that I downloaded from Celsius, time values are specified in UTC.  If you find otherwise in the CSV that
you download from Celsius, the `to-accointing.py` script will not interpret the time values within the CSV correctly.
In this case, you can use the `-t` option to specify the correct timezone for the time values in the CSV file.

The `to-accointing.py` script will automatically classify *some* transactions to save the user time.  The automatic
classifications are controlled by the `classify.json` file.  Note that if you edit the `classify.json` file, be aware
that Accointing silently ignores transactions that it does not understand, so check your import carefully.


## My Comparison ##

The CSV file that I downloaded from Celsius has 213 transactions, however, this was an older CSV file that was missing
some transactions.  Since the Celsius website no longer supports downloading of transactions, I had to manually add four
transactions to the CSV file, resulting in a total of 217 transactions.

Given the Celsius CSV as input, the CSV file output from `to-accointing.py` (referred to as the "converted CSV") also
has 217 transactions, none of which are classified as "ignored".


| Accointing import result   | Celsius CSV | Converted CSV |
| -------------------------- | ----------- | ------------- |
| Imported transactions      |     217     |       217     |
| Transactions with warnings |     217     |        26     |
| Total warnings             |     430     |        26     |


### Celsius CSV Import Result ###

I accomplished the import of the Celsius CSV file by selecting Wallets from the left-side menu, clicking the (+ Add New)
button to the right of the Exchanges section heading, and choosing Celsius Network from the list.  I then chose the
"File import" option and dropped the Celsius CSV into the drop zone.  I left the "Start import from a certain date
(optional)" on the default value of "Import full history", and lastly clicked the "Save" button to begin the import.

The good news is that the import retained all 217 transactions from the CSV file.  And transaction times seem to have
correctly recognized as UTC within the CSV.

The bad news is that literally every transaction has a warning that requires user attention.  Of the warnings, all 217
transactions have the warning "Unclassified: Classification is missing, check the circumstances under which each
classification should be applied here" because Accointing apparently leaves classification of imported transactions
entirely to the user, which I find odd. I only spot-checked the other warnings, all of which appear to be "Missing
Funds:  No purchase history for #### token", which suggests that the import process isn't properly tracking deposits
from external sources and/or withdrawals to external destinations.  This is highly concerning to say the least.

Additionally, after the import, Accointing didn't show any token balance for Celsius.  No idea why, but I didn't bother
digging into it, since there is no way I would use such a messy import requiring so much manual effort to untangle.


### Converted CSV Import Result ###

I accomplished the import of the CSV file output from `to-accointing.py` by selecting Wallets from the left-side menu,
clicking the (+ Add New) button to the right of the Exchanges section heading, typing "custom" into the search box, and
choosing the Custom Wallet (only choice) below the search area.  I then chose the "File import" option and dropped the
CSV file output from `to-accointing.py` into the drop zone. I left the "Start import from a certain date (optional)" on
the default value of "Import full history", and lastly clicked the "Save" button to begin the import.

The import retained all 217 transactions. Transaction times were recognized as UTC within the converted CSV.  

Of the 217 imported transactions, 26 transactions had warnings.  All of the warnings were "Unclassified: Classification
is missing, check the circumstances under which each classification should be applied here".  Most of these are deposits
from external sources or withdrawals to external destinations, and there's no way for the `to-accointing.py` script to
know whether those sources/destinations are internal or not.  Hence they are unavoidably left as unclassified, requiring
the user to classify them.  The remaining transactions with this warning are caused by what appear to be internal
transactions between Celsius earn and custody accounts, where there are two identical transactions in terms of date,
token type and value, except one has a positive value and the other a negative value. In theory, these could be detected
and classified as "ignored", but for now the script does not handle these.

Finally, the resulting token balances shown in Accointing effectively matched the token balances shown by Celsius, with
Accointing showing 8 digits and Celsius showing 6-digits (rounded).


[Back](TO-ACCOINTING.md)
