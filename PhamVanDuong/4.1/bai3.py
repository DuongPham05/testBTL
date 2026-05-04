with open("demo_file1.txt", "w", encoding="utf-8") as f:
    f.write("Thuc\nhanh\nvoi\nfile\nIO\n")
    with open("demo_file1.txt", "r", encoding="utf-8") as f:
        content = f.read()
        print(content.replace("\n", " "))
        with open("demo_file1.txt", "r", encoding="utf-8") as f:
            for line in f:
                print(line.strip())