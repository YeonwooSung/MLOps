# check dvc version
dvc --version

# make new drive
mkdir ./basic
# cd into new drive
cd ./basic

# init git and dvc
git init
dvc init

# create data directory
mkdir data
cd data
echo "hello world" > demo.txt
cd ..

# set up gdrive as dvc remote
dvc remote add -d storage gdrive://<GOOGLE_DRIVE_FOLDER_ID>

# commit data to git
git add data/demo.txt
git commit -m "add data"

# add data to dvc
git add .dvc/config
git commit -m "add remote storage"
dvc push
