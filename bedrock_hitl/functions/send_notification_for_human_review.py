def handler(event, context):
    _ = context
    print(f'Received event: {event}')
    # Send Emails
    return {'statusCode': 200, 'body': 'Task Token sent successfully'}
