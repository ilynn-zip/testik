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
        
        data = pension_flow.full_calc(pension_flow.T)
        
        write_participant(filename, data)
        
        print(id, " done")

# запись на страницу с результатом
def write_participant(filename, data):
    data = pd.DataFrame(data).T

    with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        start_row = writer.sheets['Результат'].max_row     
        data.to_excel(writer, sheet_name='Результат', startrow=start_row, index=False, header=False)


if __name__ == "__main__":
    main()