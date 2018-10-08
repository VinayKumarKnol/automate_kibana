**backup_visualization.py**  
**Purpose**: This script will be used in order to take the backup of kibana visualizations present on 
a _particular DC/OS cluster_ and belonging to a _particular environment_

```
  python backup_visualization.py \ 
 -u saturn \
  -b templates/meta_backup_temp.j2 \
  -e blue \
   -m blue
```   

**Options Used:**
1. `-u`: Used to tell the DC/OS cluster from where we are taking backup from.
2. `-b`: Since we are generating metadata which we will use later so we have to tell the location of that template file
 in which the data retrieved will be put together to form the metadata of a visualization.
 This metadata can be used later with `create_visual.py` script.
3. `-e`: We need to tell the name of the environment(blue, green, beige) relating to which we need our visuals from.
4. `-m` : We can modify the same backed up visualisations for a different environment on-the-fly using this option.
example: If you want to convert blue visuals to green visuals then do this:
```
  python backup_visualization.py \ 
 -u saturn \
  -b templates/meta_backup_temp.j2 \
  -e blue \
   -m green
```

_If you do not want any changes keep -e and -m to the targeted environment._ 

**Note: We have to include the environment name (blue, green, beige) in the title of the visualizations.**

**Result:** Your backup file will be created with the name `backup_file_<date the script was triggered>_<time it was triggered>.yaml`
This file has the metadata required.

