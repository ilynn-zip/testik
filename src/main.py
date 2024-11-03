import pandas as pd
from datetime import datetime
from pensionflow import PensionFlow

def main():
    filename = 'Данные.xlsx'
    try:
        df = pd.ExcelFile(filename)

        part_agreement = df.parse('Договоры участников', index_col=0)
        pens_amount = df.parse('Суммы пенсий', index_col=0)
        calc_parameters = df.parse('Параметры расчета', header=None, index_col=0)
        result = df.parse('Результат', index_col=0)
    except Exception as e:
        print(f"Ошибка: {e}")
        return

    part_combined = pd.concat([part_agreement, pens_amount], axis=1, join='inner')

    for id in part_combined.index:
        pension_flow = PensionFlow(id, part_combined.loc[id], calc_parameters)
        
        # я немного не понял не задание
        # а именно, что должно быть в результате
        # поэтому в первом случае высчитывается пенсии и дата до текущей даты
        m = pension_flow.calc_m(datetime.strptime(pension_flow.dor(), "%d.%m.%Y"), datetime.now())
        # во втором до конца договора (жизни)
        # ну и можно вычислить так на любую дату отчётного периода
        #m = pension_flow.calc_m(datetime.strptime(pension_flow.dor(), "%d.%m.%Y"), pension_flow.end_date)
        date = pension_flow.pension_date(m)
        value = pension_flow.pension_value(m)

        row = -1
        if id in result.index:
            row = result.index.to_list().index(id) + 1
        write_participant(filename, id, date, value, row)

# запись на страницу с результатом
# если участник уже имеется в таблице, то перезаписываем
def write_participant(filename, id, date, value, row=-1):
    data = pd.DataFrame([[id, date, value]])

    with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        start_row = row if row != -1 else writer.sheets['Результат'].max_row     
        data.to_excel(writer, sheet_name='Результат', startrow=start_row, index=False, header=False)


if __name__ == "__main__":
    main()