from googleapiclient.discovery import build
from google.oauth2 import service_account

class GoogleSheetTool:

    def __init__(self):        
        # Credentials
        self.service_account_file: str = "google_info.json"
        self.g_scopes: list = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=self.g_scopes
        )


    def export_workshops_info(self, ui: GuiWindow, ws: WorkshopsTool) -> None:
        """Exports the searched workshop information to an .xlsx file."""

        service = build("sheets", "v4", credentials=self.creds)
        
        # Call the Sheets API
        sheet = service.spreadsheets()

        values_to_write = [
            ["a", "b"],
            ["c", "d", "e"]
        ]

        sheet.values().update(
            spreadsheetId="1nYTi7s1VDFXsqupYs7ZPe_9_SrDL2hAAI_i0jnEB5hw",
            range="Sheet1!a1",
            valueInputOption="USER_ENTERED",
            body={"values": values_to_write},
        ).execute()


    def format_workshops_sheet(self, worksheet, last_row: int) -> None:
        """Formats excel workshops sheet."""
        pass


    def format_generated_ws_sheet(self, worksheet) -> None:
        """General format for each Co-op sheet."""
        pass


    def format_attendance_sheet(self, worksheet, last_row: int, coops: list) -> None:    
        """Formats excel attendance sheet."""
        pass



if __name__ == "__main__":
    gt = GoogleSheetTool()
    gt.main()