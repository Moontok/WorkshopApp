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
    

    def resize_request(self, range: str, size: int) -> None:
        """Resize a column or row by specified number of pixels.

        Range formats:
            - Columns: "SheetName!StartColumn:EndColumn "
                - Ex. "Sheet1!A:A" will resize column A.
            - Rows: "SheetName!StartRow:EndRow"
                - Ex. "Sheet1!1:1" will resize row 1.
        """

        processed_range: list = self.process_range(range)
        dimension: str = ""
        start_index: int = 0
        end_index: int = 0

        if processed_range[2] < 0:            
            dimension = "COLUMNS"
            start_index = processed_range[1]
            end_index = processed_range[3]
        else:
            dimension = "ROWS"
            start_index = processed_range[2]
            end_index = processed_range[4]

        format_style = {
            "updateDimensionProperties": {
                "properties": {
                    "pixelSize": size
                },
                "fields": "pixelSize",
                "range": {
                    "sheetId": processed_range[0],
                    "dimension": dimension,
                    "startIndex": start_index,
                    "endIndex": end_index
                }
            }
        }
        self.requests.append(format_style)


    def merge_cell_range_request(self, range: str, merge_type: str="MERGE_ALL") -> None:
        """Merge cells in the provided range based on merge type.
        Merge Types: MERGE_ALL, MERGE_COLUMNS, MERGE_ROWS
        """
        
        processed_range: list = self.process_range(range)
        format_style = {
            "mergeCells": {
                "range": {
                    "sheetId": processed_range[0],
                    "startColumnIndex": processed_range[1],
                    "startRowIndex": processed_range[2],
                    "endColumnIndex": processed_range[3],
                    "endRowIndex": processed_range[4]
                },
                "mergeType": merge_type
            }
        }
        self.requests.append(format_style)

    
    def format_font_range_request(
        self,
        range: str,
        font_family: str = "Arial",
        font_size: int=12,
        bold: bool = False,
        italic: bool = False,
        strikethrough: bool = False,
        underline: bool = False,
        text_color: tuple = (0, 0, 0)
    ) -> None:
        """Set the font for a range of cells."""

        processed_range = self.process_range(range)
        format_style = {
            "repeatCell": {
                "range": {
                    "sheetId": processed_range[0],
                    "startColumnIndex": processed_range[1],
                    "startRowIndex": processed_range[2],
                    "endColumnIndex": processed_range[3],
                    "endRowIndex": processed_range[4]
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "foregroundColor": {"red": text_color[0], "green": text_color[1], "blue": text_color[2]},
                            "font_family": font_family,
                            "fontSize": font_size,
                            "bold": bold,
                            "italic": italic,
                            "strikethrough": strikethrough,
                            "underline": underline
                        }
                    }
                },
                "fields": "userEnteredFormat(textFormat)"
            }
        }
        self.requests.append(format_style)


    def fill_range_request(self, range: str, fill_color: tuple=(1, 1, 1)) -> None:
        """Set the background fill for a range of cells."""

        processed_range = self.process_range(range)
        format_style = {
            "repeatCell": {
                "range": {
                    "sheetId": processed_range[0],
                    "startColumnIndex": processed_range[1],
                    "startRowIndex": processed_range[2],
                    "endColumnIndex": processed_range[3],
                    "endRowIndex": processed_range[4]
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


    def format_range_outer_border(self,  range: str, type: str="SOLID", color: tuple=(0, 0, 0)) -> None:
        """Set the outer border for a range of cells."""

        processed_range = self.process_range(range)
        border_format = {
            "updateBorders": {
                "range": {
                    "sheetId": processed_range[0],
                    "startColumnIndex": processed_range[1],
                    "startRowIndex": processed_range[2],
                    "endColumnIndex": processed_range[3],
                    "endRowIndex": processed_range[4]
                },
                "top": { "style": type, "color": {"red": color[0], "green": color[1], "blue": color[2]}},
                "bottom": {"style": type, "color": {"red": color[0], "green": color[1], "blue": color[2]}},
                "left": {"style": type, "color": {"red": color[0], "green": color[1], "blue": color[2]}},
                "right": {"style": type,  "color": {"red": color[0], "green": color[1], "blue": color[2]}},
            }
        }
        self.requests.append(border_format)


    def process_range(self, range: str) -> tuple:
        """Process the range into sheet_id and starting and ending cell."""

        range_parts: list = range.split("!")
        sheet_id: int = self.current_sheets[range_parts[0]]
        range_pair_values: list = range_parts[1].split(":")   
        start_pair: list = self.process_cell_pair(range_pair_values[0])
        end_pair: list = self.process_cell_pair(range_pair_values[1])

        return [sheet_id, start_pair[0], start_pair[1]-1, end_pair[0] + 1, end_pair[1]]

        
    def process_cell_pair(self, pair: str) -> list:        
        """Determine the numerical value for the cell locations."""

        base_columns = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        column_num: int = 0
        row_num: int = -1
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
    print(gs.process_range("A1:B1"))