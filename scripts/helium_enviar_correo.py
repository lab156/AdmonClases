import helium as he
import os
from dotenv import load_dotenv

load_dotenv()


def enviar(driver, address, subject, content):
    # he.start_chrome('https://mail.unah.edu.hn/')
    he.set_driver(driver)
    he.click('Correo nuevo')
    he.write(address, into='Para')
    he.write(subject, into='Agregar')
    he.write(content, into='Escriba / ')
    he.click('Enviar')


def sign_in_w_2fa():
    driver = he.start_chrome('https://mail.unah.edu.hn/')
    he.click("Ingresar")
    he.write(os.getenv("SENDER_EMAIL"), into='Email,')
    he.click("Next")
    he.click("Work or")
    he.write(os.getenv("UNAHEMAILPASSW"), into='Password')
    he.click('Sign in')
    input('press enter after logging in ...')
    return driver


if __name__ == "__main__":
    driver = sign_in_w_2fa()
    enviar(driver,
           os.getenv("TEST_EMAIL"),
           'holis maciso',
           'holis holis')
