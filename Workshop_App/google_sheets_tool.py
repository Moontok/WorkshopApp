
class GoogleSheetsTool:
        
    def __init__(self):
        self.current_sheets = [0]

    
    def add_row(self, row: list) -> None:
        pass
    
    def add_values_request(self, range: str, rows: list) -> dict:
        """Add values in a range."""
        
        return {"range": f"{range}", "values": rows}
    
    
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