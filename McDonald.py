import re
import requests
from datetime import datetime


class McDonald(object):
    """docstring for McDonald."""

    def __init__(self, token):
        super(McDonald, self).__init__()
        self.json = {
          "access_token": token,
          "source_info": {
            "app_version": "2.2.0",
            "device_time": "2000/00/00 00:00:00",
            "device_uuid": "device_uuid",
            "model_id": "Pixel XL",
            "os_version": "7.1.1",
            "platform": "Android"
          }
        }
        self.respones = ""
        self.coupons = []
        self.stickers = 0
        self.expire_stickers = 0

    # Request to get a lottery
    def Lottery(self):
        self.respones = requests.post('https://api2.mcddailyapp.com/lottery/get_item', json = self.json)

    # Get the coupon list
    def Coupon_List(self):

        # Request to get the coupon list
        self.respones = requests.post('https://api1.mcddailyapp.com/coupon/get_list', json = self.json).text
        count = self.respones.count('coupon_id') # Count the number of coupons
        self.respones = eval(self.respones)      # Convert string to dictionary

        # Every coupons are going to be checked the status is unused and not expired
        for value in range(count):
            status = self.respones['results']['coupons'][value]['status']
            redeem_end_datetime = self.respones['results']['coupons'][value]['object_info']['redeem_end_datetime']
            redeem_end_datetime = datetime.strptime(redeem_end_datetime, '%Y/%m/%d %H:%M:%S')

            # Status code is 1 also redeem_end_datetime is not yet
            if status == 1 and redeem_end_datetime.day - datetime.now().day >= 0:
                coupon = self.Re(value)
                self.coupons.append(coupon + 'E:' + str(redeem_end_datetime.day - datetime.now().day))

        # Return coupon list
        return self.coupons

    # Get the sticker list
    def Sticker_List(self):

        # Request to get the sticker list
        self.respones = requests.post('https://api1.mcddailyapp.com/sticker/get_list', json = self.json).text
        self.stickers = self.respones.count('歡樂貼') # Count the number of stickers
        self.respones = eval(self.respones)          # Convert string to dictionary

        # Every stickers are going to be checked is expired
        for value in range(self.stickers):
            expire_datetime = self.respones['results']['stickers'][value]['object_info']['expire_datetime']
            expire_datetime = datetime.strptime(expire_datetime, '%Y/%m/%d %H:%M:%S')
            if expire_datetime.month == datetime.now().month:
                self.expire_stickers += 1

        # Return stickers and expire_stickers
        return self.stickers, self.expire_stickers

    # Request to get a sticker lottery
    def Sticker_lottery(self):
        self.Sticker_List() # Get the stickers imformation
        sticker_ids = []    # Sticker ids list

        # Print the results of stickers imformation
        print('----- Sticker Imformation -----')
        print('Total : %d , Expire stickers : %d\n\n' % (self.stickers, self.expire_stickers))

        # If sticker number less than 6 , exit
        if self.stickers < 6:
            print('The stickers are not enough , just only %d !\n' % (self.stickers))

        # Make sure the user want to get a lottery
        else:
            bool = input('Make sure you want to get a lottery ? (y/n) ')

            # If bool is yes , get a lottery
            if bool == 'y' or bool == 'yes':

                # Get the 6 sticker ids
                for value in range(6):
                    sticker_ids.append(self.respones['results']['stickers'][value]['sticker_id'])

                # Update the json dictionary
                self.json['sticker_ids'] = sticker_ids

                # Get a sticker lottery
                self.respones = requests.post('https://api1.mcddailyapp.com/sticker/redeem', json = self.json).text

                # Print the results of coupon imformation
                coupon = self.Re()
                print('You win a coupon !\n')
                print(coupon)

    # Clear some characters are matched by Regular Expression
    def Re(self, value = 0):
        coupon = self.respones['results']['coupons'][value]['object_info']['title']
        coupon = re.sub(r'鷄', '雞', coupon)
        coupon = re.sub(r'\(G.*\)|_.*|\(新.*', '', coupon)
        return coupon