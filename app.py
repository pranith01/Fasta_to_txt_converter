from flask import Flask, request, render_template, send_from_directory
from tabulate import tabulate
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

def fasta_to_table(filename):
    with open(filename, 'r') as fasta_file:
        sequences = fasta_file.read().split('>')[1:]  # Split the file by '>' to separate sequences

        output_files = []  # List to store the generated file paths

        for i, sequence in enumerate(sequences):
            lines = sequence.split('\n')[:-1]  # Split the sequence into lines and remove the last empty line
            header = lines[0]  # The first line is the sequence header
            sequence = ''.join(lines[1:])  # Concatenate the remaining lines to get the sequence

            # Create a table with SeqID and Sequence columns
            table = [["SeqID", "Sequence"],
                     [header, sequence]]

            # Format the table with lines
            table_formatted = tabulate(table, headers="firstrow", tablefmt="grid")

            # Create a new file with a unique filename for each sequence
            output_filename = f'sequence_{i+1}.txt'

            # Write the formatted table to the new file
            with open(output_filename, 'w') as output_file:
                output_file.write(table_formatted)

            print(f'Converted sequence "{header}" to "{output_filename}"')

            # Append the generated file path to the output_files list
            output_files.append(output_filename)

        # Return the list of generated file paths
        return output_files

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files['file']

        if file and file.filename.endswith('.fasta'):
            filename = secure_filename(file.filename)
            file.save(filename)

            output_files = fasta_to_table(filename)

            # Modify the file paths to include the base URL and file extension
            output_files = [f"{request.base_url}download/{file}" for file in output_files]

            return render_template('index.html', output_files=output_files)

    return render_template('index.html')

@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(os.getcwd(), filename, as_attachment=True)

if __name__ == '__main__':
    app.run()
