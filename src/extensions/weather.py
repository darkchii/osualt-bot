from discord.ext import commands
import discord
from utils.weather import getWeatherData
from datetime import datetime, timezone, timedelta

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def weather(self, ctx, *args):
        """Command to show weather information for a given location."""
        if not args:
            await ctx.reply("Please specify a location.")
            return
        location = " ".join(args)
        data = await getWeatherData(location)
        # just sent it as a string for now, in a code block
        if data:
            #convert data['dt'] (unix number) to the local time (HH:MM), don't use discord.utils.format_dt, we need to show the actual local time value
            #timezone = data['timezone]
            local_time = datetime.fromtimestamp(data['dt'], tz=timezone.utc) + timedelta(seconds=data['timezone'])
            local_time = local_time.strftime("%H:%M")
            country_flag = data.get('country_emoji', '')
            # round values to 2 decimal places
            temp_c = round(data['temperature_c'], 2)
            temp_f = round(data['temperature_f'], 2)
            heat_index_c = round(data['heat_index_c'], 2) if data['heat_index_c'] is not None else None
            heat_index_f = round(data['heat_index_f'], 2) if data['heat_index_f'] is not None else None
            wind_kmh = round(data['wind_speed_kmh'], 1)
            wind_mph = round(data['wind_speed_mph'], 1)

            air_quality_str = f"{data['air_quality_label']} (AQI: {data['air_quality']})" if data['air_quality'] is not None else "N/A"
            if data['bad_air_quality_components']:
                air_quality_str += "\nHigh amounts of "
                air_quality_str += ", ".join(data['bad_air_quality_components'])

            embed = discord.Embed(
                title=f"Weather in {data['location']} at {local_time} {country_flag}",
                color=0xa8327f,
            )
            embed.add_field(name="Conditions", value=f"**{data['description']}** at **{temp_c}°C** / **{temp_f}°F**", inline=False)
            embed.add_field(name="Feels Like", value= f"**{heat_index_c}°C**, **{heat_index_f}°F**" if heat_index_c is not None else "N/A", inline=True )
            embed.add_field(name="Humidity", value=f"{data['humidity']}%", inline=True)
            embed.add_field(name="Wind", value=f"**{wind_kmh} km/h**, **{wind_mph} mph** from **{data['wind_direction']}**", inline=False)
            embed.add_field(name="Air Quality", value=air_quality_str, inline=True)
            embed.add_field(name="Pressure", value=f"{data['pressure']} hPa", inline=True)

            if data['alerts']:
                alert_messages = []
                for alert in data['alerts']:
                    # show times using discords time formatting (in x hours)
                    alert_messages.append(f"{alert.get('emoji', '')} **{alert['event']}** from <t:{alert['start']}:R> to <t:{alert['end']}:R>")
                embed.add_field(name="Alerts", value="\n".join(alert_messages), inline=False)

            if data['icon']:
                embed.set_thumbnail(
                    url=f"https://openweathermap.org/img/wn/{data['icon']}@2x.png"
                )
            await ctx.reply(embed=embed)
        else:
            await ctx.reply("Could not retrieve weather data for the specified location.")

async def setup(bot):
    await bot.add_cog(Weather(bot))
