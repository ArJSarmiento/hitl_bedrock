import json
import boto3


def handler(event, context):
    _ = context
    print(f'Received event: {event}')
    event_body = json.loads(event['body'])

    # Extract the human review response
    human_review_response = event_body.get('reviewAccept')
    task_token = event_body.get('taskToken')

    # Send the response back to the Step Function
    send_task_payload = {'reviewAccept': human_review_response}

    try:
        client = boto3.client('stepfunctions')
        client.send_task_success(taskToken=task_token, output=json.dumps(send_task_payload))
    except Exception as e:
        print(f'Error sending task success: {e}')
        return {'statusCode': 500, 'body': 'Error sending task'}

    # Send Emails
    return {'statusCode': 200, 'body': 'Task Token sent successfully'}
