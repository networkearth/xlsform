import json
import os

class SheetHelper(object):
    SHEET_NAME = 'sheet'

    def __init__(self, base_obj, read_func, write_func):
        self.obj = base_obj
        self.read_func = read_func
        self.write_func = write_func

    @classmethod
    def _get_sheet(cls, workbook):
        return workbook[cls.SHEET_NAME]

    @classmethod
    def _write_json(cls, folder, obj):
        with open(os.path.join(folder, cls.SHEET_NAME + '.json'), 'w') as fh:
            json.dump(obj, fh, sort_keys=True, indent=4)

    @classmethod
    def _read_json(cls, folder):
        with open(os.path.join(folder, cls.SHEET_NAME + '.json'), 'r') as fh:
            return json.load(fh)

    def read_json(self, folder):
        self.obj = self._read_json(folder)

    def write_json(self, folder):
        self._write_json(folder, self.obj)

    def read_sheet(self, workbook):
        sheet = self._get_sheet(workbook)
        self.obj = self.read_func(sheet)
                
    def write_sheet(self, workbook):
        sheet = self._get_sheet(workbook)
        self.write_func(sheet, self.obj)

def get_columns(sheet):
    return {
        i: cell.value.strip() for i, cell in enumerate(sheet[1])
        if cell.value
    }

def write_survey(sheet, survey, columns=None, next_row=2):
    if not columns:
        columns = {}
    for element in survey:
        for column, value in element.items():
            if column == 'survey':
                continue
            if column not in columns:
                columns[column] = max(columns.values()) + 1 if columns else 1
                sheet.cell(row=1, column=columns[column], value=column)
            sheet.cell(row=next_row, column=columns[column], value=value)
            
        type_definitions = [
            e.strip() for e in element['type'].split(' ') if e.strip() != ''
        ]
        if type_definitions[0].startswith('begin'):
            next_row = write_survey(sheet, element['survey'], columns, next_row=next_row+1)
            sheet.cell(
                row=next_row, column=columns['type'], 
                value=' '.join(['end' + type_definitions[0][5:]] + type_definitions[1:])
            )
        next_row += 1
    return next_row

def add_survey_element(obj, keys, value):
    if not keys:
        obj.append(value)
        return len(obj) - 1
    key = keys[0]
    if key == 'survey' and key not in obj:
        obj[key] = []
    return add_survey_element(obj[key], keys[1:], value)

def read_survey(sheet):
    survey = []
    current_survey_keys = []
    columns = get_columns(sheet)
    for row in sheet.iter_rows(min_row=2):
        element = {
            columns[i]: cell.value
            for i, cell in enumerate(row)
            if cell.value
        }
        if not element.get('type'):
            continue
        type_definitions = [
            e.strip() for e in element['type'].split(' ') if e.strip() != ''
        ]
        if type_definitions[0].startswith('end'):
            current_survey_keys = current_survey_keys[:-2]
            continue

        index_of_element = add_survey_element(survey, current_survey_keys, element)
        if type_definitions[0].startswith('begin'):
            current_survey_keys.append(index_of_element)
            current_survey_keys.append('survey')
    return survey

class SurveyHelper(SheetHelper):
    SHEET_NAME = 'survey'

    def __init__(self):
        super().__init__([], read_survey, write_survey)

def get_extra_keys(choices):
    for key, options in choices.items():
        for choice, data in options.items():
            extra_keys = {
                key: i for i, key in enumerate(data.keys())
            }
            break
        break
    return extra_keys

def write_choices(sheet, choices):
    row = 1
    # write the header row
    sheet.cell(row=row, column=1, value='list_name')
    sheet.cell(row=row, column=2, value='name')
    extra_keys = get_extra_keys(choices)
    for key, i in extra_keys.items():
        sheet.cell(row=row, column=i+3, value=key)
    # write the data rows
    for key, options in choices.items():
        for choice, data in options.items():
            row += 1
            for i, value in enumerate([key, choice]):
                sheet.cell(row=row, column=i+1, value=value)
            for extra_key, i in extra_keys.items():
                sheet.cell(row=row, column=i+3, value=data[extra_key])

def read_choices(sheet):
    choices = {}
    columns = {
        value: key for key, value in get_columns(sheet).items()
    }
    for row in sheet.iter_rows(min_row=2):
        if not row[columns['list_name']].value or not row[columns['list_name']].value.strip():
            continue
        key = row[columns['list_name']].value.strip()
        if key not in choices:
            choices[key] = {}
        choices[key][row[columns['name']].value] = {
            col_name: row[col_num].value if row[col_num].value else ''
            for col_name, col_num in columns.items()
            if col_name not in ['list_name', 'name']
        }
    return choices

class ChoicesHelper(SheetHelper):
    SHEET_NAME = 'choices'

    def __init__(self):
        super().__init__({}, read_choices, write_choices)

def write_settings(sheet, settings):
    for column, (key, value) in enumerate(settings.items()):
        sheet.cell(row=1, column=column+1, value=key)
        sheet.cell(row=2, column=column+1, value=value)

def read_settings(sheet):
    settings = {}
    for column in sheet.columns:
        if not column[0].value or not column[0].value.strip():
            continue
        key = column[0].value.strip()
        if not key:
            continue
        try:
            settings[key] = next(e.value.strip() for e in column[1:] if e.value and e.value.strip())
        except StopIteration:
            pass
    return settings

class SettingsHelper(SheetHelper):
    SHEET_NAME = 'settings'

    def __init__(self):
        super().__init__({}, read_settings, write_settings)
