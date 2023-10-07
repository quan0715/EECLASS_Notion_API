class newly():
    def __init__(self) -> None:
        self.newly_update = []
        self.newly_upload = []
    def extend_newly_update(self, update_list: list) -> None:
        self.newly_update.extend(update_list)
    def extend_newly_upload(self, upload_list: list) -> None:
        self.newly_upload.extend(upload_list)
    def get_newly_update(self) -> list:
        return self.newly_update
    def get_newly_upload(self) -> list:
        return self.newly_upload