import check_in
import logging

from qna3.common import qna3_util

logging.basicConfig(level=logging.DEBUG)

private_keys = qna3_util.parse_key_file("checkin_private_keys.txt")

for private_key in private_keys:
    logging.info(f"executing check in private key: '{private_key}'")
    (address, tx_hash_id, new_private_key) = check_in.do_check_in(private_key)
    logging.info("==================================== CHECK IN SUCCESS ===============================================")
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info(f'CHECK IN SUCCESSFUL, ADDRESS: {address}, PRIVATE_KEY: {private_key}, TX_HASH_ID: {tx_hash_id}')
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info("==================================== CHECK IN SUCCESS ===============================================")

logging.info(" ALL EXEC SUCCESSFUL !")
