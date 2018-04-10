import boto3,json
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):

   dynamodb = boto3.resource('dynamodb')
   bidtbl = dynamodb.Table('Bidding')

#
   matchId=event['queryStringParameters']['mid']
   getWin=bidtbl.scan(FilterExpression=Attr('winner').eq('WIN') & Attr().eq(matchId)
   getWin=getWin['Items']
   team=getWin[0]['team']

#
   response = bidtbl.scan(FilterExpression=Attr('team').eq(team) & Attr('matchId').eq(matchId))
   items = response['Items']

   winBid = 0
   count=0
   for l in items:
      winBid = winBid + l['bidAmt']
      print 'winBid',winBid
      count=+1

   losBid=0
   resource = bidtbl.scan(FilterExpression=Attr('team').ne(team) & Attr('matchId').eq(matchId))
   losers=resource["Items"]

   for ls in losers:
      losBid = losBid + ls['bidAmt']
      print losBid

   usrtbl=dynamodb.Table('UserRegistration')
   print len(items)
   for l in range(len(items)):
      winshare=items[l]['bidAmt']/winBid
      print winshare
      mail = items[l]['emailId']
      print mail
      bidAmt=winshare*losBid#+items[l]['bidAmt']
      print 'bidAmt',bidAmt
      userinfo = usrtbl.query(KeyConditionExpression=Key('emailId').eq(mail))
      user=userinfo['Items']
      for i in range(len(user)):
         bal=user[i]['balance']
         user[i]['balance']=bal+int(bidAmt)
         usrtbl.put_item(Item=user[i])
   return 'Successful'
