#!/bin/bash
requestName=$1
seq=$2

# Submit request
response1=`curl -s -X POST http://tara-oceans.mio.osupytheas.fr/ocean-gene-atlas_dev/api/submit \
-H "Accept: application/json"  \
-H "Content-Type: application/json"  \
-d "{\"job_title\":\"$requestName\",\"option\":\"seq\",\"seq\": \"$seq\",\"tool\":\"blastp\",\"threshold\" : \"1e-80\",\"db\":\"OM-RGC_v1\",\"normalize\":\"pertotal\"}"`

# Print response
echo "Response submitted"
echo "$response1"

# Check status, kill script if not successful
status=`echo $response1 | sed -n 's/.*status\":\"\([0-9]*\)\",.*/\1/p'`
# if error, end of execution
if [ $status != "200" ]
then
    echo "error in response 1"
    exit 
fi
echo "Status Passed"

# Parse out the estimated time to completion and the request id
eta=`echo $response1 | sed -n 's/.*eta\":\([0-9]*\),.*/\1/p'`
uniqid=`echo $response1 | sed -n 's/.*uniqid\":\"\([0-9a-zA-Z]*\)\".*/\1/p'`
# Wait for search to complete
sleep $eta
sleep 30

# Request to check results
response2=`curl -s -X POST http://tara-oceans.mio.osupytheas.fr/ocean-gene-atlas_dev/api/checkResults \
-H "Accept: application/json"  \
-H "Content-Type: application/json"  \
-d "{\"uniqid\":\"$uniqid\"}"`

# Print response
echo "Check submitted"
echo "$response2"

# Parse out the URL of the result page
url=`echo $response2|sed -n 's/.*url\":\"\([-a-z:\\\/\.\_\?\=0-9]*\).*/\1/p'`
url2=`echo $url|tr -d '\\'`

# Print the url to the results
echo "The answer page is accessible to : $url2"

# Check status, kill script if not successful
status=`echo $response2 | sed -n 's/.*status\":\"\([0-9]*\)\",.*/\1/p'`
# if error, end of execution
if [ $status != "200" ]
then
    echo "error in response 2"
    exit 
fi
echo "Status passed"

# Create a directory "../TARAOcean_output/"${requestName}"_"${uniqid}

dir="../TARAOcean_input/raw/"${requestName}"_"${uniqid}
mkdir $dir

# Download result files
# Alignment result
curl -s -X POST http://tara-oceans.mio.osupytheas.fr/ocean-gene-atlas_dev/api/fetchResults \
-H "Accept: application/json"  \
-H "Content-Type: application/json"  \
-d "{\"uniqid\":\"$uniqid\",\"file\":\"alignment result\"}" > $dir/fileresult

# Abundances & environmental data
curl -s -X POST http://tara-oceans.mio.osupytheas.fr/ocean-gene-atlas_dev/api/fetchResults \
-H "Accept: application/json"  \
-H "Content-Type: application/json"  \
-d "{\"uniqid\":\"$uniqid\",\"file\":\"abundances & environmental data\"}" > $dir/abun_enviro_data.zip

exit