# Google Maps Scraper

A Python script for extracting business details from **Google Maps** using **Selenium**.
It collects information such as business name, rating, number of reviews, address, phone number, and plus code.

---

## ✨ Features

* Search for businesses by **category** and **location**
* Extract details such as:

  * Name
  * Rating
  * Reviews count
  * Address
  * Phone number
  * Plus code
* Adjustable result limit
* Human-like random delays to reduce detection
* Simple CLI interface
* Formatted table output

---

## 📦 Requirements

* Python **3.8+**
* **Google Chrome** (latest stable version recommended)
* **ChromeDriver** (matching your Chrome version)
* Python dependencies listed in [`requirements.txt`](requirements.txt)

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/Falorenthebad/google-maps-scraper.git
cd google-maps-scraper
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Make sure **Google Chrome** and the correct **ChromeDriver** are installed and available in your PATH.

---

## ▶️ Usage

Run the script:

```bash
python google_maps_scraper.py
```

You will be prompted for:

* **Category** (e.g., `Plumbers`)
* **Location** (e.g., `Seattle`)
* **Limit** (e.g., `30`)

Example:

```
Category (e.g., Hotel): Plumber
Location (e.g., Seattle): Toronto
Limit (e.g., 30): 3
```

Output:

```
# | Name                         | Rating | Reviews | Address                                              | Phone           | Plus code
--+------------------------------+--------+---------+------------------------------------------------------+-----------------+-------------------------------------
1 | Plumbing Market              | 4.8    | 72      | 131 Whitmore Rd Unit 11. Vaughan. ON L4L 6E2. Canada | +1 289-236-2378 | QCPV+7W Vaughan. Ontario. Canada
2 | Canuck Door Systems Co.      | 4.7    | 109     | 1645 Bonhill Rd #14. Mississauga. ON L5T 1R3. Canada | +1 289-217-0415 | M88W+JW Mississauga. Ontario. Canada
3 | Royal Plumbing Services Ltd. | 4.9    | 749     | 614 Dufferin St. Toronto. ON M6K 2A9. Canada         | +1 416-537-0038 | JHX9+MC Toronto. Ontario. Canada
...
```