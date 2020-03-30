import math
import decimal


class malgo:

    def __init__(self, lot, type, base, volume, exchange_rate,
                 new_exchange_rate, leverage, balance):
        self.lot = lot
        self.type = type
        self.base = base
        self.volume = volume
        self.exchange_rate = exchange_rate
        self.new_exchange_rate = new_exchange_rate
        self.leverage = leverage
        self.balance = balance
        if self.lot == "std":
            self.one_lot = 100000

        elif self.lot == "micro":
            self.one_lot = 1000

    def get_profit(self):
        # type buy or sell
        # one lot == 100000 currency
        rate_of_currency_change = self.exchange_rate/self.new_exchange_rate

        # pip is equivalent to a single value on the last\
        #  decimal place 0.001 or 0.0001
        # get the decimal place by getting the exchange_rate exponent
        get_exponent = decimal.Decimal(f'{self.exchange_rate}').as_tuple()
        if get_exponent[2] < -4:
            one_pip = math.pow(10, get_exponent[2]+1)

            # divide the pip value by the exchange rate
            # to get the price per pip
            pip_change_value = one_pip/self.exchange_rate

            # multiply pip value by the lot size to get the total pip price
            lot_size = self.volume * self.one_lot
            price_per_pip_change = pip_change_value * lot_size

            if self.type == "sell":
                # get the market movement in pip values
                exchange_rate_difference = self.exchange_rate\
                     - self.new_exchange_rate

                # multiply price_per_pip_change by pip
                # movement to get the value in currency
                get_currency = exchange_rate_difference\
                    * price_per_pip_change

                bare_currency = get_currency * pow(10, abs(get_exponent[2]+1))\
                    * rate_of_currency_change

            elif self.type == "buy":
                # get the market movement in pip values
                exchange_rate_difference = self.new_exchange_rate\
                     - self.exchange_rate

                # multiply price_per_pip_change
                # # by pip movement to get the value in currency
                get_currency = exchange_rate_difference * price_per_pip_change

                bare_currency = get_currency * pow(10, abs(get_exponent[2]+1))\
                    * rate_of_currency_change

            if self.base != "usd":
                # closing the position means selling
                # and getting back the base currency
                profit = bare_currency * self.new_exchange_rate
            else:
                profit = bare_currency

        else:
            one_pip = math.pow(10, get_exponent[2])
            # divide the pip value by the exchange
            # rate to get the price per pip
            pip_change_value = one_pip/self.exchange_rate

            # multiply pip value by the lot size to get the total pip price
            lot_size = self.volume * self.one_lot
            price_per_pip_change = pip_change_value * lot_size

            if self.type == "sell":
                # get the market movement in pip values
                exchange_rate_difference = self.exchange_rate\
                     - self.new_exchange_rate

                # multiply price_per_pip_change by pip movement
                # to get the value in currency
                get_currency = exchange_rate_difference * price_per_pip_change
                bare_currency = get_currency * pow(10, abs(get_exponent[2]))\
                    * rate_of_currency_change
            elif self.type == "buy":
                # get the market movement in pip values
                exchange_rate_difference = self.new_exchange_rate\
                     - self.exchange_rate

                # multiply price_per_pip_change by pip movement
                # to get the value in currency
                get_currency = exchange_rate_difference * price_per_pip_change
                bare_currency = get_currency * pow(10, abs(get_exponent[2]))\
                    * rate_of_currency_change

            if self.base != "usd":
                # closing the position means selling and
                # getting back the base currency
                profit = bare_currency * self.new_exchange_rate

            else:
                profit = bare_currency
        print(f'profit {round(profit,2)}')

        return profit

    def get_margin(self):
        lot_size = self.one_lot * self.volume
        margin = lot_size/self.leverage
        profit = self.get_profit()
        equity = self.balance + profit
        free_margin = equity - margin
        margin_level = equity/margin * 100

        print(f'margin {margin}')
        print(f'profit {round(profit,2)}')
        print(f'equity {round(equity,2)}')
        print(f'free margin {round(free_margin,2)}')
        print(f'margin level {round(margin_level,2)}%')

    # def set_target(self):

cargo = malgo("std", "sell", "usd", 0.12, 108.034, 107.022, 500, 50)

cargo.get_margin()
