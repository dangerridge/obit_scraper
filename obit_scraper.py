import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import time
import requests
from bs4 import BeautifulSoup
import os

def fetch_obit_content(url, user_agent):
    """
    Fetches obituary content from the given URL using the specified User-Agent.
    
    1. Fetch the webpage at 'url' with requests, using a custom User-Agent.
    2. If the HTML contains "are you human", return None (signal to stop).
    3. Otherwise, extract relevant obituary text/HTML from <div data-blog-component="...">.
    """
    
    headers = {
        "User-Agent": user_agent
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Fetching {url} failed: {e}")
        return ""  # Return empty if there's a network/HTTP error

    print(f"  [DEBUG] Fetched {url} with status code: {resp.status_code}")
    sample_html = resp.text[:500].lower()
    print("  [DEBUG] First 500 characters of HTML:\n", resp.text[:500], "\n-----")

    # Detect "are you human" challenge
    if "are you human" in sample_html:
        print("[ERROR] 'Are you human?' captcha detected.")
        return None  # None signals we should stop processing further

    soup = BeautifulSoup(resp.text, 'html.parser')
    content_divs = soup.find_all('div', attrs={'data-blog-component': True})
    print(f"  [DEBUG] Found {len(content_divs)} 'data-blog-component' blocks")

    combined_html = []
    for div in content_divs:
        comp_type = div.get('data-blog-component', 'unknown')
        print(f"    [DEBUG] Handling data-blog-component={comp_type}")

        if comp_type == 'subtitle':
            h3 = div.find('h3')
            if h3:
                combined_html.append(f"<h3>{h3.get_text(strip=True)}</h3>")
        elif comp_type == 'image':
            img_tag = div.find('img')
            if img_tag and img_tag.get('src'):
                image_src = img_tag['src']
                combined_html.append(f'<img src="{image_src}" alt="obit image" />')
        elif comp_type == 'text':
            text_div = div.find('div', attrs={'data-blog-inner': 'text'})
            if text_div:
                block_html = str(text_div)
                combined_html.append(block_html)

    return "\n".join(combined_html)

def scrape_rss_feed(input_file, output_file, delay, user_agent):
    """
    1. Parse RSS feed from input_file.
    2. For each <item>, read <link> to get the obituary page URL.
    3. Scrape the page for relevant data:
       - If 'Are you human?' is detected, stop immediately.
    4. Put data into <description>.
    5. Save the updated feed to output_file.
    """

    print(f"[INFO] Parsing RSS feed: {input_file}")
    
    # Simple sanity check to see if file exists
    if not os.path.exists(input_file):
        print(f"[ERROR] The file '{input_file}' does not exist.")
        return

    try:
        tree = ET.parse(input_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse the RSS feed: {e}")
        return

    channel = root.find('channel')
    if channel is None:
        print(f"[ERROR] No <channel> found in {input_file}.")
        return

    items = channel.findall('item')
    print(f"[INFO] Found {len(items)} <item> entries in {input_file}.\n")
    
    for i, item in enumerate(items, start=1):
        link_elem = item.find('link')
        if link_elem is None:
            print(f"[WARN] Item {i}/{len(items)} has no <link>, skipping...")
            continue

        url = link_elem.text.strip()
        title_elem = item.find('title')
        title_text = title_elem.text.strip() if title_elem is not None else "No Title"
        
        print(f"[INFO] Processing item {i}/{len(items)} - {title_text} | {url}")
        
        obit_html = fetch_obit_content(url, user_agent)

        # If obit_html is None, "Are you human?" was triggered
        if obit_html is None:
            print(f"[INFO] 'Are you human?' triggered on item {i} with title '{title_text}'. Stopping script.")
            break
        
        # Otherwise, store in <description>
        desc_elem = item.find('description')
        if desc_elem is None:
            desc_elem = ET.SubElement(item, 'description')
        
        desc_elem.text = f"<![CDATA[\n{obit_html}\n]]>"

        # Delay between scraping each item
        print(f"[INFO] Waiting {delay} seconds before next item...\n")
        time.sleep(delay)
    
    # Write the updated RSS feed
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"\n[INFO] Done! Updated RSS feed saved to '{output_file}'.")


# ------------------- TKINTER GUI -------------------

def browse_input_file():
    """Open a file dialog to select the input RSS file."""
    filename = filedialog.askopenfilename(
        title="Select Input RSS File",
        filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")]
    )
    if filename:
        input_file_var.set(filename)

def browse_output_file():
    """Open a file dialog to select (or name) the output RSS file."""
    filename = filedialog.asksaveasfilename(
        title="Select Output RSS File",
        defaultextension=".xml",
        filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")]
    )
    if filename:
        output_file_var.set(filename)

def start_scraping():
    """Triggered by the 'Start Scraping' button."""
    input_file = input_file_var.get().strip()
    output_file = output_file_var.get().strip()
    
    # Validate delay
    try:
        delay = float(delay_var.get())
        if delay < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Delay", "Please enter a valid non-negative number for delay.")
        return

    user_agent = user_agent_var.get().strip()
    if not user_agent:
        messagebox.showwarning("Empty User-Agent", "User-Agent is empty. You might get blocked by the website.")

    # Run the scraping in the same thread (simplest approach).
    # For large RSS feeds or long tasks, consider using threading or multiprocessing.
    scrape_rss_feed(input_file, output_file, delay, user_agent)
    messagebox.showinfo("Done", f"Scraping completed. Updated feed saved to:\n{output_file}")


if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.title("Obituary Scraper")

    # Variables for storing user input
    input_file_var = tk.StringVar(value="original_feed.xml")
    output_file_var = tk.StringVar(value="updated_feed.xml")
    delay_var = tk.StringVar(value="3")  # default 3 seconds
    user_agent_var = tk.StringVar(
        value="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/58.0.3029.110 Safari/537.3"
    )

    # Layout
    frm = tk.Frame(root, padx=10, pady=10)
    frm.pack(fill=tk.BOTH, expand=True)

    # Input file
    lbl_input = tk.Label(frm, text="Input RSS File:")
    lbl_input.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    ent_input = tk.Entry(frm, textvariable=input_file_var, width=40)
    ent_input.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
    btn_browse_input = tk.Button(frm, text="Browse...", command=browse_input_file)
    btn_browse_input.grid(row=0, column=2, padx=5, pady=5)

    # Output file
    lbl_output = tk.Label(frm, text="Output RSS File:")
    lbl_output.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    ent_output = tk.Entry(frm, textvariable=output_file_var, width=40)
    ent_output.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
    btn_browse_output = tk.Button(frm, text="Browse...", command=browse_output_file)
    btn_browse_output.grid(row=1, column=2, padx=5, pady=5)

    # Delay
    lbl_delay = tk.Label(frm, text="Delay (seconds):")
    lbl_delay.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    ent_delay = tk.Entry(frm, textvariable=delay_var, width=10)
    ent_delay.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

    # User-Agent
    lbl_user_agent = tk.Label(frm, text="User-Agent:")
    lbl_user_agent.grid(row=3, column=0, sticky=tk.NW, padx=5, pady=5)
    txt_user_agent = tk.Entry(frm, textvariable=user_agent_var, width=50)
    txt_user_agent.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)

    # Start button
    btn_start = tk.Button(frm, text="Start Scraping", command=start_scraping)
    btn_start.grid(row=4, column=0, columnspan=3, pady=10)

    root.mainloop()
