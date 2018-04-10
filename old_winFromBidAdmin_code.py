import boto3,json
from boto3.dynamodb.conditions import Key, Attr
def lambda_handler(event, context):
   dynamodb = boto3.resource('dynamodb')
   bidtbl = dynamodb.Table('Bidding')
   matchId=int(event['queryStringParameters']['mid'])

   getWin=bidtbl.scan(FilterExpression=Attr('winner').eq('WIN') & Attr('matchId').eq(matchId))
   getWin=getWin['Items']
   print 'getWin',len(getWin)
   team=''
   for i in range(len(getWin)):
      team=getWin[i]['team']
   response = bidtbl.scan(FilterExpression=Attr('team').eq(team) & Attr('matchId').eq(matchId))
   items = response['Items']
   winBid = 0
   for l in items:
      winBid = winBid + l['bidAmt']
   losBid=0
   resource = bidtbl.scan(FilterExpression=Attr('team').ne(team) & Attr('matchId').eq(matchId))
   losers=resource['Items']
   for ls in losers:
      losBid = losBid + ls['bidAmt']
   usrtbl=dynamodb.Table('BidderReg')

   flag=False
   for l in range(len(items)):
      winshare=items[l]['bidAmt']/winBid
      mail = items[l]['EmailID']
      bidAmt=winshare*losBid+items[l]['bidAmt']
      userinfo = usrtbl.query(KeyConditionExpression=Key('EmailID').eq(mail))
      user=userinfo['Items']
      for i in range(len(user)):
         bal=user[i]['Amt']
         user[i]['Amt']=bal+int(bidAmt)
         usrtbl.put_item(Item=user[i])
         flag=True
   if flag:
      return { "statusCode" : 302,"headers": { "Location" : "https://s3.ap-south-1.amazonaws.com/divyaranitraining/success.html"}}
   else:
      return { "statusCode" : 302,"headers": { "Location" : "https://s3.ap-south-1.amazonaws.com/divyaranitraining/biddingpage.html" }}
