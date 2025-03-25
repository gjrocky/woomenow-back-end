import threading
import traceback

import requests
from django.conf import settings
from user_agents import parse

_request_local = threading.local()
MAX_MESSAGE_LENGTH = 1996


def truncate_message(message):
    error_list = message.split('\n')
    msg = '===============================================\n```'
    msg_list = []
    for index, m in enumerate(error_list):
        msg = msg + m + '\n'
        if index < len(error_list) - 1 and len(msg + error_list[index + 1]) > MAX_MESSAGE_LENGTH:
            msg = msg + '```'
            msg_list.append(msg)
            msg = '```'
    if len(msg) and msg != '```':
        msg = msg + '```'
        msg_list.append(msg)
    return msg_list


def send_message_to_discord(webhook_url, message):
    headers = {
        'Content-Type': 'application/json'
    }
    requests.post(webhook_url, json={"content": message}, headers=headers)


class RequestMiddleware:
    """Middleware to store request in thread-local storage."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _request_local.request = request  # Store request
        response = self.get_response(request)
        return response

    @staticmethod
    def get_request():
        return getattr(_request_local, "request", None)


class DiscordErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0].strip()
        else:
            client_ip = request.META.get('REMOTE_ADDR')
        return client_ip

    def process_exception(self, request, exception):
        webhook_url = settings.DISCORD_WEBHOOK_URL
        if webhook_url:
            # Prepare detailed error message
            exc_type = type(exception).__name__
            exc_value = str(exception)

            user_agent_string = request.META.get('HTTP_USER_AGENT', '')
            tb = traceback.TracebackException.from_exception(exception)
            tb_str = ''.join(tb.format())
            user_agent = parse(user_agent_string)

            client_ip = f"Client IP : {self.get_client_ip(request)} \n"
            url = f"URL : {request.path} \n"
            device = f"Device : {user_agent.device.family} \n"
            client_os = f"Client os : {user_agent.os.family} \n"
            browser = f"Browser : {user_agent.browser.family} \n"
            browser_version = f"Browser Version : {user_agent.browser.version_string} \n"
            server_name = f"Server Name : {request.META.get('SERVER_NAME')} \n"

            error_message = f"{client_ip}{url}{device}{client_os}{browser}{browser_version}{server_name}\n\n{tb_str}\n"

            truncated_messages = truncate_message(error_message)
            for truncated_message in truncated_messages:
                send_message_to_discord(webhook_url, truncated_message)
        return None
