def testFunc(self):
    if not self.get_cookie("username"):
        return "False"
    return "True"