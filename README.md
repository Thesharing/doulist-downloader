# DouList Downloader

Download and archive all the photos in the DouList using selenium and requests.

## Install and Run

```bash
pip install -r requirements.txt
```

Download chromedriver.exe from https://chromedriver.chromium.org/downloads. The version of chromedriver.exe must be corresponding to the version of Google Chrome.

Use Google Chrome to login Douban and get the cookie from Developer Tools (F12).

Save the cookie to cookie.txt.

Change the doulist id in `spider.list('<Doulist ID>')`.

Run `main.py`.

## Todo

* Add comments and documents.
* Simplify the logic