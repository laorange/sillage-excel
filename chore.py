# from openpyxl import Workbook
# from openpyxl.utils import get_column_letter
#
# wb = Workbook()
#
# dest_filename = 'empty_book.xlsx'
#
# ws1 = wb.active
# ws1.title = "range names"
#
# for row in range(1, 40):
#     ws1.append(range(600))
#
# ws2 = wb.create_sheet(title="Pi")
#
# ws2['F5'] = 3.14
#
# ws3 = wb.create_sheet(title="Data")
# for row in range(10, 20):
#     for col in range(27, 54):
#         _ = ws3.cell(column=col, row=row, value="{0}".format(get_column_letter(col)))
# print(ws3['AA10'].value)
#
# wb.save(filename=dest_filename)


# from openpyxl import Workbook, styles
# from openpyxl.utils import get_column_letter
#
# wb = Workbook()
#
# dest_filename = 'empty_book.xlsx'
#
# ws = wb.active
# ws.merge_cells('A2:D2')
#
# border = styles.Border(left=styles.Side(border_style="thin", color='000000'),
#                        right=styles.Side(border_style="thin", color='000000'),
#                        top=styles.Side(border_style="thin", color='000000'),
#                        bottom=styles.Side(border_style="thin", color='000000'),
#                        outline=styles.Side(border_style="thin", color='000000'),
#                        vertical=styles.Side(border_style="thin", color='000000'),
#                        horizontal=styles.Side(border_style="thin", color='000000'))
# fill = styles.PatternFill("solid", fgColor="FFFFFF")
# alignment = styles.Alignment(horizontal="center", vertical="center", wrap_text=True)
#
# cell = ws['C3']
# cell.border = border
# cell.fill = fill
# cell.alignment = alignment
# cell.value = """yguichsajkbhguihojcsalhj
# scajbkljncsbuhlasjb
# ascklisacknbjkucsahljb
# aschisacljbku"""
#
# for idx, col in enumerate(ws.columns, 1):
#     ws.column_dimensions[get_column_letter(idx)].auto_size = True
# wb.save(filename=dest_filename)


# border = styles.Border(left=styles.Side(border_style="thin", color='000000'),
#                        right=styles.Side(border_style="thin", color='000000'),
#                        top=styles.Side(border_style="thin", color='000000'),
#                        bottom=styles.Side(border_style="thin", color='000000'),
#                        outline=styles.Side(border_style="thin", color='000000'),
#                        vertical=styles.Side(border_style="thin", color='000000'),
#                        horizontal=styles.Side(border_style="thin", color='000000'))
#
# alignment = styles.Alignment(horizontal="center", vertical="center", wrap_text=True)
