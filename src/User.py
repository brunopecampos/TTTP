class User():
  def __init__(self, username):
    self.username = username
    self.is_playing = False

  def set_user_marker(self, marker):
    self.marker = marker

  def set_user_playing(self):
    self.is_playing = True

  def is_user_playing(self):
    return self.is_playing
