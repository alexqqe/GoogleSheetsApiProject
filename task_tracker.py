from authentication import authenticate_and_save_token
from authentication_receiving_token import write_to_sheet, read_from_sheet, authenticate_and_get_service, read_row_from_sheet
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pprint import pprint

def authenticate(creds_file):
    authenticate_and_save_token()
def number_to_letter(number):
    if 1 <= number <= 26:
        letter = chr(number + 64)
        return letter
    else:
        return "Ошибка: число должно быть в диапазоне от 1 до 26."
spreadsheet_id1 = ''
RANGE_NAME = 'A1:B1'

class GoogleSheetsAPI:
    def __init__(self, spreadsheet_id, range_name, creds_file):
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name
        self.creds = creds_file

    service = authenticate_and_get_service()
    def append_row(self, row):
        try:
            i = 1
            while read_row_from_sheet(self.spreadsheet_id, f'A{i}') != '':
                i+=1
            write_to_sheet([row], f'A{i}:D{i}', self.spreadsheet_id)
        except Exception as e:
            print(f'Error: {e}')

    def get_all_tasks(self):
        try:
            data = read_from_sheet(self.spreadsheet_id, 'A:Z')
            if not data:
                return 'No data found.'
            else:
                return data
        except Exception as e:
            print(f'Error: {e}')

    def update_cell(self, row, col, value):
        try:

            write_to_sheet([value], f'{number_to_letter(col)}{row}', self.spreadsheet_id)
        except Exception as e:
            print(f'Error: {e}')

sheets_api = GoogleSheetsAPI(spreadsheet_id1, RANGE_NAME, 'credentials.json')

class Task:
    def __init__(self, description, priority, due_data, status='В ожидании'):
        self.description = description
        self.priority= priority
        self.due_data = due_data
        self.status = status
    def mark_completed(self):
        self.status = 'Завершено'
    def mark_in_progress(self):
        self.status = 'В ожидании'
    def is_overdue(self):
        return self.status != 'Завершено' and datetime.date.today().isoformat() > self.due_data
    def display_task(self):
        print(f'Задача({self.description}, Приоритет: {self.priority}, Крайний срок: {self.due_data}, Статус: {self.status})')

class TaskManager:
    def __init__(self, sheets_api):
        self.sheets_api = sheets_api
        self.tasks = []
    def add_task(self, task):
        try:
            self.sheets_api.append_row([task.description, task.priority, task.due_data, task.status])
            self.tasks.append(task)
        except Exception as e:
            print(f'Error: {e}')
    def load_tasks_from_sheet(self):
        self.tasks = []
        for task in self.sheets_api.get_all_tasks():
            self.tasks.append(Task(task[0], task[1], task[2], task[3]))
    def update_task_status(self):
        for task in self.tasks:
            if task.is_overdue() == True:
                task.status = 'Просрочено'
                try:
                    i = 1
                    while read_row_from_sheet(self.sheets_api.spreadsheet_id, f'A{i}')[0][0] != task.description:
                        i += 1
                    write_to_sheet([['Просрочено']], f'D{i}', self.sheets_api.spreadsheet_id)
                except Exception as e:
                    print(f'Error: {e}')

    def mark_task_completed(self, task_description):
        for task in self.tasks:
            if task.description == task_description:
                task.mark_completed()
                try:
                    i = 1
                    while read_row_from_sheet(self.sheets_api.spreadsheet_id, f'A{i}')[0][0] != task.description:
                        i += 1
                    write_to_sheet([['Завершено']], f'D{i}', self.sheets_api.spreadsheet_id)
                    break
                except Exception as e:
                    print(f'Error: {e}')
    def get_summary(self):
        return {
            'Завершено': len([i for i in self.tasks if i.status == 'Завершено']),
            'В ожидании': len([i for i in self.tasks if i.status == 'В ожидании']),
            'Просрочено': len([i for i in self.tasks if i.status == 'Просрочено'])
        }
    def show_tasks(self):
        for task in self.tasks:
            task.display_task()

class ReportVisualizer:
    def generate_task_completion_chart(summary):
        labels = ['Завершено', 'В ожидании', 'Просрочено']
        sizes = [summary['Завершено'], summary['В ожидании'], summary['Просрочено']]
        colors = ['green', 'yellow', 'red']

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.axis('equal')  # чтобы круг был кругом

        plt.title('Статус задач')
        plt.show()

    def generate_task_trends_chart(tasks):
        tasks.sort(key=lambda x: datetime.strptime(x.due_data, '%Y-%m-%d'))

        # Получаем даты и прогресс задач
        dates = [datetime.strptime(task.due_data, '%Y-%m-%d') for task in tasks]
        progress = []

        for task in tasks:
            if task.status == 'Завершено':
                progress.append(1)
            elif task.status in ['В ожидании', 'Просрочено']:
                progress.append(0.5)

        # Строим столбчатую диаграмму
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(dates, progress, color='blue')

        # Настроим отображение даты на оси X
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)

        ax.set_xlabel('Дата')
        ax.set_ylabel('Прогресс задачи')
        ax.set_title('Прогресс выполнения задач')

        plt.show()

def main():
    creds_file = 'credentials.json'
    spreadsheet_id = ''
    range_name = 'A:Z'

    google_sheets = GoogleSheetsAPI(spreadsheet_id, range_name, creds_file)
    task_manager = TaskManager(google_sheets)

    task_manager.load_tasks_from_sheet()

    if task_manager.tasks:
        for task in task_manager.tasks:
            print(
                f"Задача({task.description}, Приоритет: {task.priority}, Крайний срок: {task.due_data}, Статус: {task.status})")
    else:
        print("Данные не найдены.")

    task1 = Task('Поспать', 'Высокий', '2024-10-10')
    task_manager.add_task(task1)

    task2 = Task('Поесть', 'Средний', '2024-10-12')
    task_manager.add_task(task2)


    task_manager.mark_task_completed('Поесть')
    print("Row updated: Завершено")

    task_manager.show_tasks()

    summary = task_manager.get_summary()
    pprint(summary)

    ReportVisualizer.generate_task_completion_chart(summary)
    ReportVisualizer.generate_task_trends_chart(task_manager.tasks)


if __name__ == "__main__":
    main()
