downloading update for barchart.com
---------------------------------------------------------------------------
WebDriverException                        Traceback (most recent call last)
~/github/beat_market_analysis/code/scrape_data.py in daily_updater(driver)
    457                     elif not up_to_date and today_ny.hour >= 20:
--> 458                         dl_source(source)
    459

~/github/beat_market_analysis/code/scrape_data.py in dl_source(source)
    433         print('downloading update for ' + source)
--> 434         sign_in(driver, source=source)
    435         download_sp600_data(driver, source=source)

~/github/beat_market_analysis/code/scrape_data.py in sign_in(driver, source)
    127     elif source == 'barchart.com':
--> 128         sign_in_barchart_com(driver)
    129

~/github/beat_market_analysis/code/scrape_data.py in sign_in_barchart_com(driver)
    166 def sign_in_barchart_com(driver):
--> 167     driver.get('https://www.barchart.com/login')
    168     email = os.environ.get('barchart_username')

/usr/local/lib/python3.6/dist-packages/selenium/webdriver/remote/webdriver.py in get(self, url)
    323         """
--> 324         self.execute(Command.GET, {'url': url})
    325

/usr/local/lib/python3.6/dist-packages/selenium/webdriver/remote/webdriver.py in execute(self, driver_co$
mand, params)
    311         if response:
--> 312             self.error_handler.check_response(response)
    313             response['value'] = self._unwrap_value(

/usr/local/lib/python3.6/dist-packages/selenium/webdriver/remote/errorhandler.py in check_response(self,
response)
    241             raise exception_class(message, screen, stacktrace, alert_text)
--> 242         raise exception_class(message, screen, stacktrace)
    243

WebDriverException: Message: Failed to decode response from marionette

During handling of the above exception, another exception occurred:

SessionNotCreatedException                Traceback (most recent call last)
~/github/beat_market_analysis/code/scrape_data.py in <module>()
    476 if __name__ == '__main__':
    477     driver = setup_driver()
--> 478     daily_updater(driver)
    479
    480

~/github/beat_market_analysis/code/scrape_data.py in daily_updater(driver)
    470             time.sleep(3600)
    471         except:
--> 472             driver.quit()
    473             driver = setup_driver()
    474

/usr/local/lib/python3.6/dist-packages/selenium/webdriver/firefox/webdriver.py in quit(self)
    189         """Quits the driver and close every associated window."""
    190         try:
--> 191             RemoteWebDriver.quit(self)
    192         except (http_client.BadStatusLine, socket.error):
    193             # Happens if Firefox shutsdown before we've read the response from

/usr/local/lib/python3.6/dist-packages/selenium/webdriver/remote/webdriver.py in quit(self)
    687         """
    688         try:
--> 689             self.execute(Command.QUIT)
    690         finally:
    691             self.stop_client()

/usr/local/lib/python3.6/dist-packages/selenium/webdriver/remote/webdriver.py in execute(self, driver_com
mand, params)
    310         response = self.command_executor.execute(driver_command, params)
    311         if response:
--> 312             self.error_handler.check_response(response)
    313             response['value'] = self._unwrap_value(
    314                 response.get('value', None))

/usr/local/lib/python3.6/dist-packages/selenium/webdriver/remote/errorhandler.py in check_response(self,
response)
    240                 alert_text = value['alert'].get('text')
    241             raise exception_class(message, screen, stacktrace, alert_text)
--> 242         raise exception_class(message, screen, stacktrace)
    243
    244     def _value_or_default(self, obj, key, default):

SessionNotCreatedException: Message: Tried to run command without establishing a connection
