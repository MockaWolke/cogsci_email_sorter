# COGSCI EMail Sorter
## Tame your Inbox with IMAP and Scikit-learn Gradient Boosting
Tired of drowning in emails about VP hours and job ads? Fear no more! This program uses IMAP (Internet Message Access Protocol) and Scikit-learn Gradient Boosting to sort incoming emails into categories like "Important", "VP Hours", and "Job Advertisements".


## Usage:
To use the program, simply run the following command in your terminal:
```
python main.py
```


The program logs in to your email account using the provided credentials and sorts the emails based on their categories. The emails labeled "Important" stay in the inbox, while "VP_Hours" and "Job_Advertisements" emails move to their respective folders.

The program uses Scikit-learn's Gradient Boosting algorithm to classify emails based on their content. The algorithm takes as input a feature vector, which is created by counting the occurrences of certain words in the email's subject and body. These words include "job", "hiwi", and any numbers that appear 10 positions before the letters "vp" in the subject.


This program remembers the last successful IMAP UID, so it only sorts emails with UIDs higher than the last successful one. This feature ensures that the program doesn't sort the same emails multiple times.

The program logs every step of the sorting process, including every classification by UID and any errors or exceptions encountered during the process. You'll find log files for every run under the "logs/" directory, with a timestamp for every file.

## Installation:
Install the required packages with:

1. pip install requirements.txt
2. Fill in your email login information in the credentials.json file. Keep this file safe and secure.
3. Create two inbox folders in your email client named ```VP_Hours``` and ```Job_Advertisements```.

## Disclaimer:
This program is provided "AS IS" without any warranty, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. The use of this program is at your own risk, and it is your responsibility to ensure that the program is used in compliance with any applicable laws and regulations.