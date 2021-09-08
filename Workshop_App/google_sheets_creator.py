from workshop_tool import WorkshopsTool
from spread_sheet_base_creator import SpreadSheetBaseCreator
from google_sheets_tool import GoogleSheetsTool
from gui_window import GuiWindow
from typing import Optional

class GoogleSheetCreator(SpreadSheetBaseCreator):

    def __init__(self):
        super().__init__()

        self.colors = {
            "light_grey": (0.8, 0.8, 0.8),
            "light_green": (0.68, 0.92, 0.68),
            "dark_grey": (0.2, 0.2, 0.2)
        }


    def export_workshops_info(self, ws: WorkshopsTool, ui: GuiWindow) -> None:
        """Exports the searched workshop information to an google sheet."""

        gs = GoogleSheetsTool()
        file_and_folder_info: Optional[tuple] = ui.google_filename_popup_box()
        if file_and_folder_info != None:
            gs.set_file_and_folder_info(file_and_folder_info)
            gs.authenticate("google_info.json")
        else:
            return        

        workshops: list = ws.get_most_recent_search_results()

        workshop_rows = list()

        for workshop in workshops:
            row: list = self.build_row_for_workshop(ws.get_co_op_info(), workshop)
            workshop_rows.append(row)
        workshop_rows.sort()

        gs.change_sheet_name_request("Sheet1", "Workshops")        
        gs.add_sheet_request("Attendance")
        gs.batch_update()

        gs.add_values_request("Workshops!A1", [
            ["Workshops At A Glance"],
            []
        ])

        gs.add_values_request("Attendance!A1:C3", [
            ["Workshop Name:", "", workshops[0]["workshop_name"]],
            ["Workshop Dates:", "", self.format_dates(workshops[0])],
            []
        ])

        for row in workshop_rows:
            gs.add_values_request(f"Workshops!A{gs.get_next_row('Workshops')}", [row[:8]])
            co_op_sheet: str = row[0]
            gs.add_sheet_request(co_op_sheet)
            gs.add_values_request(f"{co_op_sheet}!A1", [
                row[:3],
                ["Dates:", ", ".join(row[11])],
                ["Credit:", row[12]],
                ["Fee:", row[13]],
                ["Description:", row[9]],
                ["Session Link:", row[7]],
                ["Signed Up"]
            ])
            gs.add_values_request(f"Attendance!A{gs.get_next_row('Attendance')}", [
                [row[0], row[1], row[7]],
                ["Name", "Email", "District", "Hours", "Dates Attended"]
            ])

            if len(row[8]) > 0:
                for participant in row[8]:
                    gs.add_values_request(f"{co_op_sheet}!A{gs.get_next_row(co_op_sheet)}", [
                        [participant["name"], "", participant["email"], participant["school"]]
                    ])
                    gs.add_values_request(f"Attendance!A{gs.get_next_row('Attendance')}", [
                        [participant["name"], participant["email"], participant["school"]]
                    ])
            gs.add_values_request(f"Attendance!A{gs.get_next_row('Attendance')}", [
                    []
            ])
            self.co_op_abbreviations.append(row[0])
            self.format_generated_ws_sheet(gs, co_op_sheet, len(row[8]))

        gs.add_values_request(
            f"Workshops!A{len(workshops)+4}",
            [["Total:", f"{len(workshops)}", "", "Signed Up:", f"=SUM(E3:E{len(workshops)+3})"]]
        )

        gs.batch_update()
        gs.values_batch_update()

        self.format_workshops_sheet(gs, len(workshops))
        self.format_attendance_sheet(gs, workshop_rows)


    def format_workshops_sheet(self, gs: GoogleSheetsTool, number_of_workshops: int) -> None:
        """Formats excel workshops sheet."""
        
        sheet_name: str = "Workshops"

        gs.format_font_range_request(f"{sheet_name}!A1:A1", font_size=18, bold=True)
        gs.fill_range_request(f"{sheet_name}!A1:H1", self.colors["light_green"])
        gs.format_font_range_request(f"{sheet_name}!A{number_of_workshops + 4}:E{number_of_workshops + 4}", bold=True)
        gs.set_outer_border_range_request(f"{sheet_name}!A1:H1")
        gs.merge_cells_range_request(f"{sheet_name}!A1:H1")
        gs.resize_request(f"{sheet_name}!A:A", 100)
        gs.resize_request(f"{sheet_name}!B:B", 50)
        gs.resize_request(f"{sheet_name}!C:C", 500)
        gs.resize_request(f"{sheet_name}!D:D", 120)
        gs.resize_request(f"{sheet_name}!E:F", 40)
        gs.resize_request(f"{sheet_name}!G:G", 350)
        gs.resize_request(f"{sheet_name}!H:H", 450)
        gs.resize_request(f"{sheet_name}!1:1", 30)

        gs.batch_update()


    def format_generated_ws_sheet(self, gs: GoogleSheetsTool, sheet_name: str, number_of_participants: int) -> None:
        """General format for each Co-op sheet."""        

        gs.format_font_range_request(f"{sheet_name}!A1:D1", font_size=12, bold=True)
        gs.align_and_wrap_cells_range_request(f"{sheet_name}!A1:D4", horizontal="LEFT")
        gs.fill_range_request(f"{sheet_name}!A1:D1", self.colors["light_green"])
        
        gs.merge_cells_range_request(f"{sheet_name}!C1:D1")
        gs.merge_cells_range_request(f"{sheet_name}!B2:D2")
        gs.merge_cells_range_request(f"{sheet_name}!B3:D3")
        gs.merge_cells_range_request(f"{sheet_name}!B4:D4")
        gs.merge_cells_range_request(f"{sheet_name}!B5:D5")
        gs.merge_cells_range_request(f"{sheet_name}!B6:D6")

        gs.align_and_wrap_cells_range_request(f"{sheet_name}!A5:A5", vertical="TOP")
        gs.align_and_wrap_cells_range_request(f"{sheet_name}!B5:B5", vertical="TOP", wrapping="WRAP")

        gs.merge_cells_range_request(f"{sheet_name}!A7:D7")
        gs.format_font_range_request(f"{sheet_name}!A7:D7", font_size=12, bold=True)
        gs.fill_range_request(f"{sheet_name}!A7:D7", self.colors["light_grey"])

        gs.resize_request(f"{sheet_name}!A:B", 100)
        gs.resize_request(f"{sheet_name}!C:D", 300)

        for row in range(8, number_of_participants + 8):
            gs.merge_cells_range_request(f"{sheet_name}!A{row}:B{row}")
            gs.align_and_wrap_cells_range_request(f"{sheet_name}!A{row}:D{row}", wrapping="CLIP")


    def format_attendance_sheet(self, gs: GoogleSheetsTool, workshop_rows: list) -> None:    
        """Formats excel attendance sheet."""
        
        sheet_name: str = "Attendance"

        gs.merge_cells_range_request(f"{sheet_name}!A1:B1")
        gs.merge_cells_range_request(f"{sheet_name}!A2:B2")
        gs.merge_cells_range_request(f"{sheet_name}!C1:E1")
        gs.merge_cells_range_request(f"{sheet_name}!C2:E2")

        gs.resize_request(f"{sheet_name}!A:A", 200)
        gs.resize_request(f"{sheet_name}!B:C", 250)
        gs.resize_request(f"{sheet_name}!D:D", 100)
        gs.resize_request(f"{sheet_name}!E:E", 300)

        gs.format_font_range_request(f"{sheet_name}!A1:A2", font_size=12, bold=True)
        gs.align_and_wrap_cells_range_request(f"{sheet_name}!A1:A2", "RIGHT")

        gs.format_font_range_request(f"{sheet_name}!C1:E2", font_size=12, bold=True, text_color=self.colors["light_green"])
        gs.fill_range_request(f"{sheet_name}!C1:E2", self.colors["dark_grey"])
        gs.align_and_wrap_cells_range_request(f"{sheet_name}!C1:E2", "CENTER")
        gs.set_outer_border_range_request(f"{sheet_name}!A1:E2", "SOLID_THICK")


        current_row = 4
        for row in workshop_rows:
            gs.format_font_range_request(f"{sheet_name}!A{current_row}:B{current_row}", font_size=12, bold=True)

            cell_range = f"{sheet_name}!A{current_row}:E{current_row}"
            gs.fill_range_request(cell_range, fill_color=self.colors["light_green"])
            gs.set_outer_border_range_request(cell_range)
            gs.align_and_wrap_cells_range_request(cell_range, horizontal="LEFT")
            gs.merge_cells_range_request(f"{sheet_name}!C{current_row}:E{current_row}")
            
            current_row += 1

            cell_range = f"{sheet_name}!A{current_row}:E{current_row}"
            gs.format_font_range_request(cell_range, font_size=12)
            gs.fill_range_request(cell_range, self.colors["light_grey"])
            gs.align_and_wrap_cells_range_request(f"{sheet_name}!A{current_row}:C{current_row}", "LEFT")
            gs.align_and_wrap_cells_range_request(f"{sheet_name}!D{current_row}:E{current_row}", "RIGHT")
            
            for _ in range(len(row[8])):
                current_row += 1
                cell_range = f"{sheet_name}!A{current_row}:E{current_row}"
                gs.format_font_range_request(cell_range, font_size=12)
                gs.align_and_wrap_cells_range_request(f"{sheet_name}!A{current_row}:C{current_row}", "LEFT")
                gs.align_and_wrap_cells_range_request(f"{sheet_name}!D{current_row}:E{current_row}", "RIGHT")
                            
            current_row += 2
        
        gs.values_batch_update()
        gs.batch_update()


if __name__ == "__main__":
    print("This is a module...")