# check dvc version
poetry run dvc --version

# make new drive
mkdir ./basic
# cd into new drive
cd ./basic

# init git and dvc
git init
poetry run dvc init

# set up gdrive as dvc remote
# poetry run dvc remote add -d storage gdrive://<GOOGLE_DRIVE_FOLDER_ID>
poetry run dvc remote add -d storage gdrive://1rEmnrQ027VC68su_bF_bFUJphSfka2W9

# create data directory
mkdir data
cd data
echo "hello world" > demo.txt
cd ..

# commit data to git
git add data/demo.txt
git commit -m "add data"

# add data to dvc
git add .dvc/config
git commit -m "add remote storage"
poetry run dvc push
