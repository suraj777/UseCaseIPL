import boto3,json
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):

   dynamodb = boto3.resource('dynamodb')
   bidtbl = dynamodb.Table('Bidding')
   response = bidtbl.scan(FilterExpression=Attr('team').eq('MI') & Attr('matchId').eq(100))
   items = response['Items']

   winBid = 0
   count=0
   for l in items:
      winBid = winBid + l['bidAmt']
      count=+1

   losBid=0
   resource = bidtbl.scan(FilterExpression=Attr('team').ne("MI") & Attr('matchId').eq(100))
   losers=resource["Items"]

   for ls in losers:
      losBid = losBid + ls['bidAmt']

   usrtbl=dynamodb.Table('UserRegistration')
   print len(items)
   for l in range(len(items)):
      winshare=items[l]['bidAmt']/winBid
      mail = items[l]['emailId']
      bidAmt=winshare*losBid+items[l]['bidAmt']
      userinfo = usrtbl.query(KeyConditionExpression=Key('emailId').eq(mail))
      user=userinfo['Items']
      print str(l),user
      for i in range(len(user)):
         bal=user[i]['balance']
         user[i]['balance']=bal+int(bidAmt)
         usrtbl.put_item(Item=user[i])
         print user
   return 'Successful'
