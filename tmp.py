from pathlib import Path
import datetime as dt
import random


root = Path("demos/demo_data")

start = dt.date(2026, 1, 1)
for i in range(365):
    if random.random() < 0.9:
        continue

    date = start + dt.timedelta(i)

    for j in range(4):
        if random.random() < 0.7:
            continue
        file_name = date.strftime(f"%Y_%m_%d_{j}.txt")

        path = root / file_name
        with path.open("w") as file:
            file.write(
                "Demonstration file for the file count demo.\n"
                f"{date} file number {j}."
            )