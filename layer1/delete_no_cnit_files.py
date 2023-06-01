# Run this scritp to delete non cnit json files >> to reduce the space occupations

import os 
print(os.getcwd())
if "data_ue_paths" in os.listdir():
    os.chdir(os.getcwd()+"/data_ue_paths")
    for sub_dirs1 in os.listdir():
        # print("=====================1",sub_dirs1)
        for sub_dir2 in os.listdir(sub_dirs1):
            if "ue_" not in sub_dir2:
                pass
            else:
                # print("=====================2",sub_dir2)

                for file_ in os.listdir(os.getcwd()+"/"+sub_dirs1+"/"+sub_dir2):
                    # print("===================3",file_)
                    if file_.split("_")[-1] != "cnit.json":
                        # print("=============4",type(file_),file_)
                        # try:
                        os.remove(os.getcwd()+"/"+sub_dirs1+"/"+sub_dir2+"/"+file_)
                        # except:
                        #     continue
# # os.chdir(os.getcwd()+"/data_ue_paths")
# # print(os.listdir())
# os.remove("test.txt")
