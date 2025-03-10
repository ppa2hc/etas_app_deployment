# example: ./deploy.sh 49 test_kuksa_client dreamKIT-23042261

defaultAppFolder=/home/developer/workspace/In-Vehicle-Software/sdvapi/vehicle_apps

target_vm=$1 
kit_id=$3
execType="cpp"
appName=$2
appFullPath=$defaultAppFolder/$appName/build/$appName
codeFullPath=$defaultAppFolder/$appName/src/main.cpp
codeName=$(basename ${codeFullPath})

# echo ""
# echo ""
# echo "=========================================================="
# echo "=================== Build Your Platform==================="
# echo "=========================================================="
# cd /home/developer/workspace/In-Vehicle-Software_sk3.4/sdvapi/ara-com-provider
# ./run.sh $target_vm

echo ""
echo ""
echo "=========================================================="
echo "=================== Build Your App ======================="
echo "=========================================================="
cd $defaultAppFolder/$appName
./run.sh

if [ $? -eq 0 ]
then
  echo "Successfully build your app. Let's deploy !!!"
  echo ""
  echo ""
  echo "=========================================================="
  echo "=================== Deploy Your App ======================"
  echo "=========================================================="
  cd /home/developer/workspace/etas_app_deployment
  node main.js $kit_id $execType $appName $appFullPath $codeName $codeFullPath
else
  echo "Error: Could not compile. please check building errors !!!"
fi


