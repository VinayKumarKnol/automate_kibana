**creat_visual.py**  
**Purpose**: This script will create visualisations on  
a _particular DC/OS cluster_ and using the meta file given during the triggering of this script.

```
  python create_visual.py \ 
 -c config/test.yaml \
  -tc templates/template_visualization.j2  \
  -u saturn
```   

**Options Used:**
1. `-c`: Used to tell the configuration to use with the script. We can also use the backed up meta data with it also.
2. `-tc`: We have templates to generate the visualization json, we will specify the template upon which the meta data will substitute itself.
3. `-u`: Here we tell the cluster's name, Kibana of which we are targetting.


**Result:** Check the logs of this script to know the status of the visualizations.

**Logs**: `logs/visual_logs.log`

