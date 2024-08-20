from django.core.validators import RegexValidator


ERROR_MESSAGE = "Incorrect card number entered. Please enter the card number correctly"

MASTER_CARD = '^(5[1-5][0-9]{14}|2(22[1-9][0-9]{12}|2[3-9][0-9]{13}|[3-6][0-9]{14}|7[0-1][0-9]{13}|720[0-9]{12}))$'
UNIONPAY_CARD = '^(62[0-9]{14,17})$'
VISA_CARD = '^4[0-9]{12}(?:[0-9]{3})?$'
VISAMASTER_CARD = '^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})$'
UZCARD = '^(8600)[0-9]{12}$'
HUMO_CARD = '^(9860)[0-9]{12}$'

HUMO_UZCARD = RegexValidator(regex='^(8600)|(9860)[0-9]{12}$')


CVV = RegexValidator(r'^\d{1,10}$')