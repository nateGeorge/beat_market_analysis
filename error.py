downloading update for barchart.com
Message: Unable to locate element: [name="email"]

  File "/home/nate/github/beat_market_analysis/code/scrape_data.py", line 460, in dai$y_updater
    dl_source(source)
  File "/home/nate/github/beat_market_analysis/code/scrape_data.py", line 436, in dl_$
ource
    sign_in(driver, source=source)
  File "/home/nate/github/beat_market_analysis/code/scrape_data.py", line 137, in sig$
_in
    sign_in_barchart_com(driver)
  File "/home/nate/github/beat_market_analysis/code/scrape_data.py", line 184, in sig$
_in_barchart_com
    driver.find_element_by_name('email').send_keys(email)
  File "/usr/local/lib/python3.6/dist-packages/selenium/webdriver/remote/webdriver.py$
, line 487, in find_element_by_name
    return self.find_element(by=By.NAME, value=name)
  File "/usr/local/lib/python3.6/dist-packages/selenium/webdriver/remote/webdriver.py$
, line 955, in find_element
    'value': value})['value']
  File "/usr/local/lib/python3.6/dist-packages/selenium/webdriver/remote/webdriver.py$
, line 312, in execute
    self.error_handler.check_response(response)
  File "/usr/local/lib/python3.6/dist-packages/selenium/webdriver/remote/errorhandler$
py", line 242, in check_response
    raise exception_class(message, screen, stacktrace)
None
found profile at /home/nate/.mozilla/firefox/i12g875t.investing.com
downloading update for barchart.com
data not up to date for barchart.com; downloading
