# to-accointing #

## IMPORTANT NOTES ##

**NOTE #1:** This is a one-off script created for my own purposes.  I provide it here (under the MIT license) in case it
might be of use to others but make no claims of suitability or correctness for any purpose.  As a one-off script, it
does not have the rigor, testing, or documentation of a production-level program.  **If you decide to use this script,
you assume all responsibility.**  I strongly suggest that you carefully review all output CSV files before using them.

**NOTE #2:** None of the input sources (BlockFi, Celsius, TradeStation), nor the output source (Accointing), provide
proper specifications of their respective CSV file formats, so conversions are based on my own interpretation of values
using the limited dataset of my own transactions. As such, the script may not handle the full set of possible values in
an input or output CSV file.

**NOTE #3:** I have observed the the CSV import function in Accointing will **silently skip** any transactions from an
imported CSV that it does not understand, as opposed to issuing a warning.  If the token balances after import are not
extremely close to what is shown in your exchange account, there may be an import error.  Even if the token balances
match, it's a good idea to carefully review all transactions.

**NOTE #4:** This script was built for my personal use case of US-based transactions.  If you are using any of the input
sources or Accointing from outside the US, you will very likely need to make modifications to the script's internal
and/or the external configuration files to work properly for your use case.  See the Configuration section below.

