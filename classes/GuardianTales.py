import requests, json
from bs4 import BeautifulSoup

class GuardianTales:
    def __init__(self, user_id, region = 'EU'):
        self.user_id = user_id
        self.region = region
        self.url = 'https://www.guardiantales.com'
        self.url_redeem = f'{self.url}/coupon/redeem'
        self.form_headers = { 
            'Content-Type' : 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36',
        }
        self.old_coupons = self.load_old()

    def redeem(self, coupon):
        if coupon not in self.old_coupons:
            data = {
                "region": self.region,
                "userId": self.user_id,
                "code": coupon
            }
            try:
                r = requests.post(
                    self.url_redeem, 
                    data=data, 
                    headers=self.form_headers,
                    timeout=60
                )
                if r.status_code == 200:
                    if f'Something unexpected has occurred' in r.text:
                        print(f'Seems the coupon {coupon}, is no longer valid')
                    else:
                        print(f'Coupon {coupon} redeemed')
                    self.store_old(coupon)
                else:
                    print(f'Error redeeming coupon {coupon}, check the html for error: {r.text}')
            except Exception as e:
                print(f'Error redeeming coupon {coupon}, error: {e}')


    def list_codes(self):
        coupons = []
        r = requests.get('https://www.pockettactics.com/guardian-tales/code')
        if r.status_code == 200:            
            soup = BeautifulSoup(r.text, features='html.parser')
            for list_coupon in soup.find_all('ul'):
                if any(x for x in ['active', 'expired'] if x in format(list_coupon.previous.previous).lower()):
                    coupons += self.parse_codes(list_coupon)
        r = requests.get('https://ucngame.com/codes/guardian-tales-coupon-codes')
        if r.status_code == 200:            
            soup = BeautifulSoup(r.text, features='html.parser')
            for list_coupon in soup.find_all('tbody')[0]:
                coupons.append(list_coupon.contents[0].text)
        list(set(coupons))
        return coupons

    @staticmethod
    def parse_codes(rows):
        return [row.text.split(' ')[0] for row in rows.contents if row != f'\n']
    
    @staticmethod
    def load_old():
        with open('old_coupons.json', 'r') as file:
            array_str = file.read()
        return json.loads(array_str)      
    
    def store_old(self, coupon):
        self.old_coupons.append(coupon)
        with open('old_coupons.json', 'w') as file:
            json.dump(self.old_coupons, file)        