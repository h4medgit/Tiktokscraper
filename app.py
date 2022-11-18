from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


from urllib.parse import quote
from bs4 import BeautifulSoup

import time

from csv import DictWriter
import re



SHOW_MORE_BUTTON = "//*[@data-e2e='search-load-more']"



class TikTok:
    def __init__(self, excel_file='result.csv') -> None:
        self.excel_file = excel_file
        
        with open(excel_file, 'w') as file:
            pass 


        profile_path = 'C:\\Users\\PASARGAD\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1'
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-data-dir={profile_path}')
        options.add_argument('--profile-directory=Default')
        options.add_argument('--user-data-dir=C:/Temp/ChromeProfile')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        agent = self.driver.execute_script("return navigator.userAgent")
        print(f'agent : {agent}')

    def search(self, term, number):
        term = quote(term)
        url = f'https://www.tiktok.com/search/user?q={term}'
        
        self.driver.get(url)
        element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/div[1]'))
        )
        time.sleep(5)

        count = 0
        while count*10 <= number:
            source = self.driver.page_source
            users = self.extract_users(source)

            self.write(users[count*10:(count+1)*10])
            count +=1

            self.scroll()
            self.load_more()
            time.sleep(5)
        

        print(f'found {count * 10} users')
        

    def scroll(self):
        print('scrolling')
        element = self.driver.find_element(By.XPATH, SHOW_MORE_BUTTON)

        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()



    def load_more(self):
        print('clicking for more users ...')
        self.driver.find_element(By.XPATH, SHOW_MORE_BUTTON).click()



    def extract_users(self, source):
        soup = BeautifulSoup(source, 'html.parser')

        containers = soup.find('div', class_ = 'ea3pfar2').find_all('div', attrs={'data-e2e': 'search-user-container'})

        print(f'found {len(containers)} users')
        
        result = []

        for user in containers:
            try:
                followers = re.findall('<span>(.*)</span>', str(user))[0]
                username = user.a['href'].split('/')[1]
            
                result.append({'username': username, 'followers': followers, 'url': f'tiktok.com/{username}'})

            except Exception as e:
                print(f'failed fetching user info > {e}')
            

        return result


    def write(self, data: dict):
        fieldnames = ['username', 'followers', 'url']
        with open(self.excel_file, 'a', newline='') as csv_file:
            dw = DictWriter(csv_file, fieldnames=fieldnames)
            dw.writerows(data)





if __name__ == '__main__':
    try:
        tiktok = TikTok()
        tiktok.search('#nft', 1000)
    
    except KeyboardInterrupt:
        print('[!] keyboard interrupt error')