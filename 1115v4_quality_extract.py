import sys

def extract_number_from_fasta_header(header):
    # 提取fasta标题行中大于号与.之间的数值
    start_index = header.find('>') + 1
    end_index = header.find('.', start_index)
    number = header[start_index:end_index]
    return number

def extract_number_from_fastq_header(header):
    # 提取fastq标题行中@与空格之间的数值
    start_index = header.find('@') + 1
    end_index = header.find(' ', start_index)
    number = header[start_index:end_index]
    return number

def compare_and_output(fasta_file, fastq_file):
    fasta_data = {}
    output_file_name = fasta_file.split('.')[0] + '.txt'

    # 读取fasta文件
    with open(fasta_file, 'r') as fasta:
        current_number = None
        current_sequences = []

        for line in fasta:
            if line.startswith('>'):
                if current_number:
                    fasta_data[current_number] = current_sequences
                    current_sequences = []

                header = line.strip()
                current_number = extract_number_from_fasta_header(header)

            else:
                sequence = line.strip()
                current_sequences.append(sequence)

        if current_number:
            fasta_data[current_number] = current_sequences

    # 比对fastq文件
    with open(fastq_file, 'r') as fastq, open(output_file_name, 'w') as output:

        for i in range(3):
            next(fastq)  # 跳过前三行

        for i, line in enumerate(fastq):
            current_lines.append(line)

            if i % 4 == 0:
                if current_number and current_number in fasta_data:

                    for j, line in enumerate(current_lines):
                        if j >= 3:  # 只写入从第四行开始
                            output.write(line)

                header = line.strip()
                current_number = extract_number_from_fastq_header(header)
                current_lines = []

    比对fastq文件
    with open(fastq_file, 'r') as fastq, open(output_file_name, 'w') as output:
        current_number = None
        current_lines = []

        for i, line in enumerate(fastq):
            current_lines.append(line)

            if i % 4 == 0:
                if current_number and current_number in fasta_data:
                    output.writelines(current_lines)

                header = line.strip()
                current_number = extract_number_from_fastq_header(header)
                current_lines = []

        if current_number and current_number in fasta_data:
            output.writelines(current_lines)
            
    with open(output_file_name, 'r+') as f:

        lines = f.readlines()

        f.seek(0)
        f.truncate()

        for line in lines[3:]:
            f.write(line)

    f.close()
    print("Output file generated: ", output_file_name)


# 解析命令行参数
if len(sys.argv) != 3:
    print("Usage: python script.py fasta_file fastq_file")
    sys.exit(1)

fasta_file = sys.argv[1]
fastq_file = sys.argv[2]

# 调用函数处理文件
compare_and_output(fasta_file, fastq_file)