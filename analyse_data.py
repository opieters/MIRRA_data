import pandas as pd
import numpy as np
from scipy.stats import pearsonr, ttest_ind
import matplotlib.pyplot as plt

# tested on Python 3.9
# package versions:
# pandas==1.2.4
# scipy==1.6.2
# numpy==1.20.1


def per_day_stats_temperature(x, fn, dtype):
    time = x.index.values
    t = np.min(x.index.round("D"))
    if t > np.min(time):
        t -= np.timedelta64(24, "h")
    data = []
    while t < np.max(time):
        mask = (x.index >= (t+np.timedelta64(6, "h"))) & (x.index < (t+np.timedelta64(18, "h")))
        day_trace = x.loc[mask]
        mask = (x.index < (t + np.timedelta64(6, "h"))) | (x.index >= (t + np.timedelta64(18, "h")))
        mask = mask & (x.index >= t) & (x.index < (t + np.timedelta64(24, "h")))
        night_trace = x.loc[mask]

        if dtype == "day":
            if len(day_trace) > 0:
                data.append(fn(day_trace))
        else:
            if len(night_trace) > 0:
                data.append(fn(night_trace))

        t += np.timedelta64(24, "h")

    return data


if __name__ == "__main__":
    df_sensor = pd.read_csv("processed_data/sensor_data.csv")
    df_forest = pd.read_csv("processed_data/forest_data.csv")
    df_open_field = pd.read_csv("processed_data/open_field_data.csv")

    df_sensor.loc[:,"time"] = pd.to_datetime(df_sensor.loc[:,"time"])
    df_sensor = df_sensor.set_index("time")

    df_forest.loc[:, "time"] = pd.to_datetime(df_forest.loc[:, "time"])
    df_forest = df_forest.set_index("time")

    df_open_field.loc[:, "time"] = pd.to_datetime(df_open_field.loc[:, "time"])
    df_open_field = df_open_field.set_index("time")

    for i in ["soil_temperature", "air_temperature"]:
        rho, p = pearsonr(df_sensor[i], df_forest[i])
        print(f"{i} Pearson correlation coefficient: {rho} and p-value: {p}")

        print(ttest_ind(df_sensor[i], df_forest[i]))



    df_merged = pd.DataFrame({
        "light_sensor": df_sensor["light"],
        "light_open_field": df_open_field["light"],
        "soil_temperature_sensor": df_sensor["soil_temperature"],
        "soil_temperature_open_field": df_open_field["soil_temperature"]
    })

    df_merged.dropna(inplace=True)

    for i in ["light", "soil_temperature"]:
        rho, p = pearsonr(df_merged[i+"_sensor"], df_merged[i+"_open_field"])
        print(f"{i} Pearson correlation coefficient: {rho} and p-value: {p}")

        plt.plot(df_merged[i+"_sensor"], label="sensor")
        plt.plot(df_merged[i+"_open_field"], label="open_field")
        plt.legend()
        plt.show()

    df_merged = pd.DataFrame({
        "rh_sensor": df_sensor["rh"],
        "rh_open_field": df_open_field["rh"],
        "air_temperature_sensor": df_sensor["air_temperature"],
        "air_temperature_open_field": df_open_field["air_temperature"]
    })

    df_merged.dropna(inplace=True)

    for i in ["rh", "air_temperature"]:
        rho, p = pearsonr(df_merged[i + "_sensor"], df_merged[i + "_open_field"])
        print(f"{i} Pearson correlation coefficient: {rho} and p-value: {p}")

        plt.plot(df_merged[i + "_sensor"], label="sensor")
        plt.plot(df_merged[i + "_open_field"], label="open_field")
        plt.legend()
        plt.show()

    # compute correlation between reference traces
    df_merged = pd.DataFrame({
        "air_temperature_forest": df_forest["air_temperature"],
        "air_temperature_open_field": df_open_field["air_temperature"]
    })

    df_merged.dropna(inplace=True)

    rho, p = pearsonr(df_merged["air_temperature_forest"], df_merged["air_temperature_open_field"])
    print(f"Pearson correlation of air temperature between forest and open air reference loggers: {rho}")

    # compute correlation between reference traces
    df_merged = pd.DataFrame({
        "soil_temperature_forest": df_forest["soil_temperature"],
        "soil_temperature_open_field": df_open_field["soil_temperature"]
    })

    df_merged.dropna(inplace=True)

    rho, p = pearsonr(df_merged["soil_temperature_forest"], df_merged["soil_temperature_open_field"])
    print(f"Pearson correlation of soil temperature between forest and open air reference loggers: {rho}")

    df_merged = pd.DataFrame({
        "air_temperature_MIRRA": df_sensor["air_temperature"],
        "air_temperature_forest": df_forest["air_temperature"],
        "air_temperature_open_field": df_open_field["air_temperature"],
        "soil_temperature_MIRRA": df_sensor["soil_temperature"],
        "soil_temperature_forest": df_forest["soil_temperature"],
        "soil_temperature_open_field": df_open_field["soil_temperature"],
        "relative_humidity_MIRRA": df_sensor["rh"],
        "relative_humidity_open_field": df_open_field["rh"],
        "light_MIRRA": df_sensor["light"],
        "light_open_field": df_open_field["light"],
    })

    df_merged2 = pd.DataFrame({
        "soil_temperature_MIRRA": df_sensor["soil_temperature"],
        "soil_temperature_forest": df_forest["soil_temperature"],
        "soil_temperature_open_field": df_open_field["soil_temperature"],
        "relative_humidity_MIRRA": df_sensor["rh"],
        "relative_humidity_open_field": df_open_field["rh"],
        "light_MIRRA": df_sensor["light"],
        "light_open_field": df_open_field["light"],
    })

    df_merged.dropna(inplace=True)

    per_day_stats_temperature(df_merged["soil_temperature_MIRRA"], np.min, 'day')


    with open("processed_data/data_statistics.csv", "w") as f:
        f.write("variable, MIRRA, forest, openfield\n")

        data_types = ["MIRRA", "forest", "open_field"]

        for df, varl1, varl2, an, unit in [
            (df_merged, "air temperature", "air_temperature", "$^*$", "\\degreeCelsius"),
            (df_merged2, "soil temperature", "soil_temperature", "", "\\degreeCelsius"),
        ]:
            for fn, l in [
                (np.mean, f"mean {varl1}{an} [\si{{{unit}}}]"),
                (np.std,  f"$\sigma$ {varl1}{an} [\si{{{unit}}}]"),
                (np.min,  f"min {varl1}{an} [\si{{{unit}}}]"),
                (np.max,  f"max {varl1}{an} [\si{{{unit}}}]")
            ]:
                x = [fn(df[f'{varl2}_{i}']) for i in data_types]
                f.write(f"{l}, {x[0]}, {x[1]}, {x[2]}\n")

            for extr, fn in [("min", np.min), ("max", np.max)]:
                for part_of_day in ["day", "night"]:
                    x = [np.mean(per_day_stats_temperature(df[f"{varl2}_{i}"], fn, part_of_day)) for i in data_types]
                    l = f"mean {extr} {part_of_day} {varl1}{an} [\\si{{{unit}}}]"
                    f.write(f"{l}, {x[0]}, {x[1]}, {x[2]}\n")

        data_types = ["MIRRA", "open_field"]

        for df, varl1, varl2, an, unit in [
            (df_merged, "relative humidity", "relative_humidity", "$^*$", "\\percent"),
        ]:
            for fn, l in [
                (np.mean, f"mean {varl1}{an} [\si{{{unit}}}]"),
                (np.std,  f"$\sigma$ {varl1}{an} [\si{{{unit}}}]"),
                (np.min,  f"min {varl1}{an} [\si{{{unit}}}]"),
                (np.max,  f"max {varl1}{an} [\si{{{unit}}}]")
            ]:
                x = [fn(df[f'{varl2}_{i}']) for i in data_types]
                f.write(f"{l}, {x[0]}, , {x[1]}\n")

            for extr, fn in [("min", np.min), ("max", np.max)]:
                for part_of_day in ["day", "night"]:
                    x = [np.mean(per_day_stats_temperature(df[f"{varl2}_{i}"], fn, part_of_day)) for i in data_types]
                    l = f"mean {extr} {part_of_day} {varl1}{an} [\\si{{{unit}}}]"
                    f.write(f"{l}, {x[0]}, , {x[1]}\n")

        for df, varl1, varl2, unit1, unit2 in [
            (df_merged2, "light", "light", "\\lux", "\\watt\\per\\square\\metre\\per\\second"),
        ]:
            for fn, l in [
                (np.mean, f"mean {varl1} [\\si{{{unit1}}} or \\si{{{unit2}}}]"),
                (np.std,  f"$\sigma$ {varl1} [\\si{{{unit1}}} or \\si{{{unit2}}}]"),
                (np.max,  f"max {varl1} [\\si{{{unit1}}} or \\si{{{unit2}}}]")
            ]:
                x = [fn(df[f'{varl2}_{i}']) for i in data_types]
                f.write(f"{l}, {x[0]}, , {x[1]}\n")