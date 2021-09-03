from googleapiclient.discovery import build
from google.oauth2 import service_account
from pygsheets import authorize
from workshop_tool import WorkshopsTool
from gui_window import GuiWindow
from spread_sheet_base_tool import SpreadSheetBaseTool

class GoogleSheetTool(SpreadSheetBaseTool):

    def __init__(self):
        super().__init__() 

        # Credentials
        self.service_account_file: str = "google_info.json"
        self.g_scopes: list = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=self.g_scopes
        )


    def export_workshops_info(self, ui: GuiWindow=None, ws: WorkshopsTool=None) -> None:
        """Exports the searched workshop information to an .xlsx file."""

        service = build("sheets", "v4", credentials=self.creds)
        
        # Call the Sheets API
        sheet = service.spreadsheets()

        # ws.set_search_phrase(ui.lineEditPhrase.text())

        # workshops: list = ws.get_most_recent_search_results()

        values_to_write = [
            ["a", "b"],
            ["c", "d", "e"]
        ]

        sheet.clear()

        sheet.values().update(
            spreadsheetId="1nYTi7s1VDFXsqupYs7ZPe_9_SrDL2hAAI_i0jnEB5hw",
            range="Sheet1!a1",
            valueInputOption="USER_ENTERED",
            body={"values": values_to_write},
        ).execute()


    def format_workshops_sheet(self, worksheet) -> None:
        """Formats excel workshops sheet."""
        pass


    def format_generated_ws_sheet(self, worksheet) -> None:
        """General format for each Co-op sheet."""
        pass


    def format_attendance_sheet(self, worksheet) -> None:    
        """Formats excel attendance sheet."""
        pass



if __name__ == "__main__":
    gt = GoogleSheetTool()
    gt.export_workshops_info()