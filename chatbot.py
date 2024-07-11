from hugchat import hugchat
from hugchat.login import Login


# noinspection PyMissingConstructor
class Chatbot(hugchat.ChatBot):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Chatbot, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def configure(username, password, model=6):
        if Chatbot._instance is None:
            raise Exception("Chatbot instance is not created yet.")
        sign = Login(username, password)
        cookies = sign.login(cookie_dir_path='./cookies/', save_cookies=True)
        hugchat.ChatBot.__init__(Chatbot._instance, cookies=cookies.get_dict())
        Chatbot._instance.switch_llm(model)

    def __init__(self):
        # Avoid reinitialization if instance already exists
        if not hasattr(self, '_initialized'):
            self._initialized = True
