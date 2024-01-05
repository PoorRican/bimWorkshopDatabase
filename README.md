# Installation and Setup

The instructions given will be for a macOS, however, the program can be run on any system with Python 3.

## Downloading the Program

On the top-left of this page, click the green "Code" button. Select "Download ZIP". Once the ZIP file is downloaded,
open it up and move the folder to a location of your choice. This is where the program will be run from and where
the CSV files will be generated to. You can keep the folder in your Downloads folder if that's easier.

## Install Python

macOS comes with Python 2.7 pre-installed. However, this program requires Python 3.
Python 3.12 can be installed from the [Python website](https://www.python.org/ftp/python/3.12.1/python-3.12.1-macos11.pkg)

Open up the downloaded file, and follow the instructions to install Python 3.

## Installing the Required Packages

This program requires a few extra Python packages to run. A setup file has been provided.

Open up the program folder, and right click "setup.py". Select "Open With" and choose "Python Launcher (3.12)".

You will see a terminal window open up and begin to install the necessary packages. Once the terminal window says something
like "Successfully installed", you can close the terminal window.

## Getting a ChatGPT API Key

This program uses the ChatGPT API to generate the parameters. You will need to get an API key from the
[ChatGPT website](https://platform.openai.com/api-keys). Once you log in, click "Create new secret key" and give it a name.
Be sure to copy the key and save it somewhere safe. You will need it to run the program and will not be able to view it
again.

Create a file named ".env" in the same folder as the program. Open the file in a text editor, type `OPENAI_API_KEY=` and paste the API key.

The file should look like this:
```
OPENAI_API_KEY=sk-...(your rest of API key here)
```

You will need to set up a payment method. This can be done on the [OpenAI billing page](https://platform.openai.com/billing).
This service is different from normal ChatGPT or ChatGPT Plus.

# Operation

This program reads a file named "remaining.csv" and generates the CSV files for each omniclass. You can export this file
from the Numbers, Excel, or Google Sheets file. Move the file to the same folder as the program.

The "remaining.csv" must contain two columns, with no header row:
- the first column should have the omniclass classification code
- the second column should have the omniclass name

Each CSV file generated is guaranteed to be 20 parameters, each with 20 values. The generated CSV files will be appropriately
named and can be located in the "data" folder. If you run the program again with the same "remaining.csv" file, the program
will overwrite the existing CSV files. So it might be a best practice to move the generated CSV files out of the "data" folder
when you're satisfied with the results.

## Actually Running the Program

Once Python is installed, the required packages are installed, and the OpenAI API key set up, you can run the program.

Open up the program folder, and right click "main.py". Select "Open With" and choose "Python Launcher (3.12)".
A terminal window will open up and begin to run the program. It will print how many omniclass files have been read
from the "remaining.csv" file.

There will be some feedback generated in the terminal window, such as "Did not get 20 parameters for omniclass..." or
"Did not get 20 values for parameter...". This is normal, and is just the program letting you know that ChatGPT
generate a full 20 parameters for that omniclass. The program will continue to retry until ChatGPT generates proper data.

The average runtime for the program is about 1 minute per omniclass.

Once the terminal window says "Done!", you can close the terminal window.

Be sure to move the generated CSV files from the "data" folder, and delete the "remaining.csv" file. Running the program
is costly in terms of API calls, so it is best to run the program once and not to run the same list of omniclasses again
unless you have to.

# Editing Prompts

The prompts used to generate the parameters are "PARAMETER_PROMPT.txt" and "VALUE_PROMPT.txt". These files are located
in the top-level. You can edit these files to change the prompts used to generate the parameters.

The parameter prompt *needs* to have the `{omniclass}` placeholder in it. This is where the product/omniclass name will
be inserted.

Likewise, the value prompt *needs* to have the `{ordinal}` placeholder in it. This is where the ordinal number (ie:
"first", "2nd"...) will be inserted.