import datetime
import discord
from prettytable import PrettyTable
from utils.helpers import (
    get_mods_string,
)

def format_td(seconds, digits=3):
    isec, fsec = divmod(round(seconds * 10**digits), 10**digits)
    return f"{datetime.timedelta(seconds=isec)}.{fsec:0{digits}.0f}"

def get_table():
    table = PrettyTable()
    table.border = False
    table.preserve_internal_border = True
    table.header = False
    table.align = "l"
    return table

def format_leaderboard_value(value, di=""):
    if value == None:
        return "0"
    if isinstance(value, datetime.datetime):
        return str(value)
    if di.__contains__("-o") and (
        di["-o"] == "completion" or di["-o"] == "%" or di["-o"] == "length_completion"
    ):
        return str(value) + "%"
    if di.__contains__("-formattime") and di["-formattime"] == "true":
        hours = int(value / 3600)
        minutes = int(value / 60) % 60
        seconds = int(value) % 60
        return str(hours) + "h " + str(minutes) + "m " + str(seconds) + "s"
    if di.__contains__("-float") and di["-float"] == "true":
        if di.__contains__("-precision"):
            precision = 5 if not di["-precision"].isnumeric() else int(di["-precision"])
            return f"{float(value):,.{precision}f}"
        return f"{float(value):,.2f}"
    if di.__contains__("-float") and di["-float"] == "false":
        return f"{int(value):,}"
    if di.__contains__("-o") and "." in str(value):
        return f"{float(value):,.2f}"
    return f"{int(value):,}"

def format_leaderboard(rows, di=""):
    table = get_table()

    print(rows)

    embed = discord.Embed(colour=discord.Colour(0xCC5288))
    # s = "```pascal\n"
    index = 0
    for row in rows:
        # fixed_user = "{0:<15}".format(str(row[1]))
        # fixed_rank = "{0:<3}".format(str(row[0]))
        fixed_user = str(row[1])
        fixed_rank = str(row[0])
        fixed_number_diff = row[3]
        out_of_bounds = row[4]
        if row[3] == None:
            fixed_number_diff = 0

        fixed_number = format_leaderboard_value(row[2], di)
        fixed_number_diff = format_leaderboard_value(fixed_number_diff, di)

        if row[3] == None or row[3] == 0:
            fixed_number_diff = " "

        if (
            di.__contains__("-percentage")
            and di["-percentage"] == "true"
            and not (
                di.__contains__("-o") and (di["-o"] == "completion" or di["-o"] == "%")
            )
        ):
            fixed_number += "%"
            if row[3] != None and row[3] != 0:
                fixed_number_diff += "%"

        table_row = ["#" + fixed_rank, fixed_user]
        # s = s + "#" + fixed_rank + " | " + fixed_user + " | "
        if di.__contains__("-groupby"):
            # s = s + "{0:<7}".format(fixed_number)
            table_row = table_row + [fixed_number]
            fixed_group = format(str(row[5]))
            # if contains "date_trunc" in the groupby, format the date to smallest possible unit
            if "date_trunc" in di["-groupby"]:
                # format is depending on the date_trunc unit (day, month, year, etc.)
                # if the date_trunc unit is "day", format the date to "YYYY-MM-DD"
                if "day" in di["-groupby"]:
                    fixed_group = row[5].strftime("%Y-%m-%d")
                elif "month" in di["-groupby"]:
                    # show as "January 2021" instead of "2021-01"
                    fixed_group = row[5].strftime("%Y %B")
                elif "year" in di["-groupby"]:
                    fixed_group = row[5].strftime("%Y")
            elif "enabled_mods" in di["-groupby"]:
                fixed_group = get_mods_string(row[5])
            # s = s + " | " + fixed_group
            table_row = table_row[:3] + [fixed_group]
        else:
            table_row = table_row[:3] + [fixed_number]

        if not di.__contains__("-no_diff") or di["-no_diff"] == "false":
            table_row = table_row + [fixed_number_diff]

        # check if the next row is out of bounds
        add_divider = False
        next_row = rows[index + 1] if index + 1 < len(rows) else None
        if next_row != None and next_row[4] == 2:
            add_divider = True
        if out_of_bounds == 1:
            add_divider = True

        table.add_row(table_row, divider=add_divider)
        index += 1


    # if no table rows
    s = "```pascal\n"
    if table.rowcount == 0:
        s += "No result\n"
    else:
        s += table.get_string()
    s += "```"

    embed.description = s

    return embed


def format_footer(datasource="", query_execution_time=0, embed_description=""):
    datasource_text = (
        "Scores in the database" if datasource == "scores" else "Profile Stats"
    )
    footer_text = f"Based on {datasource_text} • took {query_execution_time}s"

    lines = embed_description.split("\n")
    if len(lines) > 1:
        text_width = len(max(lines, key=len))
        footer_width = int(len(footer_text) / 3.6)
        if text_width > footer_width:
            difference = text_width - footer_width
            footer_text += "᲼" * difference

    return footer_text
