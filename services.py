
from flask import Flask, request, jsonify ,redirect, url_for
import boto3
from botocore.exceptions import ClientError
import os

import json
app = Flask(__name__)
@app.route('/')
def index():
    return "welcome to aws_webservices"


''' /listec2 route return the list of all ec2 instance and their id, state, instance_type, ami_id which is on the aws server  '''
@app.route('/listec2')
def list_ec2():
    ec2 = boto3.resource('ec2',region_name='us-east-1',aws_access_key_id=os.getenv("ACCESS_ID"),
         aws_secret_access_key= os.getenv("ACCESS_KEY"))
    instances = ec2.instances.all()
    ec2Instances = []
    
    for instance in instances:
        ec2Instance = {
        "id":instance.id , 
        "instance_type":instance.instance_type,
        "public_ip_address":instance.public_ip_address,
        "state":instance.state
        }

        ec2Instances.append(ec2Instance)

    return json.dumps(ec2Instances)




''' /lists3 route returns the name of all s3 bucket created on aws server in a list '''
@app.route('/lists3')
def list_s3():
    s3 = boto3.resource('s3',region_name='us-east-1',aws_access_key_id=os.getenv("ACCESS_ID"),
         aws_secret_access_key= os.getenv("ACCESS_KEY"))
    buckets = s3.buckets.all()
    print(os.getenv("ACCESS_ID"))
    
    bucketlist = []
    for bucket in buckets:
        bucketlist.append(bucket.name)
    return json.dumps(bucketlist)


''' /creates3 route create s3 bucket with the name provided by post method'''
@app.route('/creates3',methods=['POST'])
def create_s3():
    if request.method == 'POST':
        # print('hello')
        # bucketName = request.form['bucketName']
        # bucketRegion = request.form['bucketLocation']

        bucketData = request.get_json()
        print(bucketData)
        bucketName = bucketData.get('bucketName')
        bucketRegion = bucketData.get('bucketLocation')

        try:
            s3 = boto3.resource('s3',region_name=bucketRegion,aws_access_key_id=os.getenv("ACCESS_ID"),
         aws_secret_access_key= os.getenv("ACCESS_KEY"))
            s3.create_bucket(Bucket=bucketName)
        except ClientError as e:
            print(e)

    return redirect(url_for('list_s3'))


''' /createec2 route  create ec2 instance with specification provided by user in the post method '''
@app.route('/createec2',methods=['POST'])
def createec2():
    if request.method=='POST':
        # ImageId = request.form['ImageId']
        # MinCount = int(request.form['MinCount'])
        # MaxCount = int(request.form['MaxCount'])
        # InstanceType = request.form['InstanceType']

        ec2Instance = request.get_json()
        ImageId = ec2Instance.get('ImageId')
        MinCount = ec2Instance.get('MinCount')
        MaxCount = ec2Instance.get('MaxCount')
        InstanceType = ec2Instance.get('InstanceType')


        ec2 = boto3.resource('ec2',aws_access_key_id=os.getenv("ACCESS_ID"),
         aws_secret_access_key= os.getenv("ACCESS_KEY"))
        instance = ec2.create_instances(
        ImageId=ImageId,
        MinCount=MinCount,
        MaxCount=MaxCount,
        InstanceType=InstanceType,
    )
    return redirect(url_for('list_ec2'))


''' /listdynamodbtable route list all the dynamodb table which is created on aws server'''
@app.route('/listdynamodbtable')
def listDynamoDbTable():
    dynamodb = boto3.resource('dynamodb',aws_access_key_id=os.getenv("ACCESS_ID"),
         aws_secret_access_key= os.getenv("ACCESS_KEY"))
    dynamodbTable = dynamodb.tables.all()
    tablelist = []

    for table in dynamodbTable:
        tablelist.append(table.name)

    return json.dumps(tablelist)
   

''' /createdynamodbtable route create table with detail provided by user in the post method'''
@app.route('/createdynamodbtable',methods = ['POST'])
def createDynamoDbTable():

    tableData = request.get_json()

    dynamodb = boto3.resource('dynamodb', region_name=tableData.get('region_name'),aws_access_key_id=os.getenv("ACCESS_ID"),
         aws_secret_access_key= os.getenv("ACCESS_KEY"))
    print(tableData.get('KeySchema'))
    print(tableData.get('AttributeDefinitions'))
    
    
    table = dynamodb.create_table(
        TableName = tableData.get('TableName'),
        KeySchema = tableData.get('KeySchema'),
        AttributeDefinitions = tableData.get('AttributeDefinitions'),
        ProvisionedThroughput = tableData.get('ProvisionedThroughput')

    )

    return redirect(url_for('listDynamoDbTable'))

@app.route('/deletedynamodbtable/<table>',methods = ['DELETE'])
def deleteDynamoDbTable(table):
   
    try:
        dynamodb = boto3.resource('dynamodb',aws_access_key_id=os.getenv("ACCESS_ID"),
         aws_secret_access_key= os.getenv("ACCESS_KEY"))
        table = dynamodb.Table(table)
        table.delete()
        return ('',204)
    except ClientError as e:
        print(e)

    return ('',204)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
