**create_dash.py**  
**Purpose**: This script will create dashboards on  
a _particular DC/OS cluster_ and using the meta file given during the triggering of this script.

```
  python create_dash.py \
  -c config/dash_config.yaml \
  -tc templates/template_dashboard.j2 \
  -u saturn \
  -e blue
```   

**Options Used:**
1. `-c`: Used to tell the configuration to use with the script.
2. `-tc`: We have templates to generate the dashboards json, we will specify the template upon which the meta data will substitute itself.
3. `-u`: Here we tell the cluster's name, Kibana of which we are targetting.
4. `-e`: Here we tell the environment for which we need the dashboard of.

_Note: Check your `id` in the metadata file you have provided.
Check that visual ids are correct and existing in the kibana you are targetting._

**Result:** Check the logs of this script to know the status of the dashboards.

**Logs**: `logs/dashboard_logs.log`

