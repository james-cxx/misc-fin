# Binance.US #

Binance.US token balances seems correct.  But only 215 transactions show up. (Enabling showing of ignored transactions did not show any additional transactions.)  There should be 273.   51 transactions with "No purchase history" errors, which is likely a side-effect of the missing transactions.  8 transactions were unclassified which were due to transfers to wallets not yet added into Accounting.  Total transactions with issues: 52.  Accointing documentation does state that Binance API has unsupported features such that some types of transactions must be entered manually or imported via CSV.  However, only one transaction of mine met this criteria as far as I can tell:

Unsupported Features:
Spot Trades: Conversions
Commissions from referral program

Import from converted CSV:  372 transactions (same count upon enabling showing of ignored transactions).

After matching up internal transfers...  


8 Unclassified transactions due to a Solana wallet not yet added to Accointing (partly because Accounting does not appear to support Solana!).


Another 8 transactions appear to be missing funds.  Since the final token balances appear to be correct, this may simply be due to deposits timestamps being somewhat delayed.
Binance.US makes ACH deposited funds available immediately, but the actual deposit may take more time.



END
