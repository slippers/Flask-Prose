
curl \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -X POST \
    -d '{"email":"test@example.com", "password":"test123"}' \
    -o 'login.json' \
    http://127.0.0.1:5000/login

token=`jq -r '.response.user.authentication_token' login.json`
echo $token

read -rsp $'Press any key to continue...\n' -n1 key

curl -v -i -X POST \
    -H "Content-Type: multipart/form-data" \
    -H "Authentication-Token:$token" \
    -F "label=shatit" \
    -F "file=@shatit" \
    http://127.0.0.1:5000/v1/corpora

read -rsp $'Press any key to continue...\n' -n1 key

curl -v -i -X GET \
    -H "Content-Type: multipart/form-data" \
    -H "Authentication-Token:$token" \
    http://127.0.0.1:5000/v1/corpora


read -rsp $'Press any key to continue...\n' -n1 key


curl -v -i -X DELETE \
    -H "Content-Type: multipart/form-data" \
    -H "Authentication-Token:$token" \
    http://127.0.0.1:5000/v1/corpora/1

