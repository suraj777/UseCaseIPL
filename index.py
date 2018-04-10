import boto3,json
from boto3.dynamodb.conditions import Key, Attr
def lambda_handler(event, context):
   dynamodb = boto3.resource('dynamodb')
   bidtbl = dynamodb.Table('Bidding')
   matchId=int(event['queryStringParameters']['mid'])

   getLos=''
   usrfault=False
   fmail=[]

   getWin=bidtbl.scan(FilterExpression=Attr('winner').eq('WIN') & Attr('matchId').eq(matchId))
   getWin=getWin['Items']
   # print 'getWin',len(getWin)
   team=''
   for i in range(len(getWin)):
      if getWin != []:
         if team !='':
            if team != getWin[i]['team']:
               return { "statusCode" : 302,"headers": { "Location" : "https://s3.ap-south-1.amazonaws.com/suraj-console/invalidTeam.html"}}
         team=getWin[i]['team']

   if team=='':
      getLos=bidtbl.scan(FilterExpression=Attr('winner').eq('LOS') & Attr('matchId').eq(matchId))
      getLos=getLos['Items']
      if getLos == []:
         return { "statusCode" : 302,"headers": { "Location" : "https://s3.ap-south-1.amazonaws.com/suraj-console/invalidData.html"}}
      else:
         return { "statusCode" : 302,"headers": { "Location" : "https://s3.ap-south-1.amazonaws.com/suraj-console/noAnyWinner.html"}}

   winBid = 0
   response = bidtbl.scan(FilterExpression=Attr('team').eq(team) & Attr('matchId').eq(matchId))
   winers = response['Items']
   for l in winers:
      winBid = winBid + l['bidAmt']

   losBid=0
   resource = bidtbl.scan(FilterExpression=Attr('team').ne(team) & Attr('matchId').eq(matchId))
   losers=resource['Items']
   for ls in losers:
      losBid = losBid + ls['bidAmt']

   usrtbl=dynamodb.Table('BidderReg')

   flag=False
   for l in range(len(winers)):
      winshare=winers[l]['bidAmt']/winBid
      mail = winers[l]['emailId']
      bidAmt=winshare*losBid+winers[l]['bidAmt']
      userinfo = usrtbl.query(KeyConditionExpression=Key('EmailID').eq(mail))
      user=userinfo['Items']
      if user == []:
         usrfault=True
         fmail.append(mail)
      else:
         for i in range(len(user)):
            bal=user[i]['Amt']
            user[i]['Amt']=bal+int(bidAmt)
            usrtbl.put_item(Item=user[i])
            flag=True

   if usrfault:
      return { "statusCode" : 302,"headers": { "Location" : "https://s3.ap-south-1.amazonaws.com/suraj-console/invalidUser.html?fmail="+str(fmail)}}
   elif flag:
      return { "statusCode" : 302,"headers": { "Location" : "https://s3.ap-south-1.amazonaws.com/divyaranitraining/success.html"}}
   else:
      return { "statusCode" : 302,"headers": { "Location" : "https://s3.ap-south-1.amazonaws.com/divyaranitraining/biddingpage.html" }}
