
class GoogleSheetsTool:
        
    def __init__(self):
        self.current_sheets = [0]

    
    def add_row(self, row: list) -> None:
        pass
    
    def add_values_request(self, range: str, rows: list) -> dict:
        """Add values in a range."""
        
        return {"range": range, "values": rows}
    
    
    def change_google_sheet_name_request(self, name: str) -> dict:
            "Change the name of the google sheet."

            return {"updateSpreadsheetProperties":{"properties":{"title": f"{name}"},"fields": "title"}}


    def change_sheet_name_request(self, sheet_index: int, new_name: str) -> dict:
        """Change the name of the specified sheet."""
        
        sheet_id: int = self.current_sheets[sheet_index]
        return {"updateSheetProperties":{"properties":{"sheetId": sheet_id,"title": f"{new_name}"},"fields": "title"}}


    def add_sheet_request(self, name: str) -> dict:
        """Add a new sheet request to the Google Sheet."""
        
        sheet_id: int = len(self.current_sheets)
        self.current_sheets.append(name)

        return {"addSheet":{"properties":{"sheetId": sheet_id, "title": f"{name}"}}}
    
    
    def format_font_range_request(
        self,
        sheet_id: int,
        start: tuple=(0,0),
        end: tuple=(1,1),
        font_size: int=12,
        bold: bool = False,
        italic: bool = False,
        text_color: tuple = (0.0, 0.0, 0.0)
    ) -> dict:
        format_style = {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startColumnIndex": start[0]-1, "startRowIndex": start[1]-1, "endColumnIndex": end[0], "endRowIndex": end[1]},
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "foregroundColor": {"red": text_color[0], "green": text_color[1], "blue": text_color[2]},
                            "fontSize": font_size,
                            "bold": bold,
                            "italic": italic
                        }
                    }
                },
                "fields": "userEnteredFormat(textFormat)"
            }
        }
        return format_style


    def fill_range_request(
        self,
        sheet_id: int,
        start: tuple=(0,0),
        end: tuple=(1,1),
        fill_color: tuple=(1.0, 1.0, 1.0),
    ) -> dict:
        format_style = {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startColumnIndex": start[0]-1, "startRowIndex": start[1]-1, "endColumnIndex": end[0], "endRowIndex": end[1]},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": fill_color[0], "green": fill_color[1], "blue": fill_color[2]}                        
                    }
                },
                "fields": "userEnteredFormat(backgroundColor)"
            }
        }
        return format_style


    def format_range_request(
        self,
        sheet_id: int,
        start_column: int,
        end_column: int, 
        start_row: int,
        end_row: int,
        fill_color: tuple=(1.0, 1.0, 1.0),
        text_color: tuple=(0.0, 0.0, 0.0),
        h_align: str="LEFT",
        font_size: int=12,
        bold_text: bool = False
    ) -> dict:
        format_style = {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row,
                    "startColumnIndex": start_column,
                    "endColumnIndex": end_column
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": fill_color[0], "green": fill_color[1], "blue": fill_color[2]},
                        "horizontalAlignment": h_align,
                        "textFormat": {
                            "foregroundColor": {"red": text_color[0], "green": text_color[1], "blue": text_color[2]},
                            "fontSize": font_size,
                            "bold": bold_text
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        }
        return format_style


    def format_range_outer_border(
        self,
        sheet_id: int,
        start_column: int=0,
        end_column: int=1, 
        start_row: int=0,
        end_row: int=1,
        type: str="SOLID",
        color: tuple=(0.0, 0.0, 0.0),

    ) -> dict:
        border_format = {
            "updateBorders": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row,
                    "startColumnIndex": start_column,
                    "endColumnIndex": end_column
                },
                "top": { "style": type, "color": {"red": color[0], "green": color[1], "blue": color[2]}},
                "bottom": {"style": type, "color": {"red": color[0], "green": color[1], "blue": color[2]}},
                "left": {"style": type, "color": {"red": color[0], "green": color[1], "blue": color[2]}},
                "right": {"style": type,  "color": {"red": color[0], "green": color[1], "blue": color[2]}},
            }
        }
        return border_format


    def get_range(self, range: str) -> tuple:
        
        base_columns = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"        
        start_column = ""
        start_column_num = 0
        start_row = ""        
        end_column = ""
        end_column_num = 0
        end_row = ""

        range_values = range.split(":")
        
        for char in range_values[0]: 
            if char.isalpha(): 
                start_column = "".join([start_column, char]) 
            else:
                start_row = "".join([start_row, char])

        for char in range_values[1]: 
            if char.isalpha(): 
                end_column = "".join([end_column, char]) 
            else:
                end_row = "".join([end_row, char])

        if len(start_column) > 1:
            start_column_num += 1    
            for char in start_column:
                start_column_num += base_columns.index(char)
        else:
            start_column_num = base_columns.index(start_column)

        if len(end_column) > 1:
            end_column_num += 1
            for char in end_column:
                end_column_num += base_columns.index(char)
        else:
            end_column_num = base_columns.index(end_column)

        return (start_column_num, int(start_row)-1, end_column_num+1, int(end_row))
                   


if __name__ == "__main__":
    gs = GoogleSheetsTool()
    print(gs.get_range("A1:B1"))