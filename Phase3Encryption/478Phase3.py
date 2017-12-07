#CECS 478 Phase 3
#Using resources from cryptography.io
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dsa, rsa
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives import padding
padder = padding.PKCS7(256).padder()
unpadder = padding.PKCS7(256).unpadder()
import json

#input is a message string and an RSA public key file path
def Encrypt(message, publicKey):
    backend = default_backend()
    #Load the key
    #access public key with the path
    with open(publicKey, "rb") as key_file:
            RSAPubKey = serialization.load_pem_public_key(key_file.read(), backend = backend)
    
    
    #initialize AES key 256 bits
    AESKey = os.urandom(32)
    #initialize AES IV 128 bits
    iv = os.urandom(16)
    #Construct an AES cipher object with randomly generated AES key
    #and a randomly generated IV
    cipher = Cipher(algorithms.AES(AESKey), modes.CBC(iv), backend = backend)
    AESencryptor = cipher.encryptor()
    
    #Padding is a way to take data that may or may not be a multiple of the 
    #block size for a cipher and extend it out so that it is. This is required 
    #for many block cipher modes as they require the data to be encrypted to be an 
    #exact multiple of the block size.
    from cryptography.hazmat.primitives import padding
    #padding is sometimes required to make a message the correct size
    #must be PKCS7
    padder = padding.PKCS7(128).padder()
    #Set the default string type to UTF8. This
    #is the default for newer OpenSSLs
    message = message.encode('utf-8')
    
    padded_message = padder.update(message)
    padded_message += padder.finalize()
    #AESCipher value is the padded message
    cipherAES= AESencryptor.update(padded_message) + AESencryptor.finalize()
    
    #initialize HMAC key to random 256 bits
    HMACKey = os.urandom(32)
    #generate HMAC tag
    tagHMAC = hmac.HMAC(HMACKey, hashes.SHA256(), backend = default_backend())
    tagHMAC.update(cipherAES)
    #finalize tag
    tag = tagHMAC.finalize()
    
    #concatenate AESKey and HMACKey
    concatenate = AESKey + HMACKey
    from cryptography.hazmat.primitives.asymmetric import padding
    #Encrypt keys with RSA Object aka the Public key
    cipherRSA= RSAPubKey.encrypt(concatenate, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),algorithm=hashes.SHA1(), label=None))
    #return RSA cipther, AES cipher, AES IV, and HMACTag
    jsonObject = {'cipherRSA' : cipherRSA, 'cipherAES' : cipherAES, 'iv' : iv, 'tag' : tag}
    return jsonObject
    #return (cipherRSA, cipherAES, iv, tag)


def DecryptTest(jsonObject, privateKey):
    backend = default_backend()
    #access public key with the path
    with open(privateKey, "rb") as key_file:
            objectRSA = serialization.load_pem_private_key(key_file.read(), password=None, backend = backend)

    #Load private key into RSA object   
    from cryptography.hazmat.primitives.asymmetric import padding
    concatenate = objectRSA.decrypt(jsonObject['cipherRSA'], padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()), algorithm=hashes.SHA1(),label=None))
    #Recover AES key and HMAC key
    AESKey = concatenate[:len(concatenate)//2]
    HMACKey = concatenate[len(concatenate)//2:]
    #run an HMAC(SHA256 with the HMAC key recovered from above
    #regenerate a new tag
    tagUpdate = hmac.HMAC(HMACKey, hashes.SHA256(), backend = backend)
    tagUpdate.update(jsonObject['cipherAES'])
    #compare the udpated tag with the original tag(HMACKey)
    #try catch inserted or else invalid signature error
    try:    
        #compare the two tags
        tagUpdate.verify(jsonObject['tag'])
        AESDecryptCipher = Cipher(algorithms.AES(AESKey), modes.CBC(jsonObject['iv']), backend = backend)
        AESdecryptor = AESDecryptCipher.decryptor()
        #plaintext
        text = AESdecryptor.update(jsonObject['cipherAES']) + AESdecryptor.finalize()
        
        from cryptography.hazmat.primitives import padding
        unpadder = padding.PKCS7(128).unpadder()
        #recover the plaintext data
        data = unpadder.update(text)
        data += unpadder.finalize()
        return data
    except cryptography.exceptions.InvalidSignature:
        print("invalid tag")
#encrypt message

input = "Helloooooo"

encrypt = Encrypt(input, "/Users/Keith/Desktop/478Phase3/publickeyTest.pem")
decrypt = DecryptTest(encrypt, "/Users/Keith/Desktop/478Phase3/privatekeyTest.pem" )
print(decrypt)