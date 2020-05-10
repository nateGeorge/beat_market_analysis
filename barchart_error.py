data not up to date for barchart.com; downloading
waiting for.../home/nate/Dropbox/data/sp600/sp-600-index-08-01-2019.csv
waiting for.../home/nate/Dropbox/data/sp600/sp-600-index-08-01-2019.csv
download failed
Message: Element <a class="toolbar-button download"> is not clickable at point (1207,861) because another element <iframe id="frm"> obscures it

  File "/media/nate/nates/github/beat_market_analysis/code/scrape_data.py", line 642, in daily_updater
    dl_source(source)
  File "/media/nate/nates/github/beat_market_analysis/code/scrape_data.py", line 611, in dl_source
    download_sp600_data(driver, source=source)
  File "/media/nate/nates/github/beat_market_analysis/code/scrape_data.py", line 289, in download_sp600_data
    download_barchart_com(driver)
  File "/media/nate/nates/github/beat_market_analysis/code/scrape_data.py", line 385, in download_barchart_com
    driver.find_element_by_class_name('toolbar-button.download').click()
  File "/home/nate/anaconda3/lib/python3.6/site-packages/selenium/webdriver/remote/webelement.py", line 80, in click
    self._execute(Command.CLICK_ELEMENT)
  File "/home/nate/anaconda3/lib/python3.6/site-packages/selenium/webdriver/remote/webelement.py", line 633, in _execute
    return self._parent.execute(command, params)
  File "/home/nate/anaconda3/lib/python3.6/site-packages/selenium/webdriver/remote/webdriver.py", line 321, in execute
    self.error_handler.check_response(response)
  File "/home/nate/anaconda3/lib/python3.6/site-packages/selenium/webdriver/remote/errorhandler.py", line 242, in check_response
    raise exception_class(message, screen, stacktrace)
None
