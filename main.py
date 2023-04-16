import logging
import datetime
import os
import predict
import email_utils
import tqdm
import imaplib
import json

from datetime import datetime


now = datetime.now() # current date and time


date_time = now.strftime("%Y-%m-%d-%H-%M-%S")

os.makedirs("logs",exist_ok= True)

log_file = os.path.join("logs", date_time + ".txt")


logging.basicConfig(filename= log_file,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger().addHandler(console)


# set up logger 

with open("credentials.json") as f:
    credentials = json.load(f)


try:

    imap_server = imaplib.IMAP4_SSL(credentials["incoming_imap_server"],port= credentials["incoming_port"])
    imap_server.login(credentials["user_name"], credentials["password"])
    imap_server.select('INBOX')

except Exception as e:

    logging.error(f"Connecting to account: {e}")
    exit()


logging.info(f"Succesfully logged in to {credentials['user_name']}.")


try:

    email_uids = email_utils.get_all_email_udis(imap_server)

except Exception as e:

    logging.error(f"Retrieving email uids: {e}")

    imap_server.logout()
    exit()


try:

    with open("last_email_uid.txt","r") as f:

        last_uid = int(f.read())

    email_uids = [i for i in email_uids if int(i.decode("UTF-8")) > last_uid]

except Exception as e:

    logging.error(f"Filtering new email uids: {e}")

    imap_server.logout()
    exit()


logging.info(f"Found {len(email_uids)} new emails in inbox. Now starting to move them in right folders.")



succesfully_moved_uids = []


if email_uids:

    for email_id in tqdm.tqdm(email_uids):

        email_uid_decoded = email_id.decode("UTF-8")

        try: 
        
            email_message = email_utils.fetch_and_process_email(imap_server,email_id)

        except Exception as e:

            logging.error("Failed to fetch and process email {email_uid_decoded}: {e}")
            
            continue


        try: 
            mail_text = email_utils.get_text_wrapper(email_message)
        except email_utils.InvalidContentTypeError:

            logging.error("Failed to read text of email {email_uid_decoded}. Probably just empty: {e}")
            
            continue

        except: 
            logging.error("Failed to read text of email {email_uid_decoded}: {e}")

            continue


        try:

            subject = email_utils.get_subject(email_message)
            
            query = subject + '\n' +  mail_text


            prediction = predict.get_email_predictions([query])[0]

            if prediction == "Important":
                logging.debug(f"Email {email_uid_decoded} was identified to be important. Will not be moved.")

                succesfully_moved_uids.append(email_uid_decoded)
                continue

            target_mailbox = f"Inbox.{prediction}"

        except: 

            logging.error("Failed to collect prediction of email {email_uid_decoded}: {e}")

            continue


        try:

            result = imap_server.uid('COPY', email_uid_decoded, target_mailbox)


            if result[0] == 'OK':
                    # Mark the original email as deleted
                    status = imap_server.uid('STORE', email_id, '+FLAGS', '(\Deleted)')

                    logging.debug(f"Succesfully moved email {email_uid_decoded} to {target_mailbox}.")

                    if status[0] != 'OK':

                        logging.error(f"fDeleting email {email_uid_decoded} failed after copying it. {status}")

                    
                    else:
                        succesfully_moved_uids.append(email_uid_decoded)

            else:
                
                logging.error(f"Moving of {email_uid_decoded} to {target_mailbox} failed: {result[0]}")

        except Exception as e:


            logging.error(f"Moving of {email_uid_decoded} to {target_mailbox} failed: {e}")


else:

    logging.info('No new emails found. Logging out now.')

# Loggint Out

try:


    imap_server.expunge()
    imap_server.close()
    status,_=    imap_server.logout()

    logging.info(f"Log Out Status: {status}")
    assert status == 'BYE', "Logging out did not work"



except Exception as e:

    logging.error(f"Logging out did not work: {e}")


try:

    # print new best uid

    new_highest_uid = max(list(map(int,succesfully_moved_uids)))

    with open("last_email_uid.txt","w") as f:

        f.write(str(new_highest_uid))

    logging.info(f"New Highest Email UID: {new_highest_uid}")

except Exception as e:

    logging.error(f"Failed to write new hight uid: {e}")