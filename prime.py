import base64

num=int(str(base64.b64decode((open('pub.key','r').read())).decode('utf-8')))
print('key:',num/int(open('private.key','r').read()))

