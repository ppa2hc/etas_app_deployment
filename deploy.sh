# example: ./deploy.sh 49 dreamKIT-23042261

defaultAppFolder=/var/etas/vrte/export/49/sdv/In-Vehicle-Software/sdvapi/vehicle_apps

target_vm=$1 
kit_id=$3
execType="cpp"
appName=$2
appFullPath=$defaultAppFolder/$appName/build/$appName
codeFullPath=$defaultAppFolder/$appName/src/main.cpp
codeName=$(basename ${codeFullPath})

echo ""
echo ""
echo "=========================================================="
echo "=================== Build Your Platform==================="
echo "=========================================================="
cd /var/etas/vrte/export/49/sdv/In-Vehicle-Software/sdvapi/ara-com-provider
./run.sh $target_vm

echo ""
echo ""
echo "=========================================================="
echo "=================== Build Your App ======================="
echo "=========================================================="
cd $defaultAppFolder/$appName
./run.sh

echo ""
echo ""
echo "=========================================================="
echo "=================== Deploy Your App ======================"
echo "=========================================================="
cd /home/developer/workspace/dreamkit/dk-manager/etas_app_deployment
node main.js $kit_id $execType $appName $appFullPath $codeName $codeFullPath
