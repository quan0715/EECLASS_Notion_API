class Material:
    def __init__(self, title, id, url, course, material_type, views, update_time, deadline, announcer,
                 complete_condition, read_time, complete_check, content, video_view, video_url):
        self.title = title
        self.id = id
        self.url = url
        self.course = course
        self.material_type = material_type
        self.views = views
        self.update_time = update_time
        self.deadline = deadline
        self.announcer = announcer
        self.complete_condition = complete_condition
        self.read_time = read_time
        self.complete_check = complete_check
        self.content = content
        self.video_view = video_view
        self.video_url = video_url
