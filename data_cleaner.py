def clean_data(raw_data):
    for i in raw_data['transactions']:
        if '+' in i['indicators']:
            i['transaction_type'] = 'Credit'
        else:
            i['transaction_type'] = 'Debit'
    return raw_data
