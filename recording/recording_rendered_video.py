def OnRec(app):
    """
    Args:
        type: MyApp(ShowBase) """
    app.movie(namePrefix = 'movie', duration = 1.0, fps = 30,
              format = 'png', sd = 4, source = None)


# # call with:
# self.accept("r", self.OnRec)
