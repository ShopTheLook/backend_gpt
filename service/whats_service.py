from repository.whats_repository import WhatsRepository


class WhatsService:
    def __init__(self):
        self.whats_repository = WhatsRepository()

    def send_msg(self, uid: str, msg: str):
        self.whats_repository.send_msg(uid, msg)
