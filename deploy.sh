# example: ./deploy.sh 49 dreamKIT-23042261

target_vm=$1 
kit_id=$2
execType="cpp"
appFullPath=/var/etas/vrte/export/49/vrte/usr/bin/test_kuksa_client
appName=$(basename ${appFullPath})
codeFullPath=/var/etas/vrte/export/49/sdv/In-Vehicle-Software/sdvapi/ara-com-provider/src/test_kuksa_client/main.cpp
codeName=$(basename ${codeFullPath})

echo ""
echo ""
echo "=========================================================="
echo "=================== Build Your App ======================="
echo "=========================================================="
cd /var/etas/vrte/export/49/sdv/In-Vehicle-Software/sdvapi/ara-com-provider
./run.sh $target_vm

echo ""
echo ""
echo "=========================================================="
echo "=================== Deploy Your App ======================"
echo "=========================================================="
cd /home/developer/workspace/etas_app_deployment
node main.js $kit_id $execType $appName $appFullPath $codeName $codeFullPath
