# RevisedAssignment

# Install Virtual enviornment
sudo pip3 install virtualenv

#create and activate Virtual Environment
virtualenv --python=python3 env
source env/bin/activate

#Install packages using requirment.txt
pip3 install -r requirements.txt

#Create blank DB and Restore existing DB
psql foodcourt < foodcourt.bkp




