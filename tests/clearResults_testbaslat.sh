
#!/bin/bash
echo "TG 5 Clear Results baslatiliyor..."

jmeter -n -t TestPlan-Cont.jmx -p props/TestPlan_TG5.properties
