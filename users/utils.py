import os
import binascii
import asyncio
import time

from datetime import datetime, timedelta

from django.core.mail import EmailMultiAlternatives
from django.template import loader


class UserEmailManager(object):
    user = None

    @staticmethod
    def generate_activation_key():
        security_key = binascii.hexlify(os.urandom(20)).decode()
        security_key_expires = datetime.now() + timedelta(days=7)
        return security_key, security_key_expires

    @staticmethod
    def send_email(subject_template_name, email_template_name,
                   context, from_email, to_email, html_email_template_name=None):
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        try:
            email_response = email_message.send()
        except Exception:
            email_response = None

        return email_response


async def coroutine_sleep(number, time_to_sleep):
    print('coroutine_{0} is active on the event loop'.format(number))

    print('coroutine_{0} yielding control. Going to be blocked for {1} seconds'.format(number, time_to_sleep))
    await asyncio.sleep(time_to_sleep)

    print('coroutine_{0} resumed. coroutine_{0} exiting'.format(number))


async def coroutine_example():
    # get default event loop
    loop = asyncio.get_event_loop()
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)

    future1 = asyncio.ensure_future(coroutine_sleep(1, 4))
    # loop.run_until_complete(future1)
    future2 = asyncio.ensure_future(coroutine_sleep(2, 5))
    # loop.run_until_complete(future2)

    # print('future', future1)
    # await future1
    # print('future', future2)
    # await future2
    # print('future', future3)
    # await future3

    future3 = asyncio.gather(future1, future2)
    await future3
