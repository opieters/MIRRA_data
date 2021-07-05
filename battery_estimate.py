# tested on Python 3.9

if __name__ == "__main__":
    table_sensor = {
        "deep sleep": 49e-6,
        "normal operation": 30e-3,
        "LoRa TX": 44e-3,
        "LoRa RX": 8e-3,
    }

    table_gateway = {
        "deep sleep": 56e-6,
        "normal operation": 35e-3,
        "LoRa TX": 45e-3,
        "LoRa RX": 9e-3,
        "2G stand-by": 47e-3,
        "2G comm": 475e-3,
    }

    total_consumption_sensor_24h = \
        (24*60*60-5-1-8*24*3)*table_sensor["deep sleep"] \
        + 8*table_sensor["normal operation"]*24*3 \
        + 1*table_sensor["LoRa TX"] \
        + 5*table_sensor["LoRa RX"]
    print(total_consumption_sensor_24h)

    total_consumption_sensor_avg = total_consumption_sensor_24h / (60*60*24)
    print(f"Average power consumption: {total_consumption_sensor_avg:}")

    print("Battery OK days sensor node:", 2.6/total_consumption_sensor_avg/24)

    nnodes = 1
    total_consumption_gateway_24h = \
        (24*60*60 - nnodes - (nnodes*10+10) - 20)*table_gateway["deep sleep"] \
        + nnodes*1*table_gateway["LoRa TX"] \
        + (nnodes*10+10)*table_gateway["LoRa RX"] \
        + 20*table_gateway["normal operation"] \

    total_consumption_gateway_avg = total_consumption_gateway_24h / (60*60*24)

    print("Battery OK days gateway:", 2.6 * 2/ total_consumption_gateway_avg / 24)
    print("Battery OK days gateway:", 2.6 / total_consumption_gateway_avg / 24)

    total_consumption_gateway_24h = \
        68 * table_gateway["2G stand-by"] \
        + 32 * table_gateway["2G comm"]

    total_consumption_gateway_avg = total_consumption_gateway_24h / (60 * 60 * 24)
    print(total_consumption_gateway_avg/24)

    print("Battery OK days gateway:", 10 / total_consumption_gateway_avg / 24)

    C = 10
    n_months = 1
    while C > 0:
        C -= total_consumption_gateway_avg * 24 * 31
        C = C * 0.98
        n_months += 1

    print(f"With capacity correction: {n_months}")