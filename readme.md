Obituary Scraper with Tkinter GUI

A Python script that reads an RSS feed (XML) of obituaries, scrapes each obituary’s webpage for specific content, and injects the scraped content back into the RSS feed under <description>. A Tkinter GUI is provided so users can:

    Select the input and output RSS file paths
    Adjust the delay between requests
    Modify the User-Agent header
    Start the scraping process with a single click

If a “Are you human?” challenge (or other CAPTCHA text) is detected, the script immediately stops scraping further items.
Features

    RSS Parsing/Updating: Uses xml.etree.ElementTree to read and write RSS (XML) files.
    Web Scraping: Uses the requests and BeautifulSoup libraries to fetch and parse obituary pages.
    Anti-bot Detection: Checks for the phrase “are you human” in the HTML to detect a CAPTCHA scenario.
    GUI with Tkinter: Provides a simple form to set all necessary parameters and run the script without needing the command line.

Requirements

    Python 3.x
    requests
    beautifulsoup4
    Tkinter (usually pre-installed with most Python distributions on Windows, Linux, and macOS)

Installation

    Clone or download this repository:

git clone https://github.com/YourUsername/ObituaryScraper.git
cd ObituaryScraper

Create and activate a virtual environment (optional, but recommended):

python -m venv venv
source venv/bin/activate  # On Linux/Mac
.\venv\Scripts\activate   # On Windows

Install dependencies:

pip install -r requirements.txt

Make sure your requirements.txt file contains:

requests
beautifulsoup4

Run the script:

    python obituary_scraper.py

    This will start the Tkinter GUI.

Usage
GUI Controls

    Input RSS File
        Click Browse... to select your existing RSS (XML) file containing obituary <item> entries.
        Example: original_feed.xml

    Output RSS File
        Click Browse... (or type a filename) for where you want the updated RSS feed to be saved.
        Example: updated_feed.xml

    Delay (seconds)
        Enter how many seconds the script should wait between each item’s scraping. Default is 3.

    User-Agent
        A custom User-Agent string for the requests library to mimic a normal browser.
        The default is a reasonably modern Chrome-like string.

    Start Scraping
        Click the “Start Scraping” button to begin.
        The script will:
            Parse the input RSS.
            For each <item>, read its <link>.
            Fetch and parse the obituary page.
            Extract relevant HTML from elements with data-blog-component.
            Insert the extracted HTML into the <description> tag of that <item>.
            Write out the new RSS feed to the output file.

“Are you human?” Detection

    If the HTML for any obituary page contains the phrase “are you human”, the script interprets this as a CAPTCHA or challenge and stops immediately.
    The items processed before this detection are still saved to the output RSS file.

Logging and Debug Messages

    By default, [INFO] and [DEBUG] messages appear in your terminal or command prompt.
    Errors like missing <link> elements, request failures, or a missing <channel> element in the RSS will also be printed to the console.

Script Overview

Here’s a simplified description of the main components:

    fetch_obit_content(url, user_agent)
        Makes an HTTP GET request to url with a custom User-Agent.
        If a request error occurs, returns an empty string.
        Checks if “are you human” appears in the first 500 characters (case-insensitive); if yes, returns None.
        Otherwise, uses BeautifulSoup to parse <div data-blog-component="..."> elements and extracts relevant content (subtitles, images, text blocks).
        Returns combined HTML as a string (or None if the CAPTCHA is detected).

    scrape_rss_feed(input_file, output_file, delay, user_agent)
        Loads input_file via xml.etree.ElementTree.
        Iterates through each <item>, finds its <link>, and calls fetch_obit_content(...).
        If fetch_obit_content returns None, halts further processing.
        Otherwise, updates <description> for each <item> with a <![CDATA[ ... ]]> block containing the extracted HTML.
        Waits delay seconds between each item.
        Saves the updated feed to output_file.

    Tkinter GUI
        File Choosers for input and output XML files.
        Entries for delay and User-Agent.
        Start Scraping button to invoke scrape_rss_feed with the user-provided parameters.

Known Limitations / Future Improvements

    Threading: Currently, scraping runs on the main thread. If you have many items, the GUI may appear unresponsive until the task is done. For large feeds, you can integrate threading or multiprocessing so the UI remains responsive.
    CAPTCHA Solutions: The script only stops if a CAPTCHA is detected. To truly bypass a CAPTCHA, you would need more complex logic or third-party services.
    Content Extraction: Tailored to a specific structure (data-blog-component). You may need to adjust the scraping logic in fetch_obit_content if obituary pages change their HTML structure.

Contributing

    Fork this repository and clone your fork.
    Create a new branch (git checkout -b feature/my-feature).
    Make your changes and commit (git commit -am 'Add some feature').
    Push your branch to GitHub (git push origin feature/my-feature).
    Create a new Pull Request from your fork’s branch.

All contributions to improve usability, add new features, or handle edge cases are welcome!
