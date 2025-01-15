#!/bin/bash
set -e

echo "This is setup-ckan.bash..."

echo "Installing the packages that CKAN requires..."
sudo apt-get update -qq
sudo apt-get install xmlsec1 libxmlsec1-dev

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/ckan/ckan
cd ckan

CKAN_TAG=$(git tag | grep ^ckan-$CKANVERSION | sort --version-sort | tail -n 1)
git checkout $CKAN_TAG
echo "CKAN version: ${CKAN_TAG#ckan-}"

pip install -r requirements.txt
pip install -r dev-requirements.txt
pip install -e .

cd -

echo "Creating the PostgreSQL user and database..."
psql -h localhost -U postgres -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
psql -h localhost -U postgres -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'

echo "Initialising the database..."
cd ckan
ckan -c test-core.ini db init
cd -

echo "Installing saml2 requirements..."
pip install -r dev-requirements.txt
echo "Installing ckanext-saml2auth..."
pip install -e .

echo "setup-ckan.bash is done."
