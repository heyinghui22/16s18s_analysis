import sys


# 定义提取序列表段函数
def extract_number(header, start_char, end_char):
    start_index = header.find(start_char) + 1
    end_index = header.find(end_char, start_index)
    return header[start_index:end_index]


def compare_and_output(fasta_file, fastq_file):
    # 读取fasta序列
    fasta_data = {}
    with open(fasta_file) as f:
        current_number = None
        current_sequences = []

        for line in f:
            if line.startswith('>'):
                if current_number:
                    fasta_data[current_number] = current_sequences
                    current_sequences = []

                header = line.strip()
                current_number = extract_number(header, '>', '.')

            else:
                sequence = line.strip()
                current_sequences.append(sequence)

        if current_number:
            fasta_data[current_number] = current_sequences

    # 读取fastq并比对
    output_file = fasta_file.split('.')[0] + '.txt'
    with open(fastq_file) as f1, open(output_file, 'w') as outf:

        current_lines = []
        for i, line in enumerate(f1):

            current_lines.append(line)

            if i % 4 == 0:

                number = extract_number(line, '@', ' ')

                if number in fasta_data:
                    outf.writelines(current_lines)

                current_lines = []

    print('Output file:', output_file)


if __name__ == '__main__':
    fasta_file, fastq_file = sys.argv[1:]
    compare_and_output(fasta_file, fastq_file)