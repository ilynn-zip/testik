from enum import Enum
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Stage(Enum):
    UNDEF = 0        # непонятное
    ACCUMULATION = 1 # накопление
    PAY = 2          # выплата
    

class PensionFlow():
    def __init__(self, id, participant, calc_parameters) -> None:
        self.id = id

        self.birth = participant["Дата рождения участника"]
        self.pens_age = participant["Пенсионный возраст"]

        self.pension_amount = participant["Установленный размер пенсии"]

        self.T = calc_parameters.loc["Отчетная дата", 1]
        self.gpr = calc_parameters.loc["Ставка индексации пенсии", 1]
        self.max_age = calc_parameters.loc["Максимальный возраст, лет", 1]

        self.stage = self.__set_stage(datetime.now())
        self.end_date = self.__calc_end_date()


    # форматирование даты
    @staticmethod
    def format_date(format):
        def decorator(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if isinstance(result, datetime):
                    return result.strftime(format)
                return result
            return wrapper
        return decorator


    @format_date("%d.%m.%Y")
    def pension_date(self, m, month=1):
        return self.__calc_T_date(min(self.__retire_date() + relativedelta(months=m * month), self.end_date))

    @format_date("%d.%m.%Y")
    def dor(self):
        if self.stage == Stage.ACCUMULATION:
            return self.__retire_date()
        elif self.stage == Stage.PAY:
            return self.__calc_T_date(self.__retire_date())
        
        return None

    # m - месяц-счётчик, т.е. сколько месяцев уже выплачивается пенсия
    # т.е. равен m в pension_date (мне надо было уточнить, как именно m задётся) 
    def pension_value(self, m):
        pens_value = self.pension_amount # в тз написано, что в таблице задана первая вылата

        if self.stage == Stage.PAY:
            for i in range(m):
                # индексация в январе от начала даты выхода на пенсию
                if (datetime.strptime(self.dor(), "%d.%m.%Y") + relativedelta(months=i)).month == 1: 
                    pens_value *= (1 + self.gpr)

        # посчитал, что если пенсия в рублях, то после запятой - копейки => .2f
        # (но, по хорошему, мне это надо было уточнить)
        return "{:.2f}".format(pens_value)
    
    # не понял откуда m, поэтому вычисляем на основе текущей даты (или заданной)
    # и отчётной даты от наступления пенсионнного возраста
    def calc_m(self, date_start, date_end):
        self.stage = self.__set_stage(date_end)
        diff = relativedelta(date_end, date_start)
        month = diff.years * 12 + diff.months
        return month if month > 0 else 0

    # причина, по которой следующие методы приватные,
    # они выступают как вспомогательные для тех что есть в тз
    # для определения каких-либо величин 
    # *кроме calc_m

    # устанавливает этап накопления/выплаты пенсии по возрасту
    def __set_stage(self, date):
        age = relativedelta(date, self.birth).years
        if age < self.pens_age and age > 0:
            return Stage.ACCUMULATION
        elif age >= self.pens_age and age <= self.max_age:
            return Stage.PAY
        
        return Stage.UNDEF
    
    # дата выхода на пенсию
    def __retire_date(self):
        return self.birth + relativedelta(years=self.pens_age)
    
    # дата окончания договора (или достижения максимального возраста) - последняя дата выплат 
    def __calc_end_date(self):
        date = self.birth + relativedelta(years=self.max_age)
        if date.day < self.T.day:
            date = self.__calc_T_date(date) - relativedelta(months=1)
        else:
            date = self.__calc_T_date(date)
        
        return date 
    
    # переводит дату к отчётной дате месяца
    def __calc_T_date(self, date):
        try:
            new_date = date.replace(day=self.T.day)
        except ValueError:
            first_day_next_month = date + relativedelta(months=1, day=1)
            last_day_of_month = first_day_next_month - relativedelta(days=1)
            new_date = last_day_of_month

        return new_date