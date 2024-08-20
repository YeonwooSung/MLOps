from enum import Enum
from pytz import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class DateFormat(Enum):
    yyyyMMddHHmmss = "%Y%m%d%H%M%S"
    yyyyMMdd = "%Y%m%d"
    yyyyMM = "%Y%m"
    formattedYyyyMMddHHmmss = "%Y-%m-%d %H:%M:%S"


class DateValues:

    @staticmethod
    def get_current_date():
        """
        Return current date

        :returns: current date
        :rtype: str
        """
        return datetime.now(timezone('Asia/Seoul')).strftime(DateFormat.yyyyMMdd.value)

    @staticmethod
    def get_before_60_days():
        """
        Return yesterday's date

        :returns: date of yesterday
        :rtype: str
        """
        return (datetime.now(timezone('Asia/Seoul')) - relativedelta(days=1)).strftime(DateFormat.yyyyMMdd.value)

    @staticmethod
    def get_before_one_day():
        """
        Return yesterday's date

        :returns: date of yesterday
        :rtype: str
        """
        return (datetime.now(timezone('Asia/Seoul')) - relativedelta(days=1)).strftime(DateFormat.yyyyMMdd.value)

    @staticmethod
    def get_before_one_month(base_day: str = None):
        """
        Return Last month

        :returns: last month (format: yyyyMM)
        :rtype: str
        """
        if base_day:
            month_len = 6
            day_len = 8
            if len(base_day) not in [month_len, day_len]:
                raise ValueError("Length of base_day is not allowed.")
            return (datetime.strptime((base_day[:6] + "01"), DateFormat.yyyyMMdd.value) - relativedelta(
                months=1)).strftime(DateFormat.yyyyMM.value)
        return (datetime.now(timezone('Asia/Seoul')) - relativedelta(months=1)).strftime(DateFormat.yyyyMM.value)

    @staticmethod
    def get_date_list(start_day, end_day):
        """
        Return date list between start day and end day

        :param str start_day: Start date of expected continuous date list
        :param str end_day: End date of expected continuous date list
        :returns: date list (e.g. ['20220401', '20220402', '20220403'])
        :rtype: List

        >>> from support.date_values import DateValues
        >>> date_value = DateValues()
        >>> result = date_value.get_date_list('20240401', '20240409')
        >>> result
        ['20240401', '20240402', '20240403', '20240404', '20240405', '20240406', '20240407', '20240408', '20240409']
        """
        datelist = []
        try:
            start_datetime = datetime.strptime(start_day, DateFormat.yyyyMMdd.value)
            end_datetime = datetime.strptime(end_day, DateFormat.yyyyMMdd.value)
            for i in range((end_datetime - start_datetime).days + 1):
                datelist.append((datetime.strptime(start_day, DateFormat.yyyyMMdd.value) + timedelta(days=i)).strftime(
                    DateFormat.yyyyMMdd.value))
            return datelist
        except ValueError:
            raise ValueError("You have entered a date in an incorrect format, "
                             "so please double-check the date you entered.\n"
                             f"The dates you entered are as follows: start_day = {start_day}, end_day = {end_day}")
