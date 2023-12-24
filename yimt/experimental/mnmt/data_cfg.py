

weights_csv = r"D:\dataset\mnmt\weights-1.5.csv"

conf = []
with open(weights_csv, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        parts = line.split(",")
        conf.append((parts[0], parts[3]))

with open("data.yml", "w", encoding="utf-8") as out:
    out.write("data:\n")
    out.write("  train_features_file:\n")
    for i in range(len(conf)):
        out.write("    - " + conf[i][0] + "\n")

    out.write("  train_labels_file:\n")
    for i in range(len(conf)):
        out.write("    - {:.4f}\n".format(float(conf[i][1])))