**NOTE #5:** The automatic transaction classifications done by this script are based on *my interpretation* of when the
classifications should be applied based on the Accointing documentation for [The Different Types of Crypto Transaction
Classifications](https://support.accointing.com/hc/en-us/articles/5792092522125-The-Different-Types-of-Crypto-Transaction-Classifications).

**NOTE #6:** This script is free for anyone to use.  See [the license file](LICENSE.md) for full details. However, if
this script saved you some time and you would like to say thanks, you can [buy me a coffee on
ko-fi](https://ko-fi.com/formalspec).


## Overview ##

At the time I created this script (late July, 2023), importing some CSV formats into Accointing, such as CSV files
downloaded from BlockFi and Celsius, did not yield the results I expected and required *every* transaction to be
manually adjusted. I created this script to improve the import by converting from the source CSV format to a CSV format
based on the Accounting Excel template. Note that the conversion only offers a partial solution.  Some transactions,
such as internal transfers between wallets, still require manual handling in the Accointing interface.

Additionally, since TradeStation doesn't provide a CSV export for crypto transactions, I created a conversion from two
"made-up" TradeStation CSV formats.  This is explained in more detail in the [TradeStation.md](TradeStation.md) file.

Hopefully, Accointing will eventually update their CSV import function so that this script isn't necessary.

If nothing else, this script provides working examples for things like CLI argument parsing, using **PETL** to convert
CSV formats, and using **pytz** for converting time zones.

**NOTE:**  Do not use the pre-defined "BlockFi" or "Celsius Network" Exchange wallet types when using the converted CSV
files from this script.  Instead, do the following:

1. Convert the source CSV file using this script.  (See Usage section below.)
2. In the Accointing interface, select Wallets from the left-side menu, then click the (+ Add new) button to the
   right of the Exchanges section heading (or to the right of the Wallets section heading per your preference).
3. Type "custom" into the search box.
4. Select the Custom wallet option (it should be the only option displayed in the search results).
5. Choose the "File import" option.
6. Type in a name for your custom wallet (e.g. "Celsius Custom") to indicate the source of the transactions.
7. Drop or select the CSV file that you converted using this script.
8. Choose your own preference for either "Import full history" or "From date".
9. Click the "Save" button to begin the import process.

After the import completes, one way to check for obvious problems is to check that the token balances are very close to
what you expect.  Even then, it's possible that some transactions were silently ignored by the Accounting import, so
always review the transactions carefully.


## Dependencies ##

The script requires Python3 and two additional modules:

The script requires the **PETL** module.  You will need to install it if your Python3 installation doesn't already have
it. See [the PETL docs](https://petl.readthedocs.io/en/stable/index.html) for installation instructions.

The script also requires the **pytz** module, if your Python3 installation doesn't already have it.  See [the pytz
docs](https://pythonhosted.org/pytz/#tzinfo-api) for installation instructions.


## Configuration ##

The script uses a mix of hard-coded and externalized configuration.  The hard-coded configuration appears near the top
of the `to-accointing.py` file within the section that I have labelled "DEFINITIONS".  It controls things like
recognizing CSV headers, date and time formats, default time zones, and so forth.  The script could be improved by
externalizing the hard-coded configuration so that configuration changes don't require changes to the `to-accointing.py`
file, but I simply ran out of time.

Externalized configuration files are located in the `config` subfolder.  The `classify.json` file controls the automatic
classification of transactions.  The `pairs.json` file splits trading pairs into left-side and right-side symbols.  It
is only needed for converting TradeStation CSV files.  See the [TradeStation](TradeStation.md) notes for more details.


## Input Formats ##

This script currently supports the sources listed below.  See the respective documentation files for important
information:

* [Binance.US](BinanceUS.md)
* [BlockFi](BlockFi.md)
* [Celsius](Celsius.md)
* [Coinbase](Coinbase.md) **NOTE:** Support for Coinbase is experimental!
* [TradeStation](TradeStation.md)


## Usage ##

Use `-i` or `--input` to specify one or more input CSV files to be converted.  This is the only required argument.  You
can specify multiple input files, but they must all be from the same source.

Use `-o` or `--output` to (optionally) specify the output file.  If no output file is specified, the table will be
written to stdout.

Use `-r` or `--region` to (optionally) specify which region within `classify.json` is used for classifications.  The
default is "us".

Use `-t` or `--timezone` to (optionally) override the assumed timezone for transaction times.  The timezone must match a
timezone recognized by the **pytz** module (e.g., "US/Eastern") or "UTC".  When not specified, the script will use
internal defaults depending on the detected source of the CSV header.

**NOTE:** Accounting's CSV import seems to expect that all time values are expressed as UTC times.  As a result, the
timezone of the transactions times within a CSV file must be known so that the time values can be converted to UTC in
the output file.


### Examples ###

Example with one input file and the output file (most typical use):

    python3 to-accointing.py \
      -i /path/to/input_file.csv \
      -o /path/to/output_file.csv

Multiple inputs may be specified to be combined into the output file.  All inputs must be from the same source (meaning
all inputs from BlockFi or all inputs from Celsius, etc.).  At this time, the script *does not* de-duplicate or sort the
transactions from input files in any way, so if you are using multiple inputs, be sure they do not contain duplicate
transactions.

    python3 to-accointing.py \
      -i /path/to/input_file1.csv \
      -i /path/to/input_file2.csv \
      -i /path/to/input_file3.csv \
      -o /path/to/output_file.csv


Example with one input file and no output file.  Output will be written to stdout.  This is a good way to quickly test a conversion:

    python3 to-accointing.py -i /path/to/input_file.csv

Output to stdout can be piped to other programs or directly to a file, e.g.:

    python3 to-accointing.py -i /path/to/input_file.csv > /path/to/output_file.csv

Example showing use of all arguments:

    python3 to-accointing.py \
      -r "us" \
      -t "US/Eastern" \
      -i /path/to/input_file.csv \
      -o /path/to/output_file.csv


## Bugs and Contributions ##

This is script is provided "as is" with no support.  That said, bug reports, feature ideas, and pull requests are
welcome, but I make guarantee that I will address any of these.  (Although I might be influenced by ko-fi tips!)


## Final Note ##

This script is free for anyone to use.  See [LICENSE.md](LICENSE.md) for full details.  If this script saved you some
time and you would like to say thanks, you can use my [tips page on ko-fi](https://ko-fi.com/formalspec).


END
