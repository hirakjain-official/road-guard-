import os
import time
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv('VAPI_API_KEY', '')
VAPI_PHONE_NUMBER_ID = os.getenv('VAPI_PHONE_NUMBER_ID', '')
ALERT_RECIPIENT_NUMBER = os.getenv('ALERT_RECIPIENT_NUMBER', '')


class VapiClient:
    def __init__(self):
        self._last_call_time: float = 0.0
        self._cooldown: int = 60

    def set_cooldown(self, seconds: int):
        self._cooldown = seconds

    def cooldown_remaining(self) -> int:
        elapsed = time.time() - self._last_call_time
        remaining = self._cooldown - elapsed
        return max(0, int(remaining))

    def in_cooldown(self) -> bool:
        return self.cooldown_remaining() > 0

    def trigger_call(self, speed: float) -> str:
        """
        Returns call status: 'triggered' | 'cooldown' | 'no_key' | 'error'
        """
        if self.in_cooldown():
            return 'cooldown'

        if not VAPI_API_KEY or not VAPI_PHONE_NUMBER_ID or not ALERT_RECIPIENT_NUMBER:
            print('[Vapi] API keys not set — skipping call (set in backend/.env)')
            return 'no_key'

        payload = {
            'type': 'outboundPhoneCall',
            'phoneNumberId': VAPI_PHONE_NUMBER_ID,
            'customer': {'number': ALERT_RECIPIENT_NUMBER},
            'assistant': {
                'firstMessage': (
                    f'Alert from Road Guard. A vehicle has been detected speeding at '
                    f'{speed:.0f} kilometres per hour. This is above the permitted limit. '
                    f'Please slow down immediately.'
                ),
                'model': {
                    'provider': 'openai',
                    'model': 'gpt-3.5-turbo',
                    'messages': [
                        {
                            'role': 'system',
                            'content': (
                                'You are an automated traffic enforcement notification system. '
                                'Your job is to deliver speed alerts clearly and professionally. '
                                'Keep responses brief. End the call politely after delivering the alert.'
                            ),
                        }
                    ],
                },
                'voice': {'provider': '11labs', 'voiceId': 'paula'},
                'endCallMessage': 'Thank you. Please drive safely.',
                'endCallPhrases': ['goodbye', 'understood', 'thank you'],
            },
        }

        try:
            resp = requests.post(
                'https://api.vapi.ai/call',
                headers={'Authorization': f'Bearer {VAPI_API_KEY}'},
                json=payload,
                timeout=10,
            )
            if resp.status_code in (200, 201):
                self._last_call_time = time.time()
                print(f'[Vapi] Call triggered for {speed:.0f} km/h')
                return 'triggered'
            else:
                print(f'[Vapi] API error {resp.status_code}: {resp.text}')
                return 'error'
        except Exception as e:
            print(f'[Vapi] Request failed: {e}')
            return 'error'
