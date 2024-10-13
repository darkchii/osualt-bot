import datetime
import discord
from utils.helpers import (
    get_mods_string,
)

def format_td(seconds, digits=3):
    isec, fsec = divmod(round(seconds * 10**digits), 10**digits)
    return f"{datetime.timedelta(seconds=isec)}.{fsec:0{digits}.0f}"


def format_leaderboard(rows, di=""):
    embed = discord.Embed(colour=discord.Colour(0xCC5288))
    s = "```pascal\n"
    for row in rows:
        fixed_user = "{0:<15}".format(str(row[1]))
        fixed_rank = "{0:<3}".format(str(row[0]))
        if row[2] == None:
            fixed_number = "0"
        elif isinstance(row[2], datetime.datetime):
            fixed_number = str(row[2])
        elif di.__contains__("-o") and (
            di["-o"] == "completion"
            or di["-o"] == "%"
            or di["-o"] == "length_completion"
        ):
            fixed_number = str(row[2]) + "%"
        elif di.__contains__("-o") and (
            "length" in di["-o"] and "score" not in di["-o"]
        ):
            # days = int(row[2])//(3600*24)
            # hours = (int(row[2]) // 3600) % 24
            # minutes = (int(row[2]) // 60) % 60
            # fixed_number = str(days) + "d" + str(hours) + "h" + str(minutes) + "m"
            fixed_number = format_td(row[2], 3)
            split_number = fixed_number.split(".")
            if int(split_number[1]) == 0:
                fixed_number = split_number[0]
        elif di.__contains__("-formattime") and di["-formattime"] == "true":
            hours = int(row[2] / 3600)
            minutes = int(row[2] / 60) % 60
            seconds = int(row[2]) % 60
            fixed_number = str(hours) + "h " + str(minutes) + "m " + str(seconds) + "s"
        elif di.__contains__("-float") and di["-float"] == "true":
            if di.__contains__("-precision"):
                precision = (
                    5 if not di["-precision"].isnumeric() else int(di["-precision"])
                )
                fixed_number = f"{float(row[2]):,.{precision}f}"
            else:
                fixed_number = f"{float(row[2]):,.2f}"
        elif di.__contains__("-float") and di["-float"] == "false":
            fixed_number = f"{int(row[2]):,}"
        elif di.__contains__("-o") and "." in str(row[2]):
            fixed_number = f"{float(row[2]):,.2f}"
        else:
            fixed_number = f"{int(row[2]):,}"

        if (
            di.__contains__("-percentage")
            and di["-percentage"] == "true"
            and not (
                di.__contains__("-o") and (di["-o"] == "completion" or di["-o"] == "%")
            )
        ):
            fixed_number += "%"

        s = s + "#" + fixed_rank + " | " + fixed_user + " | "
        if di.__contains__("-groupby"):
            s = s + "{0:<7}".format(fixed_number)
            fixed_group = "{0:<15}".format(str(row[3]))
            # if contains "date_trunc" in the groupby, format the date to smallest possible unit
            if "date_trunc" in di["-groupby"]:
                # format is depending on the date_trunc unit (day, month, year, etc.)
                # if the date_trunc unit is "day", format the date to "YYYY-MM-DD"
                if "day" in di["-groupby"]:
                    fixed_group = row[3].strftime("%Y-%m-%d")
                elif "month" in di["-groupby"]:
                    # show as "January 2021" instead of "2021-01"
                    fixed_group = row[3].strftime("%Y %B")
                elif "year" in di["-groupby"]:
                    fixed_group = row[3].strftime("%Y")
            elif "enabled_mods" in di["-groupby"]:
                fixed_group = get_mods_string(row[3])
            s = s + " | " + fixed_group
        else:
            s = s + fixed_number
        s = s + "\n"

    if s == "```pascal\n":
        s += "No result\n"
    embed.description = s + "```"

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
