from hashlib import md5
password = 'qCjWmsEH20mktZHcwGvXb3vaxvPMprLv'
nonce = '0356ea975ebc9d062129c99c23b1a614f1973003ffe9c3f2ae6f8ef26213a176'
D = {'nonce': nonce,
     'password': '*' * len(password),
     'hashpassword': md5((password + nonce).encode('utf-8')).hexdigest(),
     'Continue': 'Continue'}
print(D)
