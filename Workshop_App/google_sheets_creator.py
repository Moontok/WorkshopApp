from googleapiclient.discovery import build
from google.oauth2 import service_account
from workshop_tool import WorkshopsTool
from spread_sheet_base_creator import SpreadSheetBaseCreator
from google_sheets_tool import GoogleSheetsTool

class GoogleSheetCreator(SpreadSheetBaseCreator):

    def __init__(self):
        super().__init__()

        # Credentials
        self.service_account_file: str = "google_info.json"
        self.g_scopes: list = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=self.g_scopes
        )


    def export_workshops_info(self, ws: WorkshopsTool) -> None:
        """Exports the searched workshop information to an google sheet."""
                
        gs = GoogleSheetsTool()
        workshops: list = ws.get_most_recent_search_results()

        spread_sheet_id = "1nYTi7s1VDFXsqupYs7ZPe_9_SrDL2hAAI_i0jnEB5hw"

        service = build("sheets", "v4", credentials=self.creds)
        
        # Call the Sheets API
        sheet = service.spreadsheets()

        # Setting up Google Spread Sheet
        requests = list()

        requests.append(gs.change_google_sheet_name_request("Workshop Info"))
        requests.append(gs.change_sheet_name_request(0, "Workshops"))
        # requests.append(gs.add_sheet_request("Attendance"))
        requests.append(gs.format_font_range_request(0, start=(1,1), end=(1,1), font_size=18, bold=True))
        requests.append(gs.fill_range_request(0, start=(1,1), end=(1,8), fill_color=(0.0, 0.9, 0.7)))
        requests.append(gs.format_font_range_request(0, start=(len(workshops)+2, 1), end=(len(workshops)+2, 5), bold=True))
        # requests.append(gs.format_range_outer_border(0, start_column=0, end_column=8))
        
        body = {"requests": requests}

        sheet.batchUpdate(spreadsheetId=spread_sheet_id, body=body).execute()        
  
        # Adding Values

        workshops_rows = list()
        # attendance_rows = list()

        for workshop in workshops:
            row: list = self.build_row_for_workshop(ws.get_co_op_info(), workshop)
            workshops_rows.append(row[:8])
        workshops_rows.sort()
        workshops_rows.append([])
        workshops_rows.append(["Total:", f"{len(workshops)}", "", "Signed Up:", f"=SUM(E3:E{len(workshops)+3})"])

        add_value_requests = list()
        add_value_requests.append(gs.add_values_request("Workshops!A1", [["Workshops At A Glance"]]))
        add_value_requests.append(gs.add_values_request("Workshops!A3", workshops_rows))

        values_body = {"valueInputOption": "USER_ENTERED", "data": add_value_requests}
        sheet.values().batchUpdate(spreadsheetId=spread_sheet_id, body=values_body).execute()


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
    gt = GoogleSheetCreator()
    gt.export_workshops_info()