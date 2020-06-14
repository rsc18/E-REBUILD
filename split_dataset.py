import sys
import pandas as pd
import random


full_csv = sys.argv[1]
out_train_csv = sys.argv[2]
out_test_csv = sys.argv[3]

df_in = pd.read_csv(full_csv, header=0)

# get the student names
stu_names = df_in.student_name.unique()
random.shuffle(stu_names)

# Do a random 70/30 split
lim = int(0.7 * len(stu_names))
tr_names, te_names = stu_names[:lim], stu_names[lim:]

# Filter out
df_tr = df_in.loc[df_in['student_name'].isin(tr_names)]
df_te = df_in.loc[df_in['student_name'].isin(te_names)]

# Save
df_tr.to_csv(out_train_csv, index=False)
df_te.to_csv(out_test_csv, index=False)
