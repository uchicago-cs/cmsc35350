import os
import sys
import glob
from txtai.pipeline import Textractor

textractor = Textractor()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        dir = sys.argv[1]
    else:
        print("Please provide a prefix")
        exit(1)

print(f'Extracting text from PDFs in {dir}/papers')

for pdf_file in glob.glob(f'{dir}/papers/*.pdf'):
    text = textractor(pdf_file)
    base = os.path.splitext(pdf_file)[0]
    outfile = f'{base}.txt'
    print('Writing', outfile)

    with open(outfile, 'w') as file:
        file.write(text)
