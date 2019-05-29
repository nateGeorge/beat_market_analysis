# seemed to be taking up 100% of CPU with firefox

found profile at /home/nate/.mozilla/firefox/j2xpg2cz.investing.com
downloading update for barchart.com
Message: Browsing context has been discarded

  File "/media/nate/nates/github/beat_market_analysis/code/scrape_data.py", line 617, in daily_updater
    dl_source(source)
  File "/media/nate/nates/github/beat_market_analysis/code/scrape_data.py", line 588, in dl_source
    sign_in(driver, source=source)
  File "/media/nate/nates/github/beat_market_analysis/code/scrape_data.py", line 140, in sign_in
    sign_in_barchart_com(driver)
  File "/media/nate/nates/github/beat_market_analysis/code/scrape_data.py", line 195, in sign_in_barchart_com
    driver.find_element_by_name('email').send_keys(email)
  File "/home/nate/anaconda3/lib/python3.6/site-packages/selenium/webdriver/remote/webdriver.py", line 496, in find_element_by_name
    return self.find_element(by=By.NAME, value=name)
  File "/home/nate/anaconda3/lib/python3.6/site-packages/selenium/webdriver/remote/webdriver.py", line 978, in find_element
    'value': value})['value']
  File "/home/nate/anaconda3/lib/python3.6/site-packages/selenium/webdriver/remote/webdriver.py", line 321, in execute
    self.error_handler.check_response(response)
  File "/home/nate/anaconda3/lib/python3.6/site-packages/selenium/webdriver/remote/errorhandler.py", line 242, in check_response
    raise exception_class(message, screen, stacktrace)
None
