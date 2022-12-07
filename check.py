from psutil import disk_partitions, disk_usage
import smtplib, ssl
from dotenv import dotenv_values
from rich.console import Console
from rich.table import Table
from rich import box
from io import StringIO
import os

currentFolder = os.path.dirname(__file__) + "/"

config = dotenv_values(currentFolder + ".env")
console = Console(file=StringIO())

config["PART_DETECTION_THRESHOLD"] = int(config["PART_DETECTION_THRESHOLD"]) * 1_000_000
config["PART_USAGE_MB_THRESHOLD"] = int(config["PART_USAGE_MB_THRESHOLD"]) * 1_000_000
config["PART_USAGE_POURCENT_THRESHOLD"] = int(config["PART_USAGE_POURCENT_THRESHOLD"])
config["PORT"] = int(config["PORT"])


def prettyFileSize(sizeInByte):
    if sizeInByte < 1000:
        return "%.2f" % sizeInByte + "B"
    sizeInByte /= 1000
    if sizeInByte < 1000:
        return "%.2f" % sizeInByte + "KB"
    sizeInByte /= 1000
    if sizeInByte < 1000:
        return "%.2f" % sizeInByte + "MB"
    sizeInByte /= 1000
    return "%.2f" % sizeInByte + "GB"


def sendEmail(message):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config["SERVER"], config["PORT"], context=context) as server:
        server.login(config["USER"], config["PASSWORD"])
        server.sendmail(config["SENDER_EMAIL"], config["RECEIVER_EMAIL"], message)


partitions = disk_partitions()

table = Table(title="Partitions information", box=box.ASCII)
table.add_column("Filesystem")
table.add_column("Size", justify="right")
table.add_column("Used", justify="right")
table.add_column("Avail", justify="right")
table.add_column("Use%", justify="right")
table.add_column("Mounted on")


thresholdMet = False

for partition in partitions:
    usage = disk_usage(partition.mountpoint)

    # Disgard partitions which are too small in size
    if usage.total < config["PART_DETECTION_THRESHOLD"]:
        continue

    table.add_row(
        partition.device,
        prettyFileSize(usage.total),
        prettyFileSize(usage.used),
        prettyFileSize(usage.free),
        str(usage.percent) + "%",
        partition.mountpoint,
    )

    thresholdMet = thresholdMet or (
        usage.free < config["PART_USAGE_MB_THRESHOLD"]
        or usage.percent > config["PART_USAGE_POURCENT_THRESHOLD"]
    )

if thresholdMet:
    console.print(table)
    tableOutput = console.file.getvalue()

    message = f"""\
From: {config["SENDER_EMAIL"]}
To: {config["RECEIVER_EMAIL"]}
Subject: [{config["HOST_NAME"]}] Partition usage warning!

You received this warning because one of the following partition has either:
  - Less than {prettyFileSize(config["PART_USAGE_MB_THRESHOLD"])} of free storage
  - More than {config["PART_USAGE_POURCENT_THRESHOLD"]}% of usage

Partitions with a total size of less than {prettyFileSize(config["PART_DETECTION_THRESHOLD"])} are omitted.

{tableOutput}
"""

    print(message)
    sendEmail(message)
