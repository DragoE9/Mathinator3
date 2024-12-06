# Mathinator3
Raid math made easier then its ever been
## Usage
The program should be launched by running `app.py`. Utilities contains backend code and is not intended to be run directly, outside of bugtesting and development.
## Requirements
This program uses two non-standard libraries, both of which can be installed via pip
- tzlocal - Making sure the datetimes have the correct timezone
- pandas - For handling of .csv files, and various other data processing functions

These can also be found in `requirements.txt`
## Why 3?
This is the 3rd generation of a project to create a raid math calculator. It was originally known as UnderTheInfluence, and then became RealInfluence once it started actually working. Mathinator3 is a rebuilt from scratch, refactored application designed to be production ready. Using the latest and greatest of the new API shards, and doing away with wrapper libraries entirely.
## A Note About CSVs
The outputs of this program are .csv files. CSVs are both more efficient and lightweight then .xlsx files, but are also easier to handle with code. Any spreadsheet program of your choice (Excel, Google Sheets, Ect) will be able to open the CSVs as spreadsheets. From there, you can save a copy as any format you want using `Save As`.
## Banlist Options
The program provides 3 options for proceduarlly generating an ordered banlist.
- By Influence: The default behavhiour. Sorts nations based on their influence in the region. Lowest to Highest.
- WA Focus: Will sort out all of the WA member nations and put them at the top of the list. Nations are still sorted by ascending influence.
- Efficiency Weighted: An experimental algorithm which attempts to find the most "bang for your buck" bans. Not battle tested yet. May be tweaked in future versions.
## Disclaimers
This program is provided as-is with no guarantees of legality. This program has not passed any form of code review. It is the responsibility of every user to understand and insure the scripts they run are legal. You assume all risks.

This program is feature complete, but has not been extensivley bug-tested. Errors, crashes, and unexpected behavhiour, especially with edge cases may happen. Bug reports are accepted via github issues.