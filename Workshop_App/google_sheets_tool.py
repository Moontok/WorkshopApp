from googleapiclient.discovery import build
from google.oauth2 import service_account

class GoogleSheetsTool:
        
    def __init__(self, spread_sheet_id: str):

        self.spread_sheet_id = spread_sheet_id
        self.current_sheets: dict = {"Sheet1":0}
        self.sheet_id_runner: int = 1
        self.requests = list()
        self.update_values_requests = list()       

        # Credentials
        self.service_account_file: str = "google_info.json"
        self.g_scopes: list = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=self.g_scopes
        )     

        self.service = build("sheets", "v4", credentials=self.creds)
        self.sheet = self.service.spreadsheets()

    
    def values_batch_update(self) -> None:
        """Batch updates all current value requests."""

        values_body = {"valueInputOption": "USER_ENTERED", "data": self.update_values_requests}
        self.sheet.values().batchUpdate(spreadsheetId=self.spread_sheet_id, body=values_body).execute()
        self.update_values_requests.clear()


    def batch_update(self) -> None:
        """Batch updates all current requests."""
        
        body: dict = {"requests": self.requests}        
        self.sheet.batchUpdate(spreadsheetId=self.spread_sheet_id, body=body).execute()
        self.requests.clear()
    
    def add_values_request(self, range: str, rows: list) -> None:
        """Add values in a range."""
        
        self.update_values_requests.append({"range": range, "values": rows})
    
    
    def change_google_sheet_title_request(self, name: str) -> None:
            "Change the name of the google sheet."

            self.requests.append({"updateSpreadsheetProperties":{"properties":{"title": f"{name}"},"fields": "title"}})


    def change_sheet_name_request(self, old_name: str, new_name: str) -> None:
        """Change the name of the specified sheet."""
        
        self.current_sheets[new_name] = self.current_sheets[old_name]
        del self.current_sheets[old_name]

        self.requests.append({"updateSheetProperties":{"properties":{"sheetId": self.current_sheets[new_name],"title": f"{new_name}"},"fields": "title"}})


    def add_sheet_request(self, name: str) -> None:
        """Add a new sheet request to the Google Sheet."""
        
        self.current_sheets[name] = self.sheet_id_runner
        self.sheet_id_runner += 1

        self.requests.append({"addSheet":{"properties":{"sheetId": self.current_sheets[name], "title": f"{name}"}}})
    
    
    def format_font_range_request(
        self,
        sheet_id: int,
        range: list,
        font_size: int=12,
        bold: bool = False,
        italic: bool = False,
        text_color: tuple = (0.0, 0.0, 0.0)
    ) -> None:
        range = self.get_range(range)
        format_style = {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startColumnIndex": range[0],
                    "startRowIndex": range[1],
                    "endColumnIndex": range[2],
                    "endRowIndex": range[3]
                },
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
        self.requests.append(format_style)


    def fill_range_request(
        self,
        sheet_id: int,
        range: list,
        fill_color: tuple=(1.0, 1.0, 1.0),
    ) -> None:
        range = self.get_range(range)
        format_style = {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startColumnIndex": range[0],
                    "startRowIndex": range[1],
                    "endColumnIndex": range[2],
                    "endRowIndex": range[3]
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": fill_color[0], "green": fill_color[1], "blue": fill_color[2]}                        
                    }
                },
                "fields": "userEnteredFormat(backgroundColor)"
            }
        }
        self.requests.append(format_style)


    def format_range_request(
        self,
        sheet_id: int,
        range: list,
        fill_color: tuple=(1.0, 1.0, 1.0),
        text_color: tuple=(0.0, 0.0, 0.0),
        h_align: str="LEFT",
        font_size: int=12,
        bold_text: bool = False
    ) -> None:
        range = self.get_range(range)
        format_style = {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startColumnIndex": range[0],
                    "startRowIndex": range[1],
                    "endColumnIndex": range[2],
                    "endRowIndex": range[3]
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
        self.requests.append(format_style)


    def format_range_outer_border(
        self,
        sheet_id: int,
        range: list,
        type: str="SOLID",
        color: tuple=(0.0, 0.0, 0.0)
    ) -> None:
        range = self.get_range(range)
        border_format = {
            "updateBorders": {
                "range": {
                    "sheetId": sheet_id,
                    "startColumnIndex": range[0],
                    "startRowIndex": range[1],
                    "endColumnIndex": range[2],
                    "endRowIndex": range[3]
                },
                "top": { "style": type, "color": {"red": color[0], "green": color[1], "blue": color[2]}},
                "bottom": {"style": type, "color": {"red": color[0], "green": color[1], "blue": color[2]}},
                "left": {"style": type, "color": {"red": color[0], "green": color[1], "blue": color[2]}},
                "right": {"style": type,  "color": {"red": color[0], "green": color[1], "blue": color[2]}},
            }
        }
        self.requests.append(border_format)


    def get_range(self, range: str) -> tuple:

        range_values: list = range.split(":")   
        start_pair: list = self.process_cell_pair(range_values[0])
        end_pair: list = self.process_cell_pair(range_values[1])

        return [start_pair[0], start_pair[1]-1, end_pair[0] + 1, end_pair[1]]

        
    def process_cell_pair(self, pair: str) -> list:        
        
        base_columns = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        column_num: int = 0
        row_num: int = 0
        column_char_count: int = 0

        for i, char in enumerate(pair):
            if char in base_columns:
                column_num += base_columns.index(char)
                column_char_count += 1
            else:
                row_num = int(pair[i:])
                break
        
        if column_char_count > 1:
            column_num += 1

        return [column_num, row_num]               


if __name__ == "__main__":
    gs = GoogleSheetsTool()
    print(gs.get_range("A1:B1"))