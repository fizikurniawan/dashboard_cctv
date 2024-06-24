import io
import csv


def create_csv_file(data):
    fieldnames = data[0].keys()
    output = io.StringIO()

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

    # Convert StringIO to BytesIO
    csv_data = output.getvalue().encode("utf-8")
    bytes_output = io.BytesIO(csv_data)

    return bytes_output
