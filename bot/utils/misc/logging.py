import logging

# Logger obyektini yaratish
logger = logging.getLogger(__name__)

# Konsolga log chiqarish formati
logging.basicConfig(
    level=logging.INFO,
    format="%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s"
)
