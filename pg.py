import streamlit_authenticator as stauth

def generateHashedPasswords(passwords : list) -> str:
    hasher = stauth.Hasher(passwords)
    #mimics method hash_list due to issue where it claims it doesn't have a list of passwords even though this is the exact code just replacing self with hasher
    return [hasher.hash(password) for password in hasher.passwords]

if __name__ == '__main__':
    passwords = []
    while True:
        password = input('Enter a password or leave blank to finish entering passwords:\n')
        if password == '':
            break
        passwords.append(password)
    print(generateHashedPasswords(passwords))